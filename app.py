from operator import or_

from flask import Flask, render_template, request, redirect, url_for, send_from_directory,session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from flask.cli import with_appcontext
import click
from datetime import datetime
import os
from flask_admin import Admin
import requests
from flask_admin.contrib.sqla import ModelView
import nlp
import time
app = Flask(__name__)
admin = Admin(app, name='My Admin', template_mode='bootstrap3')
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'
# 将040428改为自己的数据库密码，将jobseeker改为自己的数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:zhujingbo030420@localhost/jobseeker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
resume_id = 0
job_id = 0

db = SQLAlchemy(app)
def transfer_time_into_str(time):
    return str(time.tm_year) + str(time.tm_mon) + str(time.tm_mday) + str(time.tm_hour) + str(time.tm_min) + str(time.tm_sec)

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
    salary_range = db.Column(db.String(255))
    publish_date = db.Column(db.Date)
    status = db.Column(db.Boolean)
    job_type = db.Column(db.Enum('Part Time', 'Full Time'))
    job_description = db.Column(db.Text)
    company_name = db.Column(db.String(255))
    company_tagline = db.Column(db.String(255), nullable=True)
    company_description = db.Column(db.Text, nullable=True)
    company_website = db.Column(db.String(255), nullable=True)
    company_email = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255))   


class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    application_id = db.Column(db.String(255), primary_key=True)
    job_seeker_id = db.Column(db.String(255), db.ForeignKey('users.user_id'))
    position_id = db.Column(db.String(255), db.ForeignKey('jobs.job_id'))
    status = db.Column(db.String(255))
    application_date = db.Column(db.Date)

class Interview(db.Model):
    __tablename__ = 'interviews'
    interview_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    position_id = db.Column(db.String(255), db.ForeignKey('jobs.job_id'))
    candidate_id = db.Column(db.String(255), db.ForeignKey('users.user_id'))
    interview_time = db.Column(db.DateTime)
    interview_format = db.Column(db.String(255))
    sender_id = db.Column(db.String(255), nullable=False)
    receiver_id = db.Column(db.String(255), nullable=False)
# 为每个模型视图添加搜索功能
class UserView(ModelView):
    column_searchable_list = ('name', 'email', 'username', 'phone')

class JobSeekerView(ModelView):
    column_searchable_list = ('name',)

class HumanResourcesView(ModelView):
    column_searchable_list = ('name',)

class ResumeView(ModelView):
    column_searchable_list = ('resume_id', 'user_id')

class JobView(ModelView):
    column_searchable_list = ('job_title', 'company_name', 'job_location', 'email')

class JobApplicationView(ModelView):
    column_searchable_list = ('application_id', 'job_seeker_id', 'position_id', 'status')

class InterviewView(ModelView):
    column_searchable_list = ('interview_id', 'position_id', 'candidate_id', 'interview_format')

# 添加模型视图
admin.add_view(UserView(User, db.session))
admin.add_view(JobSeekerView(JobSeeker, db.session))
admin.add_view(HumanResourcesView(HumanResources, db.session))
admin.add_view(ResumeView(Resume, db.session))
admin.add_view(JobView(Job, db.session))
admin.add_view(JobApplicationView(JobApplication, db.session))
admin.add_view(InterviewView(Interview, db.session))



class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.String(255), db.ForeignKey('users.user_id'), nullable=False)
    receiver_id = db.Column(db.String(255), db.ForeignKey('users.user_id'), nullable=False)
    context = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    # 定义外键关系
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])



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
    session['rc'] = -1
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        identify = request.form['identify']

        session['username']=username

        user = User.query.filter_by(username=username, identify=identify).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            session['identify'] = user.identify
            session['user_id'] = user.user_id
            if session['identify'] == 'JobSeeker':
                return redirect(url_for('jshome'))
            elif session['identify'] == 'HumanResource':
                return redirect(url_for('hr_home'))
            elif session['identify'] == 'Admin':
                return redirect(url_for('admin1'))
        else:
            return 'Invalid credentials'

    return render_template('login.html')

@app.route('/admin1')
def admin1():
    return render_template('admin.html')

@app.route('/jshome')
def jshome():
    return render_template('js_home.html')

