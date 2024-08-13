
from datetime import datetime
from flask_login import UserMixin
from flask import Flask
from app import db, login_manager
# app = Flask(__name__)
#
# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://addatsco_geox_user:Addatgeox??@162.214.195.234/addatsco_geox_dashboard'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



class Users(db.Model, UserMixin):

    id            = db.Column(db.Integer, primary_key=True)
    role      = db.Column(db.String(250), unique=False)
    fname      = db.Column(db.String(250), unique=False)
    lname      = db.Column(db.String(250), unique=False)
    email         = db.Column(db.String(250), unique=True)
    password      = db.Column(db.String(250))
    designation      = db.Column(db.String(250), unique=False)
    status = db.Column(db.String(200), nullable=False, default='Active')
    org_name      = db.Column(db.String(250), unique=False)
    org_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]
            setattr(self, property, value)

    def __repr__(self):
        return str(self.fname)


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    user = Users.query.filter_by(email=email).first()
    return user if user else None


class organization(db.Model, UserMixin):

    id            = db.Column(db.Integer, primary_key=True)
    company      = db.Column(db.String(250), unique=False)
    com_email      = db.Column(db.String(250), unique=False)
    com_web     = db.Column(db.String(250), unique=False)
    com_address      = db.Column(db.String(250), unique=False)
    num_employee      = db.Column(db.String(250), unique=False)
    com_number = db.Column(db.String(250), unique=True)
    linkedin     =  db.Column(db.Boolean, default=False, index=True)
    ziprecuiter     = db.Column(db.Boolean, default=False, index=True)
    fname      = db.Column(db.String(250), unique=False)
    lname      = db.Column(db.String(250), unique=False)
    email         = db.Column(db.String(250), unique=True)
    phone_number = db.Column(db.String(250), unique=True)
    password      = db.Column(db.String(250))
    status = db.Column(db.String(250), unique=True)
    note = db.Column(db.String(1500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class org_cred(db.Model, UserMixin):

    id            = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, nullable=False)
    company      = db.Column(db.String(250), unique=False)
    noti_email = db.Column(db.String(250), unique=False)
    iemail      = db.Column(db.String(250), unique=False)
    ipassword      = db.Column(db.String(250))
    zemail         = db.Column(db.String(250), unique=True)
    zpassword      = db.Column(db.String(250))
    status = db.Column(db.String(250), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class allforms_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    form_id = db.Column(db.Integer, nullable=True)
    filledby = db.Column(db.String(500), nullable=True)
    belongsto = db.Column(db.String(500), nullable=True)
    form_type = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(500), nullable=True)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.name)

    def get_related_form(self):
        if self.form_type == 'New Deals Contract Signed':
            return Marketing.query.get(self.form_id)
        elif self.form_type == 'Person Placement':
            return recruiting_data.query.get(self.form_id)
        else:
            return None

    def delete(self):
        related_form = self.get_related_form()
        if related_form:
            db.session.delete(related_form)
        db.session.delete(self)
        db.session.commit()

class userdesignation_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(500))

    def __repr__(self):
        return "{}".format(self.designation)
        return "{}".format(self.designation)


class Emails_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, nullable=False)
    message_id = db.Column(db.String(255), unique=True)

    sender_name = db.Column(db.String(255), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=True, index=True)
    subject_part1 = db.Column(db.String(255), nullable=False, index=True)
    subject_part2 = db.Column(db.String(255), nullable=False, index=True)
    formatted_date = db.Column(db.String(255), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False, index=True)
    file_content = db.Column(db.LargeBinary, nullable=True, index=True)
    pdf_content_json = db.Column(db.Text, nullable=True, index=True)
    phone_number = db.Column(db.String(255), nullable=True, index=True)
    action = db.Column(db.String(500), nullable=False, default='user', index=True)
    status = db.Column(db.String(500), nullable=False, default='applied', index=True)
    notes = db.Column(db.String(500), nullable=True, index=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    docs = db.relationship('Document', backref='email_data', lazy=True)  # Relationship with Document
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.sender_name, self.created_at)
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emails_data_id = db.Column(db.Integer, db.ForeignKey('emails_data.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_content = db.Column(db.LargeBinary, nullable=False)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return "{} - {}".format(self.file_name, self.created_at)

class Can_notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emails_data_id = db.Column(db.Integer, db.ForeignKey('emails_data.id'), nullable=False)
    notes = db.Column(db.String(1000), nullable=True)
    name = db.Column(db.String(50), nullable=True)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.sender_name, self.email)
class Hrforms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(500), nullable=True)
    candidate_name = db.Column(db.String(500), nullable=True)
    late = db.Column(db.String(500), nullable=True)
    informed = db.Column(db.String(500), nullable=True)
    otherreport = db.Column(db.String(500), nullable=True)
    reason_vacation = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.user_id, self.name)

class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(500), nullable=True)
    title = db.Column(db.String(500), nullable=True)
    image = db.Column(db.String(500), nullable=True)
    company = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(500), nullable=True)
    experience  = db.Column(db.String(500), nullable=True)
    job_type = db.Column(db.String(500), nullable=True)
    duration = db.Column(db.String(500), nullable=True)
    onsite = db.Column(db.String(500), nullable=True)
    salary_type = db.Column(db.String(500), nullable=True)
    salary = db.Column(db.String(500), nullable=True)
    job_date = db.Column(db.String(500), nullable=True)
    job_status = db.Column(db.String(500), nullable=True)
    description = db.Column(db.String(700), nullable=True)
    responsibility = db.Column(db.String(700), nullable=True)
    eligibility = db.Column(db.String(700), nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.user_id, self.name)



