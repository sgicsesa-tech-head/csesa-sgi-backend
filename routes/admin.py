from datetime import datetime

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from extensions import db
from config import Config
from models.admin import Admin
from models.event import Event
from models.blog import Blog
from utils.jwt_helper import admin_required
from utils.mail_service import send_email
from routes.email import admin_send_email_handler

admin_bp = Blueprint('admin', __name__)



# ADMIN AUTH

@admin_bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'msg': 'Email and password required'}), 400

    # ---- ENV ADMIN (primary) ----
    if email == Config.ADMIN_EMAIL:
        if Config.ADMIN_PASSWORD_HASH:
            if check_password_hash(Config.ADMIN_PASSWORD_HASH, password):
                token = create_access_token(
                    identity=email,
                    additional_claims={'is_admin': True}
                )
                return jsonify({'access_token': token}), 200
        elif Config.ADMIN_PASSWORD:
            if password == Config.ADMIN_PASSWORD:
                token = create_access_token(
                    identity=email,
                    additional_claims={'is_admin': True}
                )
                return jsonify({'access_token': token}), 200

    # ---- DB ADMIN (fallback) ----
    user = Admin.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        token = create_access_token(
            identity=email,
            additional_claims={'is_admin': True}
        )
        return jsonify({'access_token': token}), 200

    return jsonify({'msg': 'Invalid credentials'}), 401


@admin_bp.get('/me')
def me():
    return jsonify({'service': 'CSESA Admin API'}), 200


# EVENTS (ADMIN ONLY)

@admin_bp.post('/events')
@admin_required
def admin_create_event():
    data = request.get_json(silent=True) or {}

    if not data.get('title'):
        return jsonify({'msg': 'title is required'}), 400

    def parse_dt(value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None

    start_at = parse_dt(data.get('start_at'))
    end_at = parse_dt(data.get('end_at'))

    if data.get('start_at') and start_at is None:
        return jsonify({'msg': 'start_at must be ISO datetime'}), 400
    if data.get('end_at') and end_at is None:
        return jsonify({'msg': 'end_at must be ISO datetime'}), 400

    event = Event(
        title=data.get('title'),
        subtitle=data.get('subtitle'),
        description=data.get('description'),
        image_url=data.get('image_url'),
        venue=data.get('venue'),
        rulebook_url=data.get('rulebook_url'),
        start_at=start_at,
        end_at=end_at,
        is_published=bool(data.get('is_published', True)),
    )

    db.session.add(event)
    db.session.commit()
    return jsonify({'id': event.id}), 201


@admin_bp.put('/events/<int:event_id>')
@admin_required
def admin_update_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'msg': 'Event not found'}), 404

    data = request.get_json(silent=True) or {}

    for field in [
        'title', 'subtitle', 'description',
        'image_url', 'venue', 'rulebook_url'
    ]:
        if field in data:
            setattr(event, field, data.get(field))

    if 'is_published' in data:
        event.is_published = bool(data.get('is_published'))

    for field in ['start_at', 'end_at']:
        if field in data:
            try:
                setattr(
                    event,
                    field,
                    datetime.fromisoformat(data[field]) if data[field] else None
                )
            except Exception:
                return jsonify({'msg': f'{field} must be ISO datetime'}), 400

    db.session.commit()
    return jsonify({'msg': 'updated'}), 200


@admin_bp.delete('/events/<int:event_id>')
@admin_required
def admin_delete_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'msg': 'Event not found'}), 404

    db.session.delete(event)
    db.session.commit()
    return jsonify({'msg': 'deleted'}), 200


# BLOGS (ADMIN ONLY)

@admin_bp.post('/blogs')
@admin_required
def admin_create_blog():
    data = request.get_json(silent=True) or {}

    if not data.get('title'):
        return jsonify({'msg': 'title is required'}), 400

    blog = Blog(
        image_url=data.get('image_url'),
        title=data.get('title'),
        description=data.get('description'),
        tag=data.get('tag'),
    )

    db.session.add(blog)
    db.session.commit()
    return jsonify({'id': blog.id}), 201


@admin_bp.delete('/blogs/<int:blog_id>')
@admin_required
def admin_delete_blog(blog_id):
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({'msg': 'Blog not found'}), 404

    db.session.delete(blog)
    db.session.commit()
    return jsonify({'msg': 'deleted'}), 200



# EMAIL (ADMIN ONLY)

@admin_bp.post('/email/send')
@admin_required
def admin_send_email():
    data = request.get_json(silent=True) or {}
    # delegate to email handler (dry-run)
    return admin_send_email_handler(data)
