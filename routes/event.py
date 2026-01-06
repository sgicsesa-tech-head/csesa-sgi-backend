from datetime import datetime
from flask import Blueprint, request, jsonify
from extensions import db
from models.event import Event
from utils.jwt_helper import admin_required


event_bp = Blueprint('event', __name__)


@event_bp.get('/')
def list_events():
    status = request.args.get('status')  # past|upcoming|all
    q = Event.query.filter_by(is_published=True)
    now = datetime.utcnow()
    if status == 'upcoming':
        q = q.filter((Event.start_at == None) | (Event.start_at >= now))  # noqa: E711
    elif status == 'past':
        q = q.filter((Event.end_at != None) & (Event.end_at < now))  # noqa: E711
    events = q.order_by(Event.start_at.asc().nulls_last()).all()
    return jsonify([_serialize_event(e) for e in events])


@event_bp.post('/')
@admin_required
def create_event():
    data = request.get_json(silent=True) or {}
    e = Event(
        title=data.get('title'),
        subtitle=data.get('subtitle'),
        description=data.get('description'),
        image_url=data.get('image_url'),
        venue=data.get('venue'),
        rulebook_url=data.get('rulebook_url'),
        start_at=_parse_dt(data.get('start_at')),
        end_at=_parse_dt(data.get('end_at')),
        is_published=bool(data.get('is_published', True)),
    )
    db.session.add(e)
    db.session.commit()
    return jsonify(_serialize_event(e)), 201


def _parse_dt(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _serialize_event(e: Event):
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
    }
