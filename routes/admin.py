import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from extensions import db
from models.admin import Admin
from config import Config


admin_bp = Blueprint('admin', __name__)


@admin_bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'msg': 'Email and password required'}), 400

    # 1) Check env-configured admin
    env_email = Config.ADMIN_EMAIL
    env_hash = Config.ADMIN_PASSWORD_HASH
    env_plain = Config.ADMIN_PASSWORD

    valid = False
    if email == env_email:
        if env_hash:
            valid = check_password_hash(env_hash, password)
        elif env_plain:
            valid = env_plain == password

    # 2) Or fallback to DB-stored admin (optional)
    if not valid:
        user = Admin.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            valid = True

    if not valid:
        return jsonify({'msg': 'Invalid credentials'}), 401

    token = create_access_token(identity=email, additional_claims={'is_admin': True})
    return jsonify({'access_token': token})


@admin_bp.get('/me')
def me():
    return jsonify({'service': 'CSESA Admin API'})
