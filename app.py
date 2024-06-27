from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask.cli import with_appcontext
import click
import os

import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'
# 将040428改为自己的数据库密码，将jobseeking改为自己的数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:040428@localhost/jobseeker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(255))
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    security_question = db.Column(db.Text)
    email_verification_status = db.Column(db.Boolean)
    phone_verification_status = db.Column(db.Boolean)
    identify = db.Column(db.String(255))

class JobSeeker(db.Model):
    __tablename__ = 'job_seekers'
    user_id = db.Column(db.String(255), db.ForeignKey('users.user_id'), primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class HumanResources(db.Model):
    __tablename__ = 'human_resources'
    user_id = db.Column(db.String(255), db.ForeignKey('users.user_id'), primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class Admin(db.Model):
    __tablename__ = 'admins'
    user_id = db.Column(db.String(255), db.ForeignKey('users.user_id'), primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class Resume(db.Model):
    __tablename__ = 'resumes'
    resume_id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey('users.user_id'))
    education_background = db.Column(db.Text)
    work_experience = db.Column(db.Text)
    skills_and_certificates = db.Column(db.Text)
    personal_profile = db.Column(db.Text)
    career_objective = db.Column(db.Text)

class Job(db.Model):
    __tablename__ = 'jobs'
    job_id = db.Column(db.String(255), primary_key=True)
    publisher_id = db.Column(db.String(255), db.ForeignKey('users.user_id'))
    email = db.Column(db.String(255))
    job_title = db.Column(db.String(255))
    job_location = db.Column(db.String(255))
    job_region = db.Column(db.String(255))
    job_type = db.Column(db.Enum('Part Time', 'Full Time'))
    job_description = db.Column(db.Text)
    company_name = db.Column(db.String(255))
    company_tagline = db.Column(db.String(255), nullable=True)
    company_description = db.Column(db.Text, nullable=True)
    company_website = db.Column(db.String(255), nullable=True)
    company_website_fb = db.Column(db.String(255), nullable=True)
    company_website_tw = db.Column(db.String(255), nullable=True)
    company_website_li = db.Column(db.String(255), nullable=True)
    featured_image = db.Column(db.String(255), nullable=True)
    company_logo = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    salary_range = db.Column(db.String(255))
    location = db.Column(db.String(255))
    publish_date = db.Column(db.Date)
    status = db.Column(db.Boolean)

class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    application_id = db.Column(db.String(255), primary_key=True)
    job_seeker_id = db.Column(db.String(255), db.ForeignKey('users.user_id'))
    position_id = db.Column(db.String(255), db.ForeignKey('jobs.job_id'))
    status = db.Column(db.String(255))
    application_date = db.Column(db.Date)

class Interview(db.Model):
    __tablename__ = 'interviews'
    interview_id = db.Column(db.String(255), primary_key=True)
    position_id = db.Column(db.String(255), db.ForeignKey('jobs.job_id'))
    candidate_id = db.Column(db.String(255), db.ForeignKey('users.user_id'))
    interview_time = db.Column(db.DateTime)
    interview_format = db.Column(db.String(255))

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()

app.cli.add_command(create_tables)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        security_question = request.form['security_question']
        email_verification_status = False
        phone_verification_status = False
        identify = request.form['identify']

        new_user = User(user_id=user_id, name=name, phone=phone, email=email, username=username,
                        password=password, security_question=security_question,
                        email_verification_status=email_verification_status,
                        phone_verification_status=phone_verification_status, identify=identify)

        db.session.add(new_user)
        db.session.commit()

        if identify == 'JobSeeker':
            job_seeker = JobSeeker(user_id=user_id, name=name)
            db.session.add(job_seeker)
        elif identify == 'HumanResource':
            human_resource = HumanResources(user_id=user_id, name=name)
            db.session.add(human_resource)
        elif identify == 'Admin':
            admin = Admin(user_id=user_id, name=name)
            db.session.add(admin)
        
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        identify = request.form['identify']
        user = User.query.filter_by(username=username, identify=identify).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            session['identify'] = user.identify
            if session['identify'] == 'JobSeeker':
                return redirect(url_for('resume'))
            elif session['identify'] == 'HumanResource':
                return redirect(url_for('postjob'))
            elif session['identify'] == 'Admin':
                return redirect(url_for('home'))
        else:
            return 'Invalid credentials'

    return render_template('login.html')

@app.route('/postjob')
def postjob():
    return render_template('post-job.html')

@app.route('/postjobaction', methods=['GET', 'POST'])
def postjobaction():
    if request.method == 'POST':
        email = request.form['email']
        job_title = request.form['job_title']
        job_location = request.form['job_location']
        job_region = request.form['job_region']
        job_type = request.form['job_type']
        job_description = request.form.get('job_description')
        company_name = request.form['company_name']
        company_tagline = request.form.get('company_tagline')
        company_description = request.form.get('company_description')
        company_website = request.form.get('company_website')
        company_website_fb = request.form.get('company_website_fb')
        company_website_tw = request.form.get('company_website_tw')
        company_website_li = request.form.get('company_website_li')
        featured_image = request.files['featured_image'].filename
        company_logo = request.files['company_logo'].filename

        new_job = Job(
            job_id=str(1),
            publisher_id=None,
            email=email,
            job_title=job_title,
            job_location=job_location,
            job_region=job_region,
            job_type=job_type,
            job_description=job_description,
            company_name=company_name,
            company_tagline=company_tagline,
            company_description=company_description,
            company_website=company_website,
            company_website_fb=company_website_fb,
            company_website_tw=company_website_tw,
            company_website_li=company_website_li,
            featured_image=featured_image,
            company_logo=company_logo,
            description="1",
            requirements="1",
            salary_range="1",
            location="1",
            publish_date="03/01/01",
            status=True
        )
        # i+=1
        db.session.add(new_job)
        db.session.commit()
        return render_template('post-job.html')

    return render_template('post-job.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        user_id = request.form['user_id']
        education_background = request.form['education_background']
        work_experience = request.form['work_experience']
        skills_and_certificates = request.form['skills_and_certificates']
        career_objective = request.form['career_objective']
        resume_pdf = request.files['resume_pdf']

        if resume_pdf and resume_pdf.filename.endswith('.pdf'):
            # filename = secure_filename(resume_pdf.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_pdf.filename)
            resume_pdf.save(file_path)

            # Upload the PDF to ufile.io

            personal_profile = file_path

                # Save to database (example, adjust as needed)
            new_resume = Resume(
                resume_id=int(user_id),
                user_id=user_id,
                education_background=education_background,
                work_experience=work_experience,
                skills_and_certificates=skills_and_certificates,
                personal_profile=personal_profile,
                career_objective=career_objective
            )
            db.session.add(new_resume)
            db.session.commit()

            return redirect(url_for('resume_success'))

    return render_template('upload_resume.html')

@app.route('/resume_success')
def resume_success():
    return "Resume uploaded and profile generated successfully!"

@app.route('/job-posted')
def job_posted():
    return "Job successfully posted!"
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('identify', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
