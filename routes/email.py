from flask import Blueprint, request, jsonify
from utils.jwt_helper import admin_required
from utils.mail_service import send_email
from flask import current_app

email_bp = Blueprint('email', __name__)


# Public info route

@email_bp.get('/')
def info():
    return jsonify({'service': 'Email Service', 'note': 'Use admin endpoint to send emails', 'endpoint': '/admin/email/send', 'method': 'POST', 'required_fields': ['mailTo', 'subject', 'body'], 'optional_fields': ['attachment']}), 200

def admin_send_email_handler(data: dict):
    """Handle admin email send request in dry-run mode.

    Returns (response, status_code).
    """
    data = data or {}
    # case-insensitive keys
    lowered = {k.lower(): v for k, v in data.items()}

    # prefer explicit 'mailTo' per client spec, accept 'to' as well
    recipients = data.get('mailTo') or data.get('to') or lowered.get('mailto') or lowered.get('to')
    subject = data.get('subject') or lowered.get('subject')
    body = data.get('body') or lowered.get('body')
    attachment = data.get('attachment') if 'attachment' in data else lowered.get('attachment')

    # validate required fields
    if not recipients or not subject or not body:
        return jsonify({'msg': 'mailTo, subject, body required'}), 400

    # normalize recipients: allow comma-separated string or list
    if isinstance(recipients, str):
        if ',' in recipients:
            recipients = [r.strip() for r in recipients.split(',') if r.strip()]
        else:
            recipients = recipients.strip()

    # Dry-run: do not send, just return the prepared payload
    preview = {
        'status': 'dry-run',
        'sent': False,
        'to': recipients,
        'subject': subject,
        'body': body,
        'attachment': attachment,
    }
    return jsonify(preview), 200



# Admin: Send Email
# Note: admin send is handled under /admin/email/send by the admin blueprint
