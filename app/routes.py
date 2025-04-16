from flask import render_template, redirect, url_for, flash, request, Blueprint, current_app, send_from_directory
from app import bcrypt
from app.extension import db
from app.models import User, Job, JobApplication
from app.forms import RegistrationForm, LoginForm, JobPostForm, JobApplicationForm, ForgotPasswordForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid

# Initialize Blueprint
main = Blueprint('main', __name__)

# Home Page - Displays All Jobs

@main.route('/', methods=['GET', 'POST'])
def home():
    # Get filter values from the form
    location = request.args.get('location', '', type=str)
    category = request.args.get('category', '', type=str)
    company = request.args.get('company', '', type=str)

    # Base query
    query = Job.query

    # Apply filters if provided
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if category:
        query = query.filter(Job.category.ilike(f'%{category}%'))
    if company:
        query = query.filter(Job.company.ilike(f'%{company}%'))

    jobs = Job.query.with_entities(Job.id, Job.title, Job.location, Job.category, Job.salary, Job.description, Job.company).all()

    print([(job.id, job.title, job.company) for job in jobs])
    
    # Get distinct values for filters (to populate dropdowns)
    locations = Job.query.with_entities(Job.location).distinct()
    categories = Job.query.with_entities(Job.category).distinct()
    companies = Job.query.with_entities(Job.company).distinct()
    
    return render_template('home.html', jobs=jobs, locations=locations, categories=categories, companies=companies)


# User Registration
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role='seeker')
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)


# User Login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Logged in successfully!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    
    return render_template('login.html', form=form)


# Forgot Password Route
@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Password reset instructions have been sent to your email.', 'info')
            return redirect(url_for('main.login'))
        else:
            flash('Email not found in our records.', 'danger')
    
    return render_template('forgot_password.html', form=form)


# User Logout
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


# Post a Job (Employers Only)
@main.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role != 'employer':
        flash('Only employers can post jobs.', 'danger')
        return redirect(url_for('main.home'))
    
    form = JobPostForm()
    if form.validate_on_submit():
        job = Job(
            title=form.title.data.strip(), 
            description=form.description.data.strip(), 
            salary=form.salary.data, 
            location=form.location.data.strip(), 
            company=current_user.company,   
            employer_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('post_job.html', form=form)


# Apply for a Job (Job Seekers Only)
@main.route('/apply/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply(job_id):
    if current_user.role != 'seeker':
        flash('Only job seekers can apply for jobs.', 'danger')
        return redirect(url_for('main.home'))

    job = Job.query.get_or_404(job_id)
    form = JobApplicationForm()

    if form.validate_on_submit():
        resume_file = form.resume.data
        resume_filename = None

        if resume_file:
            filename = secure_filename(resume_file.filename)
            file_ext = os.path.splitext(filename)[1]
            unique_filename = f"{current_user.id}_{uuid.uuid4().hex}{file_ext}"

            resume_folder = os.path.join(current_app.root_path, 'static/uploads/resumes')  
            os.makedirs(resume_folder, exist_ok=True)

            resume_path = os.path.join(resume_folder, unique_filename)
            resume_file.save(resume_path)

            resume_filename = unique_filename  

        # Save to database
        application = JobApplication(
            cover_letter=form.cover_letter.data.strip(),
            resume=resume_filename,  
            job_id=job.id,
            user_id=current_user.id
        )
        db.session.add(application)
        db.session.commit()

        flash('Application submitted successfully!', 'success')
        return redirect(url_for('main.home'))

    return render_template('apply.html', form=form, job=job)


# Job Detail Page
@main.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)


# Serve Resume Files Securely
@main.route('/resume/<path:filename>')
@login_required
def serve_resume(filename):
    
    resume_folder = os.path.join(current_app.root_path, 'static/uploads/resumes')
    return send_from_directory(resume_folder, filename)
