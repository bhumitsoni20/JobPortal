from flask import Blueprint, render_template, flash, redirect, url_for, send_file, abort, current_app, abort, request, send_from_directory
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename, safe_join
from app.extension import db
from app.models import User, Job, JobApplication
from app.forms import JobPostForm
import os
from flask_wtf.csrf import validate_csrf

# Define Blueprints
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')
resume_bp = Blueprint('resume_bp', __name__, url_prefix='/resumes')  # Ensure /resumes is accessible

# Use Flask's config instead of hardcoding paths
def get_upload_folder():
    return os.path.join(current_app.config['UPLOAD_FOLDER'])

# Ensure the upload directory exists but only within an app context
def create_upload_folder():
    with current_app.app_context():
        os.makedirs(get_upload_folder(), exist_ok=True)

# Admin-only access decorator
def admin_only(f):
    @wraps(f)
    @login_required
    def wrap(*args, **kwargs):
        if current_user.role != "admin":  # No need for another DB query
            flash("Access Denied! Admins only.", "danger")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return wrap

# Admin Dashboard
@admin_bp.route('/dashboard')
@admin_only
def admin_dashboard():
    print(f"Current user role: {current_user.role}")  # Debugging log
    
    jobs = Job.query.all()
    applications = JobApplication.query.all()
    form = JobPostForm()  # ✅ Pass form instance

    return render_template('admin/dashboard.html', jobs=jobs, applications=applications, form=form)

# Post Job
@admin_bp.route('/post-job', methods=['GET', 'POST'])
@admin_only
def post_job():
    form = JobPostForm()
    
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            description=form.description.data,
            salary=form.salary.data,
            company=form.company.data,  
            location=form.location.data,
            employer_id=current_user.id  
        )
        db.session.add(job)
        db.session.commit()
        flash("Job posted successfully!", "success")
        return redirect(url_for('admin_bp.admin_dashboard'))
    
    return render_template('admin/post_job.html', form=form)

# Delete User
@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@admin_only
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin_bp.admin_dashboard'))

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_bp.admin_dashboard'))

# Delete Job
@admin_bp.route('/delete-job/<int:job_id>', methods=['POST'])
@admin_only
def delete_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for('admin_bp.admin_dashboard'))

    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully!', 'success')
    return redirect(url_for('admin_bp.admin_dashboard'))

# Delete Job Application
from flask_wtf.csrf import validate_csrf

@admin_bp.route('/delete-application/<int:application_id>', methods=['POST'])
@admin_only
def delete_application(application_id):
    print("Received form data:", request.form)  
    
    csrf_token = request.form.get('csrf_token')
    if not csrf_token:
        print("CSRF Token Missing!")  
        flash("CSRF token missing!", "danger")
        return abort(400)

    try:
        validate_csrf(csrf_token)
    except Exception as e:
        print("CSRF Validation Failed:", e)  
        flash("Invalid CSRF token!", "danger")
        return abort(400)

    application = JobApplication.query.get(application_id)
    if not application:
        flash("Application not found.", "danger")
        return redirect(url_for('admin_bp.admin_dashboard'))

    db.session.delete(application)
    db.session.commit()
    flash('Job application deleted successfully!', 'success')
    return redirect(url_for('admin_bp.admin_dashboard'))

# View Resume
@resume_bp.route('/<filename>')
def view_resume(filename):
    safe_filename = secure_filename(filename)  # ✅ Prevent directory traversal
    resume_folder = os.path.join(current_app.root_path, 'static/uploads/resumes')  # ✅ Ensure correct folder
    file_path = os.path.join(resume_folder, safe_filename)

    print(f"Looking for resume at: {file_path}")  # ✅ Debugging

    if not os.path.exists(file_path):
        flash("Resume file not found.", "danger")
        return redirect(url_for('admin_bp.admin_dashboard'))

    return send_from_directory(resume_folder, safe_filename)