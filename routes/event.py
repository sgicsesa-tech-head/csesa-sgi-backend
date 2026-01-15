from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from extensions import db
from models.event import Event


event_bp = Blueprint('event', __name__)


@event_bp.get('/')
def list_events():
    """List events. Query param `status` can be `upcoming`, `past`, or `all`.

    Returns published events by default.
    """
    status = request.args.get('status')  # upcoming|past|all
    q = Event.query.filter_by(is_published=True)
    now = datetime.utcnow()
    if status == 'upcoming':
        # include events without start_at (treat as upcoming)
        q = q.filter((Event.start_at == None) | (Event.start_at >= now))  # noqa: E711
        q = q.order_by(Event.start_at.asc().nulls_last())
    elif status == 'past':
        q = q.filter((Event.end_at != None) & (Event.end_at < now))  # noqa: E711
        q = q.order_by(Event.end_at.desc().nulls_last())
    else:
        q = q.order_by(Event.start_at.asc().nulls_last())

    events = q.all()
    return jsonify([serialize_event(e) for e in events]), 200


# Note: write operations for events are handled under /admin/events


@event_bp.get('/<int:event_id>')
def get_event(event_id: int):
    """Return a single published event by ID or 404 if not found/unpublished."""
    include_unpublished = str(request.args.get('include_unpublished', '')).lower() in ('1', 'true', 'yes')

    if include_unpublished:
        # require admin JWT when requesting unpublished events
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({'msg': 'Missing or invalid token'}), 401
        claims = get_jwt() or {}
        if not claims.get('is_admin'):
            return jsonify({'msg': 'Admins only'}), 403

    e = Event.query.get(event_id)
    # if not found at all, return 404
    if not e:
        return jsonify({'msg': 'Event not found'}), 404
    # if not including unpublished, only allow published events
    if not include_unpublished and not e.is_published:
        return jsonify({'msg': 'Event not found'}), 404

    return jsonify(serialize_event(e)), 200


def parse_dt(s: str):
    if not s:
        return None
    try:
        # fromisoformat handles many ISO8601 forms; returns naive or aware datetime
        return datetime.fromisoformat(s)
    except Exception:
        return None


def serialize_event(e: Event):
    return {
        'id': e.id,
        'title': e.title,
        'subtitle': e.subtitle,
        'description': e.description,
        'image_url': e.image_url,
        'venue': e.venue,
        'rulebook_url': e.rulebook_url,
        'start_at': e.start_at.isoformat() if e.start_at else None,
        'end_at': e.end_at.isoformat() if e.end_at else None,
        'is_published': e.is_published,
        'created_at': e.created_at.isoformat() if e.created_at else None,
    }
