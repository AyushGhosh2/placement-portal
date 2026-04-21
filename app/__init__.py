from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# These are created here but initialized later (so no circular imports)
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Secret key for sessions (change this to anything random in production)
    app.config['SECRET_KEY'] = 'placement_portal_secret_2024'

    # SQLite database file will be created as placement.db in the app folder
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Folder where student resumes will be uploaded
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'

    # Attach db and login manager to the app
    db.init_app(app)
    login_manager.init_app(app)

    # Where to redirect if user tries to access a page without logging in
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    # Register all blueprints (groups of routes)
    from app.auth import auth
    from app.admin import admin
    from app.company import company
    from app.student import student

    app.register_blueprint(auth)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(company, url_prefix='/company')
    app.register_blueprint(student, url_prefix='/student')

    # Create all tables and the default admin user
    with app.app_context():
        from app import models
        db.create_all()
        models.create_default_admin()

    return app