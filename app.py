from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask.cli import with_appcontext
import click

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 将040428改为自己的数据库密码，将jobseeking改为自己的数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:040428@localhost/jobseeking'
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
            return redirect(url_for('home'))
        else:
            return 'Invalid credentials'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('identify', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
