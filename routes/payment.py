import hmac
import json
from hashlib import sha256
from flask import Blueprint, request, jsonify, current_app
from extensions import db
from models.payment import Payment
from models.registration import Registration
from utils.jwt_helper import admin_required

try:
    import razorpay
except Exception:  # pragma: no cover - package may not be installed yet
    razorpay = None


payment_bp = Blueprint('payment', __name__)


@payment_bp.post('/create-order')
def create_order():
    data = request.get_json(silent=True) or {}
    amount = int(data.get('amount', 0))
    registration_id = data.get('registration_id')
    if amount <= 0:
        return jsonify({'msg': 'amount must be > 0 (in paise)'}), 400

    if registration_id and not Registration.query.get(registration_id):
        return jsonify({'msg': 'Invalid registration_id'}), 404

    key_id = current_app.config.get('RAZORPAY_KEY_ID')
    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
    if not key_id or not key_secret:
        return jsonify({'msg': 'Razorpay keys not configured'}), 500

    client = razorpay.Client(auth=(key_id, key_secret)) if razorpay else None
    if client is None:
        return jsonify({'msg': 'razorpay client not available'}), 500

    order = client.order.create({'amount': amount, 'currency': 'INR'})

    pay = Payment(
        registration_id=registration_id,
        provider_order_id=order['id'],
        amount=amount,
        status='created',
    )
    db.session.add(pay)
    db.session.commit()

    return jsonify({'order_id': order['id'], 'key_id': key_id})


@payment_bp.post('/verify')
def verify_payment():
    data = request.get_json(silent=True) or {}
    order_id = data.get('razorpay_order_id')
    payment_id = data.get('razorpay_payment_id')
    signature = data.get('razorpay_signature')
    if not order_id or not payment_id or not signature:
        return jsonify({'msg': 'Missing verification fields'}), 400

    key_secret = current_app.config.get('RAZORPAY_KEY_SECRET')
    payload = f"{order_id}|{payment_id}".encode()
    expected = hmac.new(key_secret.encode(), payload, sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return jsonify({'msg': 'Invalid signature'}), 400

    pay = Payment.query.filter_by(provider_order_id=order_id).first()
    if not pay:
        return jsonify({'msg': 'Order not found'}), 404
    pay.transaction_id = payment_id
    pay.status = 'paid'
    db.session.commit()
    # Optionally update registration status
    if pay.registration_id:
        reg = Registration.query.get(pay.registration_id)
        if reg:
            reg.status = 'paid'
            db.session.commit()

    return jsonify({'status': 'verified'})


@payment_bp.get('/')
@admin_required
def list_payments():
    pays = Payment.query.order_by(Payment.created_at.desc()).all()
    return jsonify([
        {
            'id': p.id,
            'registration_id': p.registration_id,
            'order_id': p.provider_order_id,
            'transaction_id': p.transaction_id,
            'amount': p.amount,
            'currency': p.currency,
            'status': p.status,
        }
        for p in pays
    ])
