from datetime import datetime
from extensions import db


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(300))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    venue = db.Column(db.String(200))
    rulebook_url = db.Column(db.String(500))
    start_at = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='event', lazy=True)
