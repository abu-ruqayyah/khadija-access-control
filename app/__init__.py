import os
from flask import Flask, jsonify, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import Config
from app.models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

csrf = CSRFProtect()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["300 per day", "100 per hour"],
    storage_uri="memory://"
)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['LAB_EVIDENCE_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data:;"
        )
        return response

    @app.route('/health')
    def health_check():
        return jsonify({"status": "ok", "app": "Khadija Bukar Access Control Audit", "student": "Khadija Bukar", "fellow_id": "FE/26/4554984566"}), 200

    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.main.routes import main_bp
    from app.blueprints.audit.routes import audit_bp
    from app.blueprints.reports.routes import reports_bp
    from app.blueprints.lab.routes import lab_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(lab_bp)

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app
