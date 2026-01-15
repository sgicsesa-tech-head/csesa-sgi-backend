from flask import Blueprint, request, jsonify
from extensions import db
from models.blog import Blog


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
            'created_at': b.created_at.isoformat() if b.created_at else None,
        }
        for b in posts
    ]), 200
