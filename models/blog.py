from datetime import datetime
from extensions import db


class Blog(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    tag = db.Column(db.String(50))  # 'Tech' or 'Other'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
