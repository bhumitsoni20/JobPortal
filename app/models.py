from app.extension import db, login_manager
from flask_login import UserMixin
from datetime import datetime

# Load User for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='seeker')  # Can be 'seeker', 'employer', or 'admin'
    company = db.Column(db.String(100), nullable=True )
    # Employer relationship
    jobs_posted = db.relationship('Job', back_populates='employer', lazy=True)

    # Seeker relationship
    applications = db.relationship('JobApplication', back_populates='applicant', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    salary = db.Column(db.Float, nullable=True)  # Changed to Float for easier arithmetic
    location = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(100), nullable=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    employer = db.relationship('User', back_populates='jobs_posted')
    company = db.Column(db.String(100), nullable=False)
    applications = db.relationship('JobApplication', back_populates='job', lazy=True, cascade="all, delete-orphan")

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cover_letter = db.Column(db.Text, nullable=False)
    date_applied = db.Column(db.DateTime, default=datetime.utcnow)
    resume = db.Column(db.String(255), default=None)  # Explicitly defaulting to None

    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    job = db.relationship('Job', back_populates='applications')
    applicant = db.relationship('User', back_populates='applications')

# Optional: Keeping Admin as a separate model
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
