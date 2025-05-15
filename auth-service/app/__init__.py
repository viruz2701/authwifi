import os
from datetime import timedelta
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import logging
from logging.handlers import RotatingFileHandler
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Sentry initialization
if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
cache = Cache(config={'CACHE_TYPE': 'RedisCache' if os.getenv('REDIS_URL') else 'SimpleCache'})

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.ProductionConfig' if os.getenv('FLASK_ENV') == 'production' else 'config.DevelopmentConfig')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    configure_logging(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_commands(app)
    
    return app

def configure_logging(app):
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
        handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=1024*1024,
            backupCount=5
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(handler)

def register_blueprints(app):
    from app.auth import auth_bp
    from app.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify(status='ok', time=datetime.utcnow().isoformat())

def register_error_handlers(app):
    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify(error=str(e)), 400
    
    @app.errorhandler(500)
    def handle_server_error(e):
        app.logger.error(f'Server error: {str(e)}')
        return jsonify(error='Internal server error'), 500

def register_commands(app):
    @app.cli.command('create-admin')
    def create_admin():
        """Create admin user"""
        from app.models import AdminUser
        admin = AdminUser(
            username=os.getenv('ADMIN_USERNAME'),
            password=os.getenv('ADMIN_PASSWORD')
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created')

from app import models