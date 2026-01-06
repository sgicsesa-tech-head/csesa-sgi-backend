from flask import Blueprint, request, jsonify
from app import db
from models.blog import Blog
from utils.jwt_helper import admin_required


blog_bp = Blueprint('blog', __name__)


@blog_bp.get('/')
def list_blogs():
    tag = request.args.get('tag')  # Tech|Other
    q = Blog.query
    if tag:
        q = q.filter(Blog.tag == tag)
    posts = q.order_by(Blog.created_at.desc()).all()
    return jsonify([
        {
            'id': b.id,
            'image_url': b.image_url,
            'title': b.title,
            'description': b.description,
            'tag': b.tag,
            'created_at': b.created_at.isoformat(),
        }
        for b in posts
    ])


@blog_bp.post('/')
@admin_required
def create_blog():
    data = request.get_json(silent=True) or {}
    b = Blog(
        image_url=data.get('image_url'),
        title=data.get('title'),
        description=data.get('description'),
        tag=data.get('tag'),
    )
    db.session.add(b)
    db.session.commit()
    return jsonify({'id': b.id}), 201
