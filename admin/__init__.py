from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Измените на реальный секретный ключ
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    from .views import admin_bp
    from .auth import auth_bp
    
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    
    with app.app_context():
        db.create_all()
    
    return app 