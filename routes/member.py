from flask import Blueprint, request, jsonify
from extensions import db
from models.member import Member
from utils.jwt_helper import admin_required


member_bp = Blueprint('member', __name__)

ALLOWED_CATEGORIES = {"Development", "Association", "Faculty"}
ALLOWED_DIVISIONS = {"TECSE", "SECSE", "FECSE"}


@member_bp.get('/')
def list_members():
    category = request.args.get('category')  # Development|Association|Faculty (legacy)
    year = request.args.get('year')  # e.g., 2025-26
    q = Member.query
    if category:
        q = q.filter(Member.category == category)
    if year:
        q = q.filter(Member.year == year)
    members = q.order_by((Member.display_order.asc().nulls_last()), Member.created_at.asc()).all()
    return jsonify([_serialize_member(m) for m in members])


@member_bp.get('/categories')
def categories():
    return jsonify(sorted(list(ALLOWED_CATEGORIES)))


@member_bp.get('/by-year')
def members_by_year():
    """Return data grouped by year, matching frontend schema."""
    result = {}
    for m in Member.query.order_by(Member.year.asc(), Member.display_order.asc().nulls_last()).all():
        yr = m.year or 'Unknown'
        result.setdefault(yr, []).append(_serialize_member(m))
    return jsonify(result)


@member_bp.get('/years')
def list_years():
    years = sorted({m.year for m in Member.query.all() if m.year})
    return jsonify(years)


@member_bp.post('/')
@admin_required
def create_member():
    data = request.get_json(silent=True) or {}
    required = ['name', 'role', 'division', 'year']
    if any(not data.get(k) for k in required):
        return jsonify({'msg': f'required fields: {", ".join(required)}'}), 400
    if data['division'] not in ALLOWED_DIVISIONS:
        return jsonify({'msg': 'invalid division', 'allowed': sorted(list(ALLOWED_DIVISIONS))}), 400
    # category stays optional for legacy filters
    if data.get('category') and data['category'] not in ALLOWED_CATEGORIES:
        return jsonify({'msg': 'invalid category', 'allowed': sorted(list(ALLOWED_CATEGORIES))}), 400
    m = Member(
        name=data.get('name'),
        photo_url=data.get('photo_url'),
        social1=data.get('social1'),
        social2=data.get('social2'),
        category=data.get('category'),
        role=data.get('role'),
        division=data.get('division'),
        display_order=data.get('order'),
        year=data.get('year'),
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({'id': m.id}), 201


@member_bp.put('/<int:member_id>')
@admin_required
def update_member(member_id: int):
    m = Member.query.get(member_id)
    if not m:
        return jsonify({'msg': 'member not found'}), 404
    data = request.get_json(silent=True) or {}
    if 'name' in data:
        m.name = data['name']
    if 'photo_url' in data:
        m.photo_url = data['photo_url']
    if 'social1' in data:
        m.social1 = data['social1']
    if 'social2' in data:
        m.social2 = data['social2']
    if 'category' in data:
        if data['category'] not in ALLOWED_CATEGORIES:
            return jsonify({'msg': 'invalid category', 'allowed': sorted(list(ALLOWED_CATEGORIES))}), 400
        m.category = data['category']
    if 'role' in data:
        m.role = data['role']
    if 'division' in data:
        if data['division'] not in ALLOWED_DIVISIONS:
            return jsonify({'msg': 'invalid division', 'allowed': sorted(list(ALLOWED_DIVISIONS))}), 400
        m.division = data['division']
    if 'order' in data:
        m.display_order = data['order']
    if 'year' in data:
        m.year = data['year']
    db.session.commit()
    return jsonify({'id': m.id})


@member_bp.delete('/<int:member_id>')
@admin_required
def delete_member(member_id: int):
    m = Member.query.get(member_id)
    if not m:
        return jsonify({'msg': 'member not found'}), 404
    db.session.delete(m)
    db.session.commit()
    return jsonify({'status': 'deleted'})


def _serialize_member(m: Member):
    # Match frontend schema field names
    return {
        'id': m.id,
        'name': m.name,
        'role': m.role,
        'image': m.photo_url or '/api/placeholder/200/240',
        'order': m.display_order,
        'division': m.division,
    }


@member_bp.post('/bulk')
@admin_required
def bulk_import():
    """Bulk import members in the frontend format.

    Accepted payloads:
    1) Mapping format (recommended):
       { "2025-26": [ { name, role, image, order, division }, ... ], "2024-25": [ ... ] }
       Or wrapped as { "data": { ... }, "mode": "replace|append" }

    2) Flat format (as in your screenshot):
       { "year": "2025-26", "division": "Development Team", "members": [ { name, role, image, order } ] }
       Division can be provided at the top-level or per item.

    Default mode is 'replace': existing members for a year are deleted before insert.
    """
    payload = request.get_json(silent=True) or {}
    mode = (payload.get('mode') or 'replace').lower()

    # Normalize to mapping format
    mapping = payload.get('data')
    if not mapping:
        if 'members' in payload and ('year' in payload or 'years' in payload):
            yr = payload.get('year') or 'Unknown'
            default_div = payload.get('division')
            items = payload.get('members') or []
            # Ensure each item has a division (fallback to top-level division)
            norm_items = []
            for it in items:
                it = dict(it)
                if 'division' not in it and default_div:
                    it['division'] = default_div
                norm_items.append(it)
            mapping = {yr: norm_items}
        else:
            # Assume raw mapping
            mapping = payload

    if not isinstance(mapping, dict):
        return jsonify({'msg': 'invalid payload: expected year → members mapping'}), 400

    inserted = 0
    years_touched = []
    for year, items in mapping.items():
        if not isinstance(items, list):
            return jsonify({'msg': f'year {year} must map to a list'}), 400
        years_touched.append(year)
        if mode == 'replace':
            # Avoid SQLAlchemy query.delete() binding issues; delete row-by-row
            for old in Member.query.filter(Member.year == year).all():
                db.session.delete(old)

        for it in items:
            name = it.get('name')
            role = it.get('role')
            division = it.get('division')  # optional in bulk import
            if not name or not role:
                # Skip invalid row
                continue
            m = Member(
                name=name,
                role=role,
                division=division,
                display_order=it.get('order'),
                year=year,
                photo_url=it.get('image') or '/api/placeholder/200/240',
            )
            db.session.add(m)
            inserted += 1

    db.session.commit()
    return jsonify({'mode': mode, 'years': years_touched, 'inserted': inserted})