@app.route('/jsresume')
def jsresume():
    return render_template('js_resume.html')

@app.route('/hr_home')
def hr_home():
    return render_template('hr_home.html')

@app.route('/js_joblist')
def js_joblist():
    print(session['rc'])
    jobs = Job.query.order_by(desc(Job.publish_date)).all()
    job_list = []
    if session['rc'] == -1:
        for job in jobs:
            job_info = {
                'id': job.job_id,
                'job_title': job.job_title,
                'job_location': job.job_location,
                'job_type': job.job_type,
                'company_name': job.company_name,
            }
            job_list.append(job_info)
    else:
        for job in jobs:
            job_info = {
                'id': job.job_id,
                'job_title': job.job_title,
                'job_location': job.job_location,
                'job_type': job.job_type,
                'company_name': job.company_name,
            }
            print(job.category)
            if session['rc'] == int(job.category):
                print("==")
                job_list.insert(0,job_info)
            else:
                job_list.append(job_info)
    print(job_list)
    

    return render_template('js_joblist.html', jobs=job_list)

@app.route('/jsinterviews')
def jsinterviews():
    user_id = session['user_id']
    if user_id is None:
        return "User not logged in", 401
    print(user_id)
    # 查询面试信息，按ID排序
    interviews = Interview.query.filter_by(receiver_id=user_id).order_by(Interview.interview_id.desc()).all()
    interview_list = []
    for interview in interviews:
        interview_info = {
            'interview_id': interview.interview_id,
            'position_id': interview.position_id,
            'candidate_id': interview.candidate_id,
            'interview_time': interview.interview_time,
            'interview_format': interview.interview_format,
            'sender_id': interview.sender_id,
            'receiver_id': interview.receiver_id
        }
        interview_list.append(interview_info)
    print(interview_list)
    return render_template('js_interviews.html', interviews=interview_list)

@app.route('/hrinterviewlist')
def hrinterviewlist():
    user_id = session['user_id']
    if user_id is None:
        return "User not logged in", 401

    # 查询面试信息，按ID排序
    interviews = Interview.query.filter_by(sender_id=user_id).order_by(Interview.interview_id.desc()).all()
    interview_list = []
    for interview in interviews:
        interview_info = {
            'interview_id': interview.interview_id,
            'position_id': interview.position_id,
            'candidate_id': interview.candidate_id,
            'interview_time': interview.interview_time,
            'interview_format': interview.interview_format,
            'sender_id': interview.sender_id,
            'receiver_id': interview.receiver_id
        }
        interview_list.append(interview_info)
    print(interview_list)
    return render_template('hr_interviewlist.html', interviews=interview_list)

@app.route('/js_interviewdetails_<interview_id>')
def js_interviewdetails(interview_id):
    print(interview_id)
    interview = Interview.query.get_or_404(interview_id)
    return render_template('js_interviewdetails.html', interview=interview)

@app.route('/hr_interviewdetails_<interview_id>')
def hr_interviewdetails(interview_id):
    print(interview_id)
    interview = Interview.query.get_or_404(interview_id)
    return render_template('hr_interviewdetails.html', interview=interview)

@app.route('/tohr_postinterviews/<job_id>/<receiver_id>')
def tohr_postinterviews(job_id, receiver_id):
    return render_template('hr_postinterviews.html', job_id=job_id, receiver_id=receiver_id)


@app.route('/tojs_interviews')
def tojs_interviews():
    return render_template('js_interviews.html')

@app.route('/postinterviewaction/<job_id>/<receiver_id>', methods=['GET', 'POST'])
def postinterviewaction(job_id, receiver_id):
    if request.method == 'POST':
        position_id = job_id
        candidate_id = receiver_id
        interview_time = request.form['interview_time']
        interview_format = request.form['interview_format']
        sender_id = session['user_id']  # Assuming the sender is the logged-in user

        new_interview = Interview(
            position_id=position_id,
            candidate_id=candidate_id,
            interview_time=interview_time,
            interview_format=interview_format,
            sender_id=sender_id,
            receiver_id=receiver_id
        )

        db.session.add(new_interview)
        db.session.commit()
        return redirect(url_for('hrinterviewlist'))

    return render_template('post-interview.html')


