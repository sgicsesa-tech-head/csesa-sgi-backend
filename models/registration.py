from datetime import datetime
from extensions import db


class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    team_name = db.Column(db.String(120))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    status = db.Column(db.String(30), default='pending')  # pending/paid/cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
