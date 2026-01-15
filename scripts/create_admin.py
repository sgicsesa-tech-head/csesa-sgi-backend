# One-off script to create an admin user in the database for local testing.
# Usage (from project root):
#   py -3 scripts/create_admin.py --email admin@csesa.in --password admin123

import sys
import os
import argparse
from werkzeug.security import generate_password_hash

# Ensure project root is on sys.path so imports work when running script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from extensions import db
from app import create_app
from models.admin import Admin

parser = argparse.ArgumentParser()
parser.add_argument('--email', required=True)
parser.add_argument('--password', required=True)
args = parser.parse_args()

app = create_app()
with app.app_context():
    db.create_all()
    email = args.email
    pwd = args.password
    existing = Admin.query.filter_by(email=email).first()
    if existing:
        print('Admin already exists:', email)
        sys.exit(0)
    h = generate_password_hash(pwd)
    a = Admin(email=email, password_hash=h)
    db.session.add(a)
    db.session.commit()
    print('Created admin:', email)