@app.route('/js_chooseresumes_<job_id>')
def js_chooseresumes(job_id):
    user_id = session['user_id']
    if user_id is None:
        return "User not logged in", 401

    # 查询简历信息，按ID排序
    resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.resume_id.desc()).all()
    resume_list = []
    for resume in resumes:
        resume_info = {
            'resume_id': resume.resume_id,
            'education_background': resume.education_background,
            'work_experience': resume.work_experience,
            'skills_and_certificates': resume.skills_and_certificates,
            'career_objective': resume.career_objective
        }
        resume_list.append(resume_info)
    return render_template('js_resumelist1.html', resumes=resume_list, job_id=job_id)
@app.route('/js_sendresumes_<job_id>_<resume_id>')
def js_sendresumes( job_id,resume_id):
    application_id = resume_id
    user_id = session['user_id']
    status = True
    # 获取当前时间并格式化为 xxxx/xx/xx
    application_date = datetime.now().strftime('%Y/%m/%d')
    if user_id is None:
        return "User not logged in", 401
    new_application = JobApplication(
        application_id=application_id,
        job_seeker_id=user_id,
        position_id=job_id,
        status=status,
        application_date=application_date
        )
    db.session.add(new_application)
    db.session.commit()
    return render_template('js_sendresumesuccess.html')

@app.route('/jsresumelist')
def jsresumelist():
    user_id = session['user_id']
    if user_id is None:
        return "User not logged in", 401

    # 查询简历信息，按ID排序
    resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.resume_id.desc()).all()
    resume_list = []
    for resume in resumes:
        resume_info = {
            'resume_id': resume.resume_id,
            'education_background': resume.education_background,
            'work_experience': resume.work_experience,
            'skills_and_certificates': resume.skills_and_certificates,
            'career_objective': resume.career_objective
        }
        s = str(resume.career_objective)
        resume_list.append(resume_info)
    p = nlp.predict(s)
    session['rc']=int(p)
    return render_template('js_resumelist.html', resumes=resume_list)

@app.route('/js_details_<resume_id>')
def js_resumedetails(resume_id):
    print(resume_id)
    resume = Resume.query.get_or_404(resume_id)
    return render_template('js_resumedetails.html', resume=resume,resume_id=resume_id)

@app.route('/hr_resumedetails_<resume_id>')
def hr_resumedetails(resume_id):
    print(resume_id)
    resume = Resume.query.get_or_404(resume_id)
    return render_template('hr_resumedetails.html', resume=resume,resume_id=resume_id)

@app.route('/js_jobdetails_<job_id>')
def js_jobdetails(job_id):
    print(job_id)
    job = Job.query.get_or_404(job_id)
    # print(job)
    return render_template('js_jobdetails.html',job=job)

@app.route('/hr_joblist')
def hr_joblist():
    user_id = session['user_id']
    if user_id is None:
        return "User not logged in", 401

    jobs = Job.query.filter_by(publisher_id=user_id).order_by(desc(Job.publish_date)).all()
    job_list = []
    for job in jobs:
        job_info = {
            'id': job.job_id,
            'job_title': job.job_title,
            'job_location': job.job_location,
            'job_type': job.job_type,
            'company_name': job.company_name,
        }
        job_list.append(job_info)
    # print(job_list)

    return render_template('hr_joblist.html',jobs=job_list)

@app.route('/hr_resumelist_<job_id>')
def hr_resumelist(job_id):
    # 第一步：查询 JobApplication 表
    applications = JobApplication.query.filter_by(position_id=job_id).order_by(JobApplication.job_seeker_id.desc()).all()
    application_ids = [a.application_id for a in applications]
    
    # 第二步：查询 Resume 表

    # 查询简历信息，按ID排序
    resumes = Resume.query.filter(Resume.resume_id.in_(application_ids)).order_by(Resume.resume_id.desc()).all()

    resume_list = []
    for resume in resumes:
        resume_info = {
            'user_id': resume.user_id,
            'resume_id': resume.resume_id,
            'education_background': resume.education_background,
            'work_experience': resume.work_experience,
            'skills_and_certificates': resume.skills_and_certificates,
            'career_objective': resume.career_objective
        }
        resume_list.append(resume_info)
    print(resume_list)
    return render_template('hr_resumelist.html', resumes=resume_list,job_id=job_id)


