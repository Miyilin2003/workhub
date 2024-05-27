class User:
    def __init__(self, user_id, name, phone, email, username, password, security_question, email_verification_status, phone_verification_status, identify):
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.email = email
        self.username = username
        self.password = password
        self.security_question = security_question
        self.email_verification_status = email_verification_status
        self.phone_verification_status = phone_verification_status
        self.identify = identify #JobSeeker/HumanResources/Admin


class JobSeeker(User):
    # Additional methods specific to JobSeeker
    pass
class HumanResources(User):
    # Additional methods specific to HumanResources
    pass
class Admin(User):
    # Additional methods specific to Admin
    pass


class Resume:
    def __init__(self, resume_id, user_id, education_background, work_experience, skills_and_certificates, personal_profile, career_objective):
        self.resume_id = resume_id
        self.user_id = user_id
        self.education_background = education_background
        self.work_experience = work_experience
        self.skills_and_certificates = skills_and_certificates
        self.personal_profile = personal_profile
        self.career_objective = career_objective


class Job:
    def __init__(self, job_id, publisher_id, description, requirements, salary_range, location, publish_date, status):
        self.job_id = job_id
        self.publisher_id = publisher_id
        self.description = description
        self.requirements = requirements
        self.salary_range = salary_range
        self.location = location
        self.publish_date = publish_date
        self.status = status

class JobApplication:
    def __init__(self, application_id, job_seeker_id, position_id, status, application_date):
        self.application_id = application_id
        self.job_seeker_id = job_seeker_id
        self.position_id = position_id
        self.status = status
        self.application_date = application_date


class Interview:
    def __init__(self, interview_id, position_id, candidate_id, interview_time, interview_format):
        self.interview_id = interview_id
        self.position_id = position_id
        self.candidate_id = candidate_id
        self.interview_time = interview_time
        self.interview_format = interview_format


#创建mqsql的表语句
'''
    CREATE TABLE users (
    user_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    email VARCHAR(255),
    username VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    security_question TEXT,
    email_verification_status BOOLEAN,
    phone_verification_status BOOLEAN,
    identify VARCHAR(255)
);
'''

'''
CREATE TABLE job_seekers (
    user_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TABLE human_resources (
    user_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TABLE admins (
    user_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

'''

'''
CREATE TABLE resumes (
    resume_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    education_background TEXT,
    work_experience TEXT,
    skills_and_certificates TEXT,
    personal_profile TEXT,
    career_objective TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
'''

'''
CREATE TABLE jobs (
    job_id VARCHAR(255) PRIMARY KEY,
    publisher_id VARCHAR(255),
    description TEXT,
    requirements TEXT,
    salary_range VARCHAR(255),
    location VARCHAR(255),
    publish_date DATE,
    status BOOLEAN,
    FOREIGN KEY (publisher_id) REFERENCES users(user_id)
);
'''

'''
CREATE TABLE job_applications (
    application_id VARCHAR(255) PRIMARY KEY,
    job_seeker_id VARCHAR(255),
    position_id VARCHAR(255),
    status VARCHAR(255),
    application_date DATE,
    FOREIGN KEY (job_seeker_id) REFERENCES users(user_id),
    FOREIGN KEY (position_id) REFERENCES jobs(job_id)
);
'''

'''
CREATE TABLE job_applications (
    application_id VARCHAR(255) PRIMARY KEY,
    job_seeker_id VARCHAR(255),
    position_id VARCHAR(255),
    status VARCHAR(255),
    application_date DATE,
    FOREIGN KEY (job_seeker_id) REFERENCES users(user_id),
    FOREIGN KEY (position_id) REFERENCES jobs(job_id)
);
'''

'''
CREATE TABLE interviews (
    interview_id VARCHAR(255) PRIMARY KEY,
    position_id VARCHAR(255),
    candidate_id VARCHAR(255),
    interview_time DATETIME,
    interview_format VARCHAR(255),
    FOREIGN KEY (position_id) REFERENCES jobs(job_id),
    FOREIGN KEY (candidate_id) REFERENCES users(user_id)
);
'''