class Marketing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(500), nullable=True)
    company = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(500), nullable=True)
    substatus = db.Column(db.String(500), nullable=True)
    cperson = db.Column(db.String(500), nullable=True)
    cphone = db.Column(db.Integer, nullable=True)
    location = db.Column(db.String(500), nullable=True)
    Markup = db.Column(db.Integer, nullable=True)
    otherReport = db.Column(db.Text(1000), nullable=True)
    company_status = db.Column(db.String(500))
    Notes = db.Column(db.Text(1000), nullable=True)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.user_id, self.name)


class Deals_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marketing_id = db.Column(db.String(250), nullable=False)
    notes = db.Column(db.String(1000), nullable=False)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.notes, self.marketing_id)

class Deletedata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delete_id = db.Column(db.String(250), nullable=False)
    notes = db.Column(db.String(1000), nullable=False)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.notes, self.marketing_id)

class Otherfinal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(500), nullable=True)
    other_report = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.user_id, self.name)



class recruiting_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(500), nullable=True)
    candidate = db.Column(db.String(500), nullable=True)
    phone = db.Column(db.Integer, nullable=True)
    company = db.Column(db.String(500), nullable=True)
    did_you = db.Column(db.String(500), nullable=True)
    ecname = db.Column(db.String(500), nullable=True)
    ecnumber = db.Column(db.Integer, nullable=True)
    location = db.Column(db.String(500), nullable=True)
    locationcgoing = db.Column(db.String(500), nullable=True)
    starttime = db.Column(db.String(500), nullable=True)
    needmember = db.Column(db.String(500), nullable=True)
    interviewdate = db.Column(db.String(500), nullable=True)
    companydate = db.Column(db.String(500), nullable=True)
    help = db.Column(db.String(500), nullable=True)
    person_starting = db.Column(db.String(500), nullable=True)
    other_report = db.Column(db.String(500), nullable=True)
    position = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text(500), nullable=True)
    rnotes = db.Column(db.Text(1500), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    content = db.Column(db.LargeBinary, nullable=True)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.name, self.subject)

class candidateLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Joborder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    company_id = db.Column(db.Integer, nullable=True)
    company_name = db.Column(db.String(500), nullable=True)
    payrate = db.Column(db.Integer, nullable=True)
    jobstatus = db.Column(db.String(500), nullable=True)
    title = db.Column(db.String(500), nullable=True)
    salarytype = db.Column(db.String(500), nullable=True)
    starttime = db.Column(db.String(500), nullable=True)
    endtime = db.Column(db.String(500), nullable=True)
    vacancy = db.Column(db.Integer, nullable=True)
    archived = db.Column(db.Boolean, default=False)
    days = db.Column(db.String(500), nullable=True)
    filled_vacancy = db.Column(db.Integer, nullable=True)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.title, self.vacancy)

class Joborder_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    joborder_id = db.Column(db.String(250), nullable=False)
    notes = db.Column(db.String(1000), nullable=False)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.notes, self.joborder_id)

class otherreport_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    other_id = db.Column(db.String(250), nullable=False)
    notes = db.Column(db.String(1000), nullable=False)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return "{} - {}".format(self.notes, self.other_id)

class hr_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hr_id = db.Column(db.String(250), nullable=False)
    notes = db.Column(db.String(1000), nullable=False)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return "{} - {}".format(self.notes, self.hr_id)
class member_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(250), nullable=False)
    notes = db.Column(db.String(1000), nullable=False)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.notes, self.member_id)

class postjob_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postjod_id = db.Column(db.String(250), nullable=False)
    notes = db.Column(db.String(1000), nullable=False)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.notes, self.postjod_id)

class candidate_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.String(250), nullable=False)
    notes = db.Column(db.String(1000), nullable=False)
    org_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.notes, self.candidate_id)

class Targets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(500), nullable=False)
    new = db.Column(db.Integer, nullable=False)
    notsigned = db.Column(db.Integer, nullable=False)
    reopen = db.Column(db.Integer, nullable=False)
    resume = db.Column(db.Integer, nullable=False)
    interview =db.Column(db.Integer, nullable=False)
    placement = db.Column(db.Integer, nullable=False)
    helping = db.Column(db.Integer, nullable=False)
    target = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    weekstart = db.Column(db.Date, default=datetime.utcnow().date())
    weekend = db.Column(db.Date, default=datetime.utcnow().date())
    new_achieve = db.Column(db.Integer, nullable=False, default=0)
    notsigned_achieve = db.Column(db.Integer, nullable=False, default=0)
    reopen_achieve= db.Column(db.Integer, nullable=False, default=0)
    resume_achieve= db.Column(db.Integer, nullable=False, default=0)
    interview_achieve= db.Column(db.Integer, nullable=False, default=0)
    placement_achieve= db.Column(db.Integer, nullable=False, default=0)
    helping_achieve= db.Column(db.Integer, nullable=False, default=0)
    target_achieve= db.Column(db.Integer, nullable=False, default=0)
    score_achieve= db.Column(db.Integer, nullable=False, default=0)
    achieve_percentage = db.Column(db.Integer, nullable=False, default=0)
    org_id = db.Column(db.Integer, nullable=False)

class score_board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blue = db.Column(db.Integer, nullable=False)
    green = db.Column(db.Integer, nullable=False)
    yellow = db.Column(db.Integer)
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(500))

    def __repr__(self):
        return "{}".format(self.role_name)
