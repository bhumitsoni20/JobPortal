import os

# Define Base Directory


class Config:
    # Security
    SECRET_KEY = 'aa151727806b1b9da89d9be583d4ae100518af5ab5173f82affa62100e850749'
    CSRF_ENABLED = True
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///jobportal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Upload Configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads/resumes')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB upload limit

    # Flask-Mail Configuration (Optional)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # Set in environment variables
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # Set in environment variables
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

# Ensure Upload Folder Exists
if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)