@app.route('/hr_jobdetails_<job_id>')
def hr_jobdetails(job_id):
    print(job_id)
    job = Job.query.get_or_404(job_id)
    print(job)
    return render_template('hr_jobdetails.html',job=job)

@app.route('/hr_message')
def hr_message():
    user_id = session['user_id']

    # 查询所有与当前用户相关的聊天记录，并按最新消息的时间排序
    messages = db.session.query(
        Message.sender_id, Message.receiver_id, db.func.max(Message.timestamp).label('latest_timestamp')
    ).filter(
        or_(Message.sender_id == user_id, Message.receiver_id == user_id)
    ).group_by(
        Message.sender_id, Message.receiver_id
    ).order_by(
        desc('latest_timestamp')
    ).all()

    # 提取与当前用户聊过天的用户ID，并按最新消息的时间排序
    chat_users = {}
    for message in messages:
        if message.sender_id != user_id:
            chat_users[message.sender_id] = message.latest_timestamp
        elif message.receiver_id != user_id:
            chat_users[message.receiver_id] = message.latest_timestamp

    # 根据最新消息的时间对用户进行排序
    sorted_chat_users = sorted(chat_users.items(), key=lambda x: x[1], reverse=True)
    sorted_chat_user_ids = [user_id for user_id, _ in sorted_chat_users]

    # 查询这些用户的信息
    chat_user_info = User.query.filter(User.user_id.in_(sorted_chat_user_ids)).all()
    chat_user_info_sorted = sorted(chat_user_info, key=lambda u: sorted_chat_user_ids.index(u.user_id))

    # 获取每个用户的最近两条聊天记录
    user_recent_messages = {}
    for user in chat_user_info_sorted:
        recent_messages = Message.query.filter(
            or_(
                (Message.sender_id == user_id) & (Message.receiver_id == user.user_id),
                (Message.sender_id == user.user_id) & (Message.receiver_id == user_id)
            )
        ).order_by(Message.timestamp.desc()).limit(2).all()
        user_recent_messages[user.user_id] = recent_messages

    return render_template('hr_message.html', chat_user_info=chat_user_info_sorted,
                           user_recent_messages=user_recent_messages)

@app.route('/js_message')
def js_message():
    user_id = session['user_id']

    # 查询所有与当前用户相关的聊天记录，并按最新消息的时间排序
    messages = db.session.query(
        Message.sender_id, Message.receiver_id, db.func.max(Message.timestamp).label('latest_timestamp')
    ).filter(
        or_(Message.sender_id == user_id, Message.receiver_id == user_id)
    ).group_by(
        Message.sender_id, Message.receiver_id
    ).order_by(
        desc('latest_timestamp')
    ).all()

    # 提取与当前用户聊过天的用户ID，并按最新消息的时间排序
    chat_users = {}
    for message in messages:
        if message.sender_id != user_id:
            chat_users[message.sender_id] = message.latest_timestamp
        elif message.receiver_id != user_id:
            chat_users[message.receiver_id] = message.latest_timestamp

    # 根据最新消息的时间对用户进行排序
    sorted_chat_users = sorted(chat_users.items(), key=lambda x: x[1], reverse=True)
    sorted_chat_user_ids = [user_id for user_id, _ in sorted_chat_users]

    # 查询这些用户的信息
    chat_user_info = User.query.filter(User.user_id.in_(sorted_chat_user_ids)).all()
    chat_user_info_sorted = sorted(chat_user_info, key=lambda u: sorted_chat_user_ids.index(u.user_id))

    # 获取每个用户的最近两条聊天记录
    user_recent_messages = {}
    for user in chat_user_info_sorted:
        recent_messages = Message.query.filter(
            or_(
                (Message.sender_id == user_id) & (Message.receiver_id == user.user_id),
                (Message.sender_id == user.user_id) & (Message.receiver_id == user_id)
            )
        ).order_by(Message.timestamp.desc()).limit(2).all()
        user_recent_messages[user.user_id] = recent_messages

    return render_template('js_message.html', chat_user_info=chat_user_info_sorted,
                           user_recent_messages=user_recent_messages)

