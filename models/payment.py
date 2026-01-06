from datetime import datetime
from extensions import db


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.id'))
    provider = db.Column(db.String(50), default='razorpay')
    provider_order_id = db.Column(db.String(120))
    transaction_id = db.Column(db.String(120))
    amount = db.Column(db.Integer)  # in smallest currency unit (paise)
    currency = db.Column(db.String(10), default='INR')
    status = db.Column(db.String(30), default='created')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
