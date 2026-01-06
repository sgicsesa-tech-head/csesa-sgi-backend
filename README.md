# CSESA Backend (Flask)

A minimal API for CSESA with Admin auth (JWT), Events, Blogs, Members, Registrations, Payments (Razorpay test), and Email service.

## Quick Start (Windows, PowerShell)

```powershell
# 1) Create venv
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# 2) Install deps
pip install -r requirements.txt

# 3) Configure env
copy .env.example .env
# Edit .env with your values (admin, mail, razorpay)

# 4) Initialize DB (SQLite by default)
$env:FLASK_APP="app:create_app"
flask db init; flask db migrate -m "init"; flask db upgrade

# 5) Run
python app.py
```

Base URL: http://localhost:5000

## Endpoints Overview

- Auth
  - POST /admin/login → { access_token }
- Events
  - GET /events?status=upcoming|past|all
  - POST /events (admin)
- Blogs
  - GET /blogs?tag=Tech|Other
  - POST /blogs (admin)
- Members
  - GET /members?category=Development|Association|Faculty&year=2025-26
  - GET /members/categories → ["Development","Association","Faculty","Faculty Advisors"]
  - GET /members/years → ["2024-25","2025-26", ...]
  - GET /members/by-year → { "2025-26": [{ id, name, role, image, order, division }] }
  - POST /members (admin)
  - POST /members/bulk (admin)
    - Body example (replace mode):
      {
        "mode": "replace",
        "data": {
          "2025-26": [
            { "name": "Test President", "role": "President", "image": "/api/placeholder/200/240", "order": 1, "division": "TECSE" }
          ]
        }
      }
- Registration
  - POST /registration → create registration (public)
  - GET /registration?event_id= (admin)
- Payments (Razorpay test mode)
  - POST /payment/create-order → { order_id, key_id }
  - POST /payment/verify → { status: 'verified' }
- Email
  - POST /email/send (admin)

Send JWT in protected requests:

Authorization: Bearer <token>

## Frontend Integration
- Frontend calls these JSON APIs using the base URL above.
- CORS is enabled for all origins by default; restrict in production.
- For Razorpay, frontend collects payment using key_id and order_id, then POSTs razorpay_order_id, razorpay_payment_id, and razorpay_signature to /payment/verify.
 - Members UI can use GET /members/by-year to render grouped sections by academic year.
 - Use GET /members/years for quick filter options; reads are public, writes require Admin JWT.

## Notes
- Default DB is SQLite (csesa.db). Set DATABASE_URL in .env for MySQL/Postgres.
- Prefer ADMIN_PASSWORD_HASH over plaintext. Generate with:
  python -c "from werkzeug.security import generate_password_hash as g; print(g('yourpass'))"
- Mail uses basic SMTP with TLS (Gmail/Office). Use app passwords where required.

## Development
- New models/fields → flask db migrate then flask db upgrade.
- Run GET /health to check service status.
 - Postman collection: see postman/CSESA_Backend.postman_collection.json

## Collaboration
- Branching: use feature branches (e.g., feature/members-ui, fix/events-filter).
- Pull Requests: open PRs to main; require at least one approval.
- Commits: follow conventional commits (feat:, fix:, docs:, chore:).
- Issues: file bugs and features with clear steps and expected results.
- Secrets: never commit .env; use .env.example and GitHub repo secrets for CI.
