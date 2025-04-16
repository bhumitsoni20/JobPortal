from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed

# Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

# Job Posting Form
class JobPostForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Job Description', validators=[DataRequired(), Length(min=10, max=1000)])
    salary = FloatField('Salary', validators=[Optional(), NumberRange(min=0, message="Salary must be a positive number")])  # Ensure salary is positive
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max=100)])
    company = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Post Job')

# Job Application Form
class JobApplicationForm(FlaskForm):
    cover_letter = TextAreaField('Cover Letter', validators=[DataRequired(), Length(min=10, max=1000)])
    resume = FileField('Upload Resume', validators=[
        FileAllowed(['pdf', 'doc', 'docx'], 'Only PDF, DOC, or DOCX files are allowed!')
    ])  # Removed DataRequired() to allow optional uploads for edits
    submit = SubmitField('Apply')

class ForgotPasswordForm(FlaskForm):
    email=StringField('Email', validators=[DataRequired(), Email()])
    submit=SubmitField('Reset Password')