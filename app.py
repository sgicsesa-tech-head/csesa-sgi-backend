import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import db, migrate, jwt


def create_app():
    """Application factory for the CSESA backend."""
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Import models so Alembic discovers them
    from models import admin, blog, event, member, payment, registration  # noqa: F401

    # Blueprints
    from routes.admin import admin_bp
    from routes.event import event_bp
    from routes.blog import blog_bp
    from routes.member import member_bp
    from routes.registration import registration_bp
    from routes.payment import payment_bp
    from routes.email import email_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(event_bp, url_prefix='/events')
    app.register_blueprint(blog_bp, url_prefix='/blogs')
    app.register_blueprint(member_bp, url_prefix='/members')
    app.register_blueprint(registration_bp, url_prefix='/registration')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(email_bp, url_prefix='/email')

    @app.get('/health')
    def health():
        return {'status': 'ok'}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
