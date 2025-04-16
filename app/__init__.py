from flask import Flask
from app.extension import db, login_manager, bcrypt
from config import Config
from flask_wtf.csrf import CSRFProtect

csrf= CSRFProtect()
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  
    
    csrf.init_app(app)  
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    from app.routes import main
    from app.admin_routes import admin_bp, resume_bp

    login_manager.login_view = "main.login"
    login_manager.login_message_category = "info"

    app.register_blueprint(main)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(resume_bp, url_prefix='/resumes')

    return app