@app.route('/js_chat_<publisher_id>')
def js_chat(publisher_id):
    user_id = session['user_id']
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == publisher_id)) |
        ((Message.sender_id == publisher_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp.asc()).all()
    chat_user = User.query.get(publisher_id)
    chat_user_name = chat_user.name if chat_user else "Unknown User"

    return render_template('js_chat.html', user_name=user_id, chat_name=publisher_id, messages=messages,
                           chat_user_name=chat_user_name)

@app.route('/hr_chat_<publisher_id>')
def hr_chat(publisher_id):
    user_id = session['user_id']
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == publisher_id)) |
        ((Message.sender_id == publisher_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp.asc()).all()
    chat_user = User.query.get(publisher_id)
    chat_user_name = chat_user.name if chat_user else "Unknown User"

    print(messages)
    for message in messages:
        print(message.sender_id)

    print(user_id)

    return render_template('hr_chat.html', user_name=user_id, chat_name=publisher_id, messages=messages,
                           chat_user_name=chat_user_name)

@app.route('/js_create_message_<user_name>_<chat_name>', methods=['POST'])
def js_create_message(user_name,chat_name):
    content = request.form['chat_content']
    new_message = Message(
        sender_id=user_name,
        receiver_id=chat_name,
        context=content
    )
    db.session.add(new_message)
    db.session.commit()
    return redirect(url_for('js_chat',publisher_id=chat_name))

@app.route('/hr_create_message_<user_name>_<chat_name>', methods=['POST'])
def hr_create_message(user_name,chat_name):
    content = request.form['chat_content']
    new_message = Message(
        sender_id=user_name,
        receiver_id=chat_name,
        context=content
    )
    db.session.add(new_message)
    db.session.commit()
    return redirect(url_for('hr_chat',publisher_id=chat_name))


@app.route('/postjob')
def postjob():
    return render_template('post-job.html')



@app.route('/postjobaction', methods=['GET', 'POST'])
def postjobaction():
    global job_id
    job_id += 1
    if request.method == 'POST':
        email = request.form['email']
        job_title = request.form['job_title']
        job_location = request.form['job_location']
        job_type = request.form['job_type']
        job_description = request.form.get('job_description')
        salary_range = request.form.get('salary_range',None)
        publish_date = request.form.get('publish_date')
        status = request.form.get('status')
        # 将 'status' 转换为布尔类型
        if status is not None:
            status = status.lower() in ['true', '1', 'yes', 'on']
        else:
            status = False  # 默认值可以根据需求设置
        company_name = request.form['company_name']
        company_tagline = request.form.get('company_tagline',None)
        company_description = request.form.get('company_description',None)
        company_website = request.form.get('company_website',None)
        company_email = request.form.get('company_email',None)
        new_job = Job(
            job_id=job_id,
            publisher_id=session['user_id'],
            email=email,
            job_title=job_title,
            job_location=job_location,
            salary_range = salary_range,
            publish_date=publish_date,
            status  = status,
            job_type=job_type,
            job_description=job_description,
            company_name=company_name,
            company_tagline=company_tagline,
            company_description=company_description,
            company_website=company_website,
            company_email=company_email,
            category = nlp.predict(job_description)
        )

        db.session.add(new_job)
        db.session.commit()
        return redirect(url_for('hr_joblist'))

    return render_template('post-job.html')

@app.route('/change_post_<job_id>', methods=['GET', 'POST'])
def change_post(job_id):
    if request.method == 'POST':
        job = Job.query.get_or_404(job_id)

        # 从表单中获取新的数据并更新实例属性
        job.email = request.form['email']
        job.job_title = request.form['job_title']
        job.job_location = request.form['job_location']
        job.job_type = request.form['job_type']
        job.job_description = request.form.get('job_description')
        job.salary_range = request.form.get('salary_range', None)
        job.publish_date = request.form.get('publish_date')
        status = request.form.get('status')

        # 将 'status' 转换为布尔类型
        if status is not None:
            job.status = status.lower() in ['true', '1', 'yes', 'on']
        else:
            job.status = False  # 默认值可以根据需求设置

        job.company_name = request.form['company_name']
        job.company_tagline = request.form.get('company_tagline', None)
        job.company_description = request.form.get('company_description', None)
        job.company_website = request.form.get('company_website', None)
        job.company_email = request.form.get('company_email', None)

        # 提交更改到数据库
        db.session.commit()
        return redirect(url_for('hr_joblist'))

    return render_template('post-job.html')


@app.route('/change_resume/<resume_id>', methods=['GET', 'POST'])
def change_resume(resume_id):
    if request.method == 'POST':
        resume = Resume.query.get_or_404(resume_id)
        resume.education_background=request.form['education_background']
        resume.work_experience=request.form['work_experience']
        resume.skills_and_certificates=request.form['skills_and_certificates']
        resume.career_objective=request.form['career_objective']
        db.session.commit()
        return redirect(url_for('js_resumedetails', resume_id=resume_id))



@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    global resume_id
    global resume_category
    if request.method == 'POST':
        resume_id += 1
        user_id = request.form['user_id']
        education_background = request.form['education_background']
        work_experience = request.form['work_experience']
        skills_and_certificates = request.form['skills_and_certificates']
        career_objective = request.form['career_objective']
        resume_pdf = request.files['resume_pdf']
        session['rc'] = nlp.predict(career_objective)
        print("resume_category:",session['rc'])
        if resume_pdf and resume_pdf.filename.endswith('.pdf'):
            # filename = secure_filename(resume_pdf.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_pdf.filename)
            resume_pdf.save(file_path)

            # Upload the PDF to ufile.io

            personal_profile = file_path

                # Save to database (example, adjust as needed)
            new_resume = Resume(
                resume_id=resume_id,
                user_id=user_id,
                education_background=education_background,
                work_experience=work_experience,
                skills_and_certificates=skills_and_certificates,
                personal_profile=personal_profile,
                career_objective=career_objective,
            )
            db.session.add(new_resume)
            db.session.commit()
            
            
            return redirect(url_for('resume_success'))

    return render_template('upload_resume.html')


@app.route('/download_resume/<int:resume_id>')
def download_resume(resume_id):
    resume = Resume.query.get(resume_id)
    if resume:
        file_path = resume.personal_profile
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        return "Resume not found", 404



@app.route('/resume_success')
def resume_success():
    return render_template('resume_uploaded_successful.html')

@app.route('/job-posted')
def job_posted():
    return "Job successfully posted!"

# @app.route('/upload_resume', methods=['GET', 'POST'])
# def upload_resume():
#     if request.method == 'POST':
#         user_id = request.form['user_id']
#         education_background = request.form['education_background']
#         work_experience = request.form['work_experience']
#         skills_and_certificates = request.form['skills_and_certificates']
#         career_objective = request.form['career_objective']
#         resume_pdf = request.files['resume_pdf']

#         if resume_pdf and resume_pdf.filename.endswith('.pdf'):
#             # filename = secure_filename(resume_pdf.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_pdf.filename)
#             resume_pdf.save(file_path)

#             # Upload the PDF to ufile.io

#             personal_profile = file_path

#                 # Save to database (example, adjust as needed)
#             new_resume = Resume(
#                 resume_id=user_id,
#                 user_id=user_id,
#                 education_background=education_background,
#                 work_experience=work_experience,
#                 skills_and_certificates=skills_and_certificates,
#                 personal_profile=personal_profile,
#                 career_objective=career_objective
#             )
#             db.session.add(new_resume)
#             db.session.commit()

#             return redirect(url_for('jsresumelist'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('identify', None)
    return redirect(url_for('home'))

# @app.route('/')
# def HR_home():
#     return redirect(url_for('HR/main.html'))
#
# @app.route('/HR')
# def HR():
#    return render_template('HR/index.html')
#
# @app.route('/HR/about')
# def about():
#    return render_template('HR/about.html')
#
# @app.route('/JS')
# def JS():
#    return render_template('HR/index.html')
#
# @app.route('/Admin')
# def admin():
#    return render_template('HR/index.html')


if __name__ == '__main__':
    app.run(debug=True)
