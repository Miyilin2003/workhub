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
    def __init__(self, job_id, publisher_id, email, job_title, job_location, job_region, job_type, job_description, company_name, company_tagline, company_description, company_website, company_website_fb, company_website_tw, company_website_li, featured_image, company_logo, description, requirements, salary_range, location, publish_date, status):
        self.job_id = job_id
        self.publisher_id = publisher_id
        self.email = email
        self.job_title = job_title
        self.job_location = job_location
        self.job_region = job_region
        self.job_type = job_type
        self.job_description = job_description
        self.company_name = company_name
        self.company_tagline = company_tagline
        self.company_description = company_description
        self.company_website = company_website
        self.company_website_fb = company_website_fb
        self.company_website_tw = company_website_tw
        self.company_website_li = company_website_li
        self.featured_image = featured_image
        self.company_logo = company_logo
        self.description = description
        self.requirements = requirements
        self.salary_range = salary_range
        self.location = location
        self.publish_date = publish_date
        self.status = status
        self.category = 0


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
create_sql=[
        """
        CREATE TABLE IF NOT EXISTS users (
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
        """,
        """
        CREATE TABLE IF NOT EXISTS job_seekers (
            user_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS human_resources (
            user_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS admins (
            user_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS resumes (
            resume_id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255),
            education_background TEXT,
            work_experience TEXT,
            skills_and_certificates TEXT,
            personal_profile TEXT,
            career_objective TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """,
    """
    CREATE TABLE IF NOT EXISTS jobs (
        job_id VARCHAR(255) PRIMARY KEY,
        publisher_id VARCHAR(255),
        email VARCHAR(255),
        job_title VARCHAR(255),
        job_location VARCHAR(255),
        job_region VARCHAR(255),
        job_type ENUM('Part Time', 'Full Time'),
        job_description TEXT,
        company_name VARCHAR(255),
        company_tagline VARCHAR(255) NULL,
        company_description TEXT NULL,
        company_website VARCHAR(255) NULL,
        company_website_fb VARCHAR(255) NULL,
        company_website_tw VARCHAR(255) NULL,
        company_website_li VARCHAR(255) NULL,
        featured_image VARCHAR(255) NULL,
        company_logo VARCHAR(255) NULL,
        description TEXT,
        requirements TEXT,
        salary_range VARCHAR(255),
        location VARCHAR(255),
        publish_date DATE,
        status BOOLEAN,
        FOREIGN KEY (publisher_id) REFERENCES users(user_id),
        category VARCHAR(255)
    );
    """,
        """
        CREATE TABLE IF NOT EXISTS job_applications (
            application_id VARCHAR(255) PRIMARY KEY,
            job_seeker_id VARCHAR(255),
            position_id VARCHAR(255),
            status VARCHAR(255),
            application_date DATE,
            FOREIGN KEY (job_seeker_id) REFERENCES users(user_id),
            FOREIGN KEY (position_id) REFERENCES jobs(job_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS interviews (
            interview_id VARCHAR(255) PRIMARY KEY,
            position_id VARCHAR(255),
            candidate_id VARCHAR(255),
            interview_time DATETIME,
            interview_format VARCHAR(255),
            FOREIGN KEY (position_id) REFERENCES jobs(job_id),
            FOREIGN KEY (candidate_id) REFERENCES users(user_id)
        );
        """
    ]
