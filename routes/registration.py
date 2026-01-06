from flask import Blueprint, request, jsonify
from extensions import db
from models.registration import Registration
from models.event import Event
from utils.jwt_helper import admin_required
from utils.mail_service import send_email


registration_bp = Blueprint('registration', __name__)


@registration_bp.post('/')
def create_registration():
    data = request.get_json(silent=True) or {}
    required = ['name', 'email', 'event_id']
    if any(not data.get(k) for k in required):
        return jsonify({'msg': 'name, email, event_id required'}), 400

    # ensure event exists
    if not Event.query.get(data['event_id']):
        return jsonify({'msg': 'Invalid event_id'}), 404

    reg = Registration(
        name=data['name'],
        email=data['email'],
        team_name=data.get('team_name'),
        event_id=data['event_id'],
    )
    db.session.add(reg)
    db.session.commit()

    # Optional: send confirmation email (ignore failures during dev)
    try:
        send_email(
            to=reg.email,
            subject='CSESA Registration Received',
            body=f'Thanks {reg.name}! Your registration ID is {reg.id}.',
        )
    except Exception:
        pass

    return jsonify({'id': reg.id, 'status': reg.status}), 201


@registration_bp.get('/')
@admin_required
def list_registrations():
    event_id = request.args.get('event_id', type=int)
    q = Registration.query
    if event_id:
        q = q.filter(Registration.event_id == event_id)
    regs = q.order_by(Registration.created_at.desc()).all()
    return jsonify([
        {
            'id': r.id,
            'name': r.name,
            'email': r.email,
            'team_name': r.team_name,
            'event_id': r.event_id,
            'status': r.status,
        }
        for r in regs
    ])
