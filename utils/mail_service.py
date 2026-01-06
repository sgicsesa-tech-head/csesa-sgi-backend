import mimetypes
import os
import smtplib
from email.message import EmailMessage
from typing import Optional
from flask import current_app


def send_email(to: str, subject: str, body: str, attachment_path: Optional[str] = None):
    """Send an email via simple SMTP using env creds.

    Expects MAIL_EMAIL and MAIL_PASSWORD in config. Uses Gmail SMTP if
    address ends with @gmail.com; otherwise tries STARTTLS on port 587.
    """
    sender = current_app.config.get('MAIL_EMAIL')
    password = current_app.config.get('MAIL_PASSWORD')
    if not sender or not password:
        raise RuntimeError('MAIL_EMAIL/MAIL_PASSWORD not configured')

    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)

    if attachment_path:
        path = os.path.abspath(attachment_path)
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(path, 'rb') as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(path))

    # Basic SMTP
    host = 'smtp.gmail.com' if sender.endswith('@gmail.com') else 'smtp.office365.com'
    port = 587
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
    return True
