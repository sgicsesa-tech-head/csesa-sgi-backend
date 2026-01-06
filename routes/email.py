from flask import Blueprint, request, jsonify
from utils.jwt_helper import admin_required
from utils.mail_service import send_email


email_bp = Blueprint('email', __name__)


@email_bp.post('/send')
@admin_required
def send_mail():
    data = request.get_json(silent=True) or {}
    required = ['to', 'subject', 'body']
    if any(not data.get(k) for k in required):
        return jsonify({'msg': 'to, subject, body required'}), 400
    send_email(data['to'], data['subject'], data['body'], data.get('attachment'))
    return jsonify({'status': 'sent'})
