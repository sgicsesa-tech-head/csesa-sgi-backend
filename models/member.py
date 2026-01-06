from datetime import datetime
from extensions import db


class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    photo_url = db.Column(db.String(500))
    social1 = db.Column(db.String(200))
    social2 = db.Column(db.String(200))
    # Legacy category kept for compatibility
    category = db.Column(db.String(50))  # Development, Association, Faculty
    # New fields to match frontend schema
    role = db.Column(db.String(100))
    division = db.Column(db.String(20))  # TECSE | SECSE | FECSE
    display_order = db.Column(db.Integer)
    year = db.Column(db.String(9))  # e.g., "2025-26"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
