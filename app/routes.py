import re
from docx import Document
from dateutil.relativedelta import relativedelta
import PyPDF2
from app.model import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from . import db, app
from werkzeug.utils import secure_filename
import os
import io
from flask import (
    Flask,
    session,
    render_template,
    redirect,
    request,
    url_for,
    jsonify,
    send_file,
    Response,
)
from passlib.hash import sha256_crypt
from flask_login import login_user
from sqlalchemy import desc, exists, func, case, or_, extract, and_, distinct
from functools import wraps
from app.forms import LoginForm, CreateAccountForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import pycountry_convert as pc
import pycountry
import csv
from math import ceil
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import base64
import bcrypt
import schedule
import time
import multiprocessing
import schedule
import threading
import time
from app.util import verify_pass
from datetime import datetime, timedelta
from base64 import b64encode
import schedule
import threading
import time

# Set a secret key for session management
app.secret_key = "geoxhr123??"
from flask import send_file, jsonify, make_response
import io
import os
import mimetypes
from itertools import chain
from sqlalchemy import or_, not_
import logging

from collections import defaultdict


# ... (other imports and database setup)

# # Configure Flask-Session to use Redis
# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
# app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Allow cross-site cookie access (important for iframes)
# app.config['SESSION_COOKIE_SECURE'] = False  # Only send cookies over HTTPS (recommended for production)
# fs.init_app(app)

# # Initialize storage
# storage = fs.Storage('files')
# Session(app)

# Define global variables
global_user_id = None
global_role = None
global_org_id = None
global_user_name = None
global_user_email = None

    
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session or "role" not in session:
                return redirect(url_for("login"))

            user_role = request.cookies.get("role")
            if user_role not in allowed_roles:
                return redirect(url_for("login"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def format_job_description(description):
    # Check for numbered list format (e.g., "1. Item 1\n2. Item 2")
    if re.match(r"^\d+\.\s", description, re.MULTILINE):
        formatted_description = re.sub(
            r"^(\d+\.\s)", r"<li>\1", description, flags=re.MULTILINE
        )
        formatted_description = f"<ul>{formatted_description}</ul>"
    # Check for bulleted list format (e.g., "• Item 1\n• Item 2")
    elif re.match(r"^•\s", description, re.MULTILINE):
        formatted_description = re.sub(
            r"^(•\s)", r"<li>\1", description, flags=re.MULTILINE
        )
        formatted_description = f"<ul>{formatted_description}</ul>"
    # Plain text
    else:
        formatted_description = description

    return formatted_description


def extract_pdf_text(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text_content = ""
    for page in pdf_reader.pages:
        text_content += page.extract_text()
    binary_pdf_content = text_content.encode("utf-8")
    return binary_pdf_content


def extract_pdf_content(pdf_file):
    content = pdf_file.read()
    return content


def extract_docx_content(docx_file):
    doc = Document(docx_file)
    content = docx_file.read()
    return content


def format_posted_time(created_at):
    current_time = datetime.now()
    time_difference = current_time - created_at

    if time_difference.days == 1:
        return "1 day ago"
    elif time_difference.days > 1 and time_difference.days <= 7:
        return f"{time_difference.days} days ago"
    else:
        return created_at.strftime("%Y-%m-%d %H:%M:%S")  # Fallback to original format


@app.route("/websitejobs")
def websitejobs():
    alljobs = (
        Jobs.query.filter(
            Jobs.job_status == "active", Jobs.company.in_(["1", "12", "13", "123"])
        )
        .order_by(desc(Jobs.created_at))
        .all()
    )
    formatted_times = [format_posted_time(job.created_at) for job in alljobs]
    for job, formatted_time in zip(alljobs, formatted_times):
        job.formatted_time = formatted_time
    return render_template("websitejobs.html", alljobs=alljobs)


@app.route("/handshrjobs")
def handshrjobs():
    alljobs = (
        Jobs.query.filter(
            Jobs.job_status == "active", Jobs.company.in_(["2", "12", "23", "123"])
        )
        .order_by(desc(Jobs.created_at))
        .all()
    )
    formatted_times = [format_posted_time(job.created_at) for job in alljobs]
    for job, formatted_time in zip(alljobs, formatted_times):
        job.formatted_time = formatted_time
    return render_template("handshrjobs.html", alljobs=alljobs)


@app.route("/i8isjobs")
def i8isjobs():
    alljobs = (
        Jobs.query.filter(
            Jobs.job_status == "active", Jobs.company.in_(["3", "13", "23", "123"])
        )
        .order_by(desc(Jobs.created_at))
        .all()
    )
    formatted_times = [format_posted_time(job.created_at) for job in alljobs]
    for job, formatted_time in zip(alljobs, formatted_times):
        job.formatted_time = formatted_time
    return render_template("i8isjobs.html", alljobs=alljobs)


@app.route("/i8isjobdetails/<int:id>")
def i8isjobdetails(id):
    jobdetail = Jobs.query.filter(Jobs.id == id).first()
    formatted_time = format_posted_time(jobdetail.created_at)
    jobdetail.formatted_time = formatted_time  # Attach formatted time to the job detail
    job_description = jobdetail.description
    formatted_notes = format_job_description(jobdetail.notes)
    formatted_eligibility = format_job_description(jobdetail.eligibility)
    formatted_responsibility = format_job_description(jobdetail.responsibility)
    formatted_description = format_job_description(job_description)
    jobdetail.formatted_notes = formatted_notes
    jobdetail.formatted_eligibility = formatted_eligibility
    jobdetail.formatted_responsibility = formatted_responsibility
    jobdetail.formatted_description = formatted_description
    # print(formatted_description)
    # print(jobdetail.formatted_time)

    latest_jobs = Jobs.query.order_by(Jobs.created_at.desc()).limit(2).all()
    format_time = [format_posted_time(data.created_at) for data in latest_jobs]
    for job, format_time in zip(latest_jobs, format_time):
        job.format_time = format_time
    return render_template(
        "i8isjobdetails.html", jobdetail=jobdetail, latest_jobs=latest_jobs
    )


@app.route("/handshrjobdetail/<int:id>")
def handshrjobdetail(id):
    jobdetail = Jobs.query.filter(Jobs.id == id).first()
    formatted_time = format_posted_time(jobdetail.created_at)
    jobdetail.formatted_time = formatted_time  # Attach formatted time to the job detail
    job_description = jobdetail.description
    formatted_notes = format_job_description(jobdetail.notes)
    formatted_eligibility = format_job_description(jobdetail.eligibility)
    formatted_responsibility = format_job_description(jobdetail.responsibility)
    formatted_description = format_job_description(job_description)
    jobdetail.formatted_notes = formatted_notes
    jobdetail.formatted_eligibility = formatted_eligibility
    jobdetail.formatted_responsibility = formatted_responsibility
    jobdetail.formatted_description = formatted_description
    # print(formatted_description)
    # print(jobdetail.formatted_time)

    latest_jobs = Jobs.query.order_by(Jobs.created_at.desc()).limit(2).all()
    format_time = [format_posted_time(data.created_at) for data in latest_jobs]
    for job, format_time in zip(latest_jobs, format_time):
        job.format_time = format_time
    return render_template(
        "handshrjobdetail.html", jobdetail=jobdetail, latest_jobs=latest_jobs
    )


@app.route("/jobdetail/<int:id>")
def jobdetail(id):
    jobdetail = Jobs.query.filter(Jobs.id == id).first()
    formatted_time = format_posted_time(jobdetail.created_at)
    jobdetail.formatted_time = formatted_time  # Attach formatted time to the job detail
    job_description = jobdetail.description
    formatted_notes = format_job_description(jobdetail.notes)
    formatted_eligibility = format_job_description(jobdetail.eligibility)
    formatted_responsibility = format_job_description(jobdetail.responsibility)
    formatted_description = format_job_description(job_description)
    jobdetail.formatted_notes = formatted_notes
    jobdetail.formatted_eligibility = formatted_eligibility
    jobdetail.formatted_responsibility = formatted_responsibility
    jobdetail.formatted_description = formatted_description
    # print(formatted_description)
    # print(jobdetail.formatted_time)

    latest_jobs = Jobs.query.order_by(Jobs.created_at.desc()).limit(2).all()
    format_time = [format_posted_time(data.created_at) for data in latest_jobs]
    for job, format_time in zip(latest_jobs, format_time):
        job.format_time = format_time
    return render_template(
        "postjobdetail.html", jobdetail=jobdetail, latest_jobs=latest_jobs
    )


@app.route("/apply", methods=["POST"])
def apply():
    if request.method == "POST":
        fname = request.form.get("firstName")
        lname = request.form.get("lastName")
        email = request.form.get("email")
        phone = request.form.get("number")
        position = request.form.get("position")
        file = request.files["myFile"]
        jobid = request.form.get("jobid")
        org_id = 1

        filename = file.filename
        if file and filename:  # Check if the file has a valid extension
            content = file.read()
        else:
            content = None
        current_datee = datetime.now().strftime("%a, %d %b %Y")
        exist = Emails_data.query.filter(
            and_(Emails_data.email == email, Emails_data.subject_part1 == position)
        ).all()

        current_date = datetime.now()
        one_month_ago = current_date - relativedelta(months=1)
        if exist:
            for check in exist:
                formatted_date = datetime.strptime(check.formatted_date, "%a, %d %b %Y")
                # print(formatted_date, one_month_ago, current_date)
                if one_month_ago <= formatted_date <= current_date:
                    # print(" already applied")
                    response = jsonify({"message": "already_applied"})
                    response.status_code = 200
                    return response
                else:
                    # print("date not set")
                    apply = Emails_data(
                        sender_name=fname + " " + lname,
                        email=email,
                        phone_number=phone,
                        subject_part2=position,
                        formatted_date=current_datee,
                        file_name=filename,
                        file_content=content,
                        subject_part1="GeoxHR website ",
                        org_id=org_id,
                    )
                    db.session.add(apply)
                    db.session.commit()
                    response = jsonify({"message": "success"})
                    response.status_code = 200
                    return response

        else:
            # print("data not exist")
            apply = Emails_data(
                sender_name=fname + " " + lname,
                email=email,
                phone_number=phone,
                subject_part2=position,
                formatted_date=current_datee,
                file_name=filename,
                file_content=content,
                subject_part1="GeoxHR website ",
                org_id=org_id,
            )
            db.session.add(apply)
            db.session.commit()
            response = jsonify({"message": "success"})
            response.status_code = 200
            return response


@app.route("/handsapply", methods=["POST"])
def handsapply():
    if request.method == "POST":
        fname = request.form.get("firstName")
        lname = request.form.get("lastName")
        email = request.form.get("email")
        phone = request.form.get("number")
        position = request.form.get("position")
        file = request.files["myFile"]
        jobid = request.form.get("jobid")
        org_id = 1
        filename = file.filename
        if file and filename:  # Check if the file has a valid extension
            content = file.read()
        else:
            content = None
        current_datee = datetime.now().strftime("%a, %d %b %Y")
        exist = Emails_data.query.filter(
            and_(Emails_data.email == email, Emails_data.subject_part1 == position)
        ).all()

        current_date = datetime.now()
        one_month_ago = current_date - relativedelta(months=1)
        if exist:
            for check in exist:
                formatted_date = datetime.strptime(check.formatted_date, "%a, %d %b %Y")
                # print(formatted_date, one_month_ago, current_date)
                if one_month_ago <= formatted_date <= current_date:
                    # print(" already applied")
                    response = jsonify({"message": "already_applied"})
                    response.status_code = 200
                    return response
                else:
                    # print("date not set")
                    apply = Emails_data(
                        sender_name=fname + " " + lname,
                        email=email,
                        phone_number=phone,
                        subject_part2=position,
                        formatted_date=current_datee,
                        file_name=filename,
                        file_content=content,
                        subject_part1="HandsHR website ",
                        org_id=1,
                    )
                    db.session.add(apply)
                    db.session.commit()
                    response = jsonify({"message": "success"})
                    response.status_code = 200
                    return response

        else:
            # print("data not exist")
            apply = Emails_data(
                sender_name=fname + " " + lname,
                email=email,
                phone_number=phone,
                subject_part2=position,
                formatted_date=current_datee,
                file_name=filename,
                file_content=content,
                subject_part1="HandsHR website ",
                org_id=1,
            )
            db.session.add(apply)
            db.session.commit()
            response = jsonify({"message": "success"})
            response.status_code = 200
            return response


@app.route("/i8isapply", methods=["POST"])
def i8isapply():
    if request.method == "POST":
        fname = request.form.get("firstName")
        lname = request.form.get("lastName")
        email = request.form.get("email")
        phone = request.form.get("number")
        position = request.form.get("position")
        file = request.files["myFile"]
        jobid = request.form.get("jobid")
        org_id = 1
        filename = file.filename
        if file and filename:  # Check if the file has a valid extension
            content = file.read()
        else:
            content = None
        current_datee = datetime.now().strftime("%a, %d %b %Y")
        exist = Emails_data.query.filter(
            and_(Emails_data.email == email, Emails_data.subject_part1 == position)
        ).all()

        current_date = datetime.now()
        one_month_ago = current_date - relativedelta(months=1)
        if exist:
            for check in exist:
                formatted_date = datetime.strptime(check.formatted_date, "%a, %d %b %Y")
                # print(formatted_date, one_month_ago, current_date)
                if one_month_ago <= formatted_date <= current_date:
                    # print(" already applied")
                    response = jsonify({"message": "already_applied"})
                    response.status_code = 200
                    return response
                else:
                    # print("date not set")
                    apply = Emails_data(
                        sender_name=fname + " " + lname,
                        email=email,
                        phone_number=phone,
                        subject_part2=position,
                        formatted_date=current_datee,
                        file_name=filename,
                        file_content=content,
                        subject_part1="i8is website ",
                        org_id=org_id,
                    )
                    db.session.add(apply)
                    db.session.commit()
                    response = jsonify({"message": "success"})
                    response.status_code = 200
                    return response

        else:
            # print("data not exist")
            apply = Emails_data(
                sender_name=fname + " " + lname,
                email=email,
                phone_number=phone,
                subject_part2=position,
                formatted_date=current_datee,
                file_name=filename,
                file_content=content,
                subject_part1="i8is website ",
                org_id=org_id,
            )
            db.session.add(apply)
            db.session.commit()
            response = jsonify({"message": "success"})
            response.status_code = 200
            return response


@app.route("/signin")
def route_default():
    if "user_id" in session:
        user_id = request.cookies.get('user_id')
        role = request.cookies.get("role")
        email = session["email"]
        user = session["user"]
        org_id = request.cookies.get('org_id')

        return redirect(url_for("index"))
    return redirect(url_for("landing"))


@app.route("/", methods=["GET", "POST"])
def landing():
    email = request.args.get('email')
    password = request.args.get('password')

    if email and password:
        return redirect(url_for("login", email=email, password=password))

    return render_template("landing.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    return render_template("signup.html")


@app.route("/directlogin", methods=["GET", "POST"])
def directlogin():
    email = request.args.get('email')
    password = request.args.get('password')
    # print(email, password)

    if email and password:
        user = Users.query.filter_by(email=email).first()
        print(user)
        if user:
            if user.status == "Active" and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                # Successful login
                 # Set global variables
                # global global_user_id, global_role, global_org_id, global_user_name, global_user_email
                # global_user_id = user.id
                # global_role = user.role
                # global_org_id = user.org_id
                # global_user_name = f"{user.fname} {user.lname}"
                # global_user_email = user.email
                
                # session["user_id"] = user.id
                # session["role"] = user.role
                # session["org_id"] = user.org_id
                # session["email"] = user.email
                # session["org_name"] = user.org_name
                # session["user"] = f"{user.fname} {user.lname}"
                 # Set cookies
                 # Successful login
                login_user(user)
                resp = make_response(redirect(url_for("index")))
                resp.set_cookie('user_id', str(user.id), samesite='None', secure=True)  # Set secure=True if using HTTPS
                resp.set_cookie('role', user.role, samesite='None', secure=True)  # Set secure=True if using HTTPS
                resp.set_cookie('org_id', str(user.org_id), samesite='None', secure=True)  # Set secure=True if using HTTPS
                resp.set_cookie('email', str(user.email), samesite='None', secure=True)  # Set secure=True if using HTTPS
                resp.set_cookie('org_name', str(user.org_name), samesite='None', secure=True)  # Set secure=True if using HTTPS
                resp.set_cookie('user', str(f"{user.fname} {user.lname}"), samesite='None', secure=True)  # Set secure=True if using HTTPS

                return resp
            else:
                return jsonify({"message": "wrong credentials"}), 200
        else:
            return jsonify({"message": "User not found"}), 200
    else:
        return jsonify({"message": "User not found"}), 200


@app.route("/addorg", methods=["POST"])
def org():
    if request.method == "POST":
        company = request.form.get("company")
        com_email = request.form.get("com_email")
        email = request.form.get("email")
        com_number = request.form.get("com_number")
        num = request.form.get("num")  # Assuming this is phone_number

        # Check if any of the given fields already exist in the database
        existing_entry = (
            db.session.query(organization)
            .filter(
                or_(
                    organization.company == company,
                    organization.com_email == com_email,
                    organization.email == email,
                    organization.com_number == com_number,
                    organization.phone_number == num,
                )
            )
            .first()
        )
        # Check if any of the given fields already exist in the database
        existing_email = (
            db.session.query(Users)
            .filter(or_(Users.email == company, Users.email == email))
            .first()
        )
        # if existing_entry:
        #     if existing_entry.company == company:
        #         return jsonify({"error": "Company already exists"}), 400
        #     elif existing_entry.com_email == com_email:
        #         return jsonify({"error": "Company email already exists"}), 400
        #     elif existing_entry.email == email:
        #         return jsonify(
        #             {"error": "Contact person email already exists, choose another"}
        #         ), 400
        #     elif existing_entry.com_number == com_number:
        #         return jsonify({"error": "Company phone number already exists"}), 400
        #     elif existing_entry.phone_number == num:
        #         return jsonify(
        #             {
        #                 "error": "Contact person phone number already exists, choose another"
        #             }
        #         ), 400
        # if existing_email:
        #     if existing_email.email == com_email:
        #         return jsonify({"error": "Company email already exists"}), 400
        #     elif existing_email.email == email:
        #         return jsonify(
        #             {"error": "Contact person email already exists, choose another"}
        #         ), 400
        try:
            # No existing record found, proceed with creating a new entry
            lkd = True if request.form.get("lkd") == "1" else False
            zpr = True if request.form.get("zpr") == "2" else False
            com_web = request.form.get("com_web")
            com_address = request.form.get("com_address")
            nemp = request.form.get("nemp")
            fname = request.form.get("fname")
            lname = request.form.get("lname")
            status = "Approved"
            password = request.form.get("password")
            encpassword = sha256_crypt.encrypt(password)

            entry = organization(
                company=company,
                com_email=com_email,
                com_web=com_web,
                com_address=com_address,
                com_number=com_number,
                linkedin=lkd,
                ziprecuiter=zpr,
                num_employee=nemp,
                fname=fname,
                lname=lname,
                phone_number=num,
                email=email,
                password=encpassword,
                status=status,
            )
            # Commit the organization entry to the database
            db.session.add(entry)
            db.session.commit()

            usrentry = Users(
                    role="owner",
                    fname=fname,
                    lname=lname,
                    email=com_email,
                    password=encpassword,
                    designation="owner",
                    status="Active",
                    org_name=company,
                    org_id=entry.id,
                )
            db.session.add(usrentry)
                
            email_subject = f"""Registration Successfull"""
            print(email_subject)
            email_body = f"""
                                             <!DOCTYPE html>
                                             <html>
                                             <head>
                                                  <style>
                                                     body {{
                                                         font-family: Arial, sans-serif;
                                                     }}
                                                     .container {{
                                                         background-color: #f2f2f2;
                                                         padding: 20px;
                                                         border-radius: 10px;
                                                         max-width: 800px;
                                                         margin: auto;
                                                     }}
                                                     .cont-img{{
                                                         width: 34%;
                                                         margin: auto;
                                                         display: block;
                                                         margin-bottom:20px
                                                     }}
                                                     .details {{
                                                         margin-top: 10px;
                                                     }}
                                                     .details p {{
                                                         margin: 0;
                                                     }}
                                                     .bold {{
                                                         font-weight: bold;
                                                     }}
                                                     .signature {{
                                          margin-top: 20px;
                                          font-size:15px
                                      }}
                                      .signature p {{
                                            margin: 0px;
                                      }}
                                      .signature2 p {{
                                            margin: 0px;
                                            text-align: center;
                                      }}
                                      .hello{{
                                             border: 1px solid #19355f;
                                             margin-bottom: 28px;
                                      }}
                                      .signature2 {{
                                              padding: 7px;
                                              background: #ffff;
                                              margin-top: 21px;
                                      }}
                                                     .geoxhr {{
                                                            width: 100px;
                                                           margin-top: 10px;
                                                     }}
                                                 </style>
                                             </head>
                                             <body>
                                                 <div class="container">
                                                     <img class="cont-img" src="{{ url_for('static', filename='img/clickhr.png') }}">
                                                     <div class="hello"></div>

                                                     <p>We are thrilled to inform you that your registration has been successfully processed! Thank you for choosing to join our community.</p>
                                                     <p>Our team will now review your registration details and reach out to you shortly for any further information required to complete the process.</p>

                                                     <div class="signature">
                                          <p>Thankyou.</p>

                                       </div>
                                      <div class="signature2">
                                           <p>If assistance is required, feel free to reach out to us at:</p>
                                           <p>clickhr@click-hr.com.</p>
                                           <p> +1 647-930-0988</p>
                                      </div>
                                                 </div>
                                             </body>
                                             </html>
                                             """
            # recipients = [rcpt]
            recipients = ["nagina@i8is.com", com_email]

            # msg = Message(subject=email_subject, recipients=recipients, html=email_body)
            # mail.send(msg)
            # db.session.add(entry)
            db.session.commit()
    # Assuming the operation was successful
            response_data = {
                "success": True,
                "message": "Registered Successfully!",
                "data": None  # You can include any additional data here
            }
            return jsonify(response_data), 200
    
        except Exception as e:
            print("error",e)
            db.session.rollback()
            # response = jsonify({"error": f"Error signing up"})
            # # response = jsonify({'error': f'Error signing up: {str(e)}'})
            # response.status_code = 500
            # return response
            
            response_data = {
                "success": False,
                "message": "Registered failed!",
                "error": f'Error signing up: {str(e)}'
            }
            return jsonify(response_data), 500


@app.route("/privacypolicy", methods=["GET", "POST"])
def privacypolicy():
    return render_template("privacy.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if the user is already logged in
    if "user_id" in session:
        return redirect(url_for("index"))

    email = None
    password = None

    # Handle POST request
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

    # Handle GET request or fallback
    elif request.method == "GET":
        email = request.args.get('email')
        password = request.args.get('password')

    if email and password:
        # Locate user by email
        user = Users.query.filter_by(email=email).first()
        if user:
            if user.status == "Active":
                if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    # if user.status == "Active" and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):

                    # Successful login
                    login_user(user)
                    resp = make_response(redirect(url_for("index")))
                    resp.set_cookie('user_id', str(user.id), samesite='None', secure=True)  # Set secure=True if using HTTPS
                    resp.set_cookie('role', user.role, samesite='None', secure=True)  # Set secure=True if using HTTPS
                    resp.set_cookie('org_id', str(user.org_id), samesite='None', secure=True)  # Set secure=True if using HTTPS
                    resp.set_cookie('email', str(user.email), samesite='None', secure=True)  # Set secure=True if using HTTPS
                    resp.set_cookie('org_name', str(user.org_name), samesite='None', secure=True)  # Set secure=True if using HTTPS
                    resp.set_cookie('user', str(f"{user.fname} {user.lname}"), samesite='None', secure=True)  # Set secure=True if using HTTPS

                    return resp
                else:
                    return render_template("login.html", msg="Wrong email or password")
            else:
                return render_template("login.html", msg="Deactivated Account")
        else:
            return render_template("login.html", msg="User Not Found")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/logoutforcandidate")
def logoutforcandidate():
    session.clear()
    return redirect(url_for("logincandidate"))


engine = create_engine('mysql+pymysql://hayat:Hayat_admin123@35.183.134.169/Clickhrin')
# engine = create_engine("mysql+pymysql://hayat:Hayat_admin123@35.183.134.169/geoxhrdb")
# engine = create_engine('mysql+pymysql://root:@localhost/clickhrinfiniti')

# Create a session factory
Session = sessionmaker(bind=engine)


class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr)

    __setattr__ = dict.__setitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


@app.route("/index")
# @role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def index():
    
    user_idd = request.cookies.get('user_id')
    print("useris found in cookies", user_idd)
    # role = request.cookies.get("role")
    # org_id = request.cookies.get('org_id')
    # Access global variables instead of session variables
    user_id = request.cookies.get('user_id')
    role = request.cookies.get('role')
    org_id = request.cookies.get('org_id')
    session = {}
    session["user_id"] = user_id
    session["role"] = role
    session["org_id"] = org_id
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
  
    # print("org_id", org_id)
    allusers = Users.query.filter(Users.org_id == org_id).all()
    allusers_data = [
        {
            "id": user.id,
            "name": user.fname,
            "status": user.status,
            "created": user.created_at,
            "updated_at": user.updated_at,
        }
        for user in allusers
    ]

    placed = allforms_data.query.filter(
        allforms_data.status == "Candidate Placement", allforms_data.org_id == org_id
    ).all()
    placed_data = defaultdict(lambda: defaultdict(int))
    for place in placed:
        user_id = place.user_id
        created_at = place.created_at
        placed_data[user_id][created_at] += 1
    placed_data = [
        {
            "user_id": user_id,
            "placement_by_date": [
                {"date": date, "count": count} for date, count in data.items()
            ],
        }
        for user_id, data in placed_data.items()
    ]
    # print("placed_data",placed_data)
    resumes = allforms_data.query.filter(
        allforms_data.status == "Resume Sent", allforms_data.org_id == org_id
    ).all()
    resume_data = defaultdict(lambda: defaultdict(int))
    # print("resume_data",resume_data)
    for resume in resumes:
        user_id = resume.user_id
        created_at = resume.created_at
        # print("Debug - User ID:", user_id, ", Created At:", created_at, ", Type of Created At:", type(created_at))
        resume_data[user_id][created_at] += 1

    resume_data = [
        {
            "user_id": user_id,
            "resumes_by_date": [
                {"date": date, "count": count} for date, count in data.items()
            ],
        }
        for user_id, data in resume_data.items()
    ]

    interviews = allforms_data.query.filter(
        allforms_data.status == "Interview Scheduled", allforms_data.org_id == org_id
    ).all()
    interview_data = defaultdict(lambda: defaultdict(int))
    for interview in interviews:
        user_id = interview.user_id
        created_at = interview.created_at
        interview_data[user_id][created_at] += 1
    interview_data = [
        {
            "user_id": user_id,
            "interview_by_date": [
                {"date": date, "count": count} for date, count in data.items()
            ],
        }
        for user_id, data in interview_data.items()
    ]

    helps = allforms_data.query.filter(
        allforms_data.status == "Help Another", allforms_data.org_id == org_id
    ).all()
    help_data = defaultdict(lambda: defaultdict(int))
    for help in helps:
        user_id = help.user_id
        created_at = help.created_at
        help_data[user_id][created_at] += 1
    help_data = [
        {
            "user_id": user_id,
            "help_by_date": [
                {"date": date, "count": count} for date, count in data.items()
            ],
        }
        for user_id, data in help_data.items()
    ]

    signed = allforms_data.query.filter(
        allforms_data.status == "New deal opened and contract signed",
        allforms_data.org_id == org_id,
    ).all()
    signed_data = defaultdict(lambda: defaultdict(int))
    for sign in signed:
        user_id = sign.user_id
        created_at = sign.created_at
        signed_data[user_id][created_at] += 1
    signed_data = [
        {
            "user_id": user_id,
            "sign_by_date": [
                {"date": date, "count": count} for date, count in data.items()
            ],
        }
        for user_id, data in signed_data.items()
    ]

    notsigned = allforms_data.query.filter(
        allforms_data.status == "New deal and contract not signed",
        allforms_data.org_id == org_id,
    ).all()
    notsigned_data = defaultdict(lambda: defaultdict(int))
    for notsign in notsigned:
        user_id = notsign.user_id
        created_at = notsign.created_at
        notsigned_data[user_id][created_at] += 1
    notsigned_data = [
        {
            "user_id": user_id,
            "notsigned_by_date": [
                {"date": date, "count": count} for date, count in data.items()
            ],
        }
        for user_id, data in notsigned_data.items()
    ]

    reopened = allforms_data.query.filter(
        allforms_data.status == "Reopened deals", allforms_data.org_id == org_id
    ).all()
    reopen_data = defaultdict(lambda: defaultdict(int))
    for reopen in reopened:
        user_id = reopen.user_id
        created_at = reopen.created_at
        reopen_data[user_id][created_at] += 1
    reopen_data = [
        {
            "user_id": user_id,
            "reopen_by_date": [
                {"date": date, "count": count} for date, count in data.items()
            ],
        }
        for user_id, data in reopen_data.items()
    ]

    total_users = Users.query.filter(Users.org_id == org_id).count()
    totalcandidate = Emails_data.query.filter(
        Emails_data.action == "Interested", Emails_data.org_id == org_id
    ).count()
    action = "Interested"
    alldata = (
        Emails_data.query.filter(
            Emails_data.action == action, Emails_data.org_id == org_id
        )
        .order_by(desc(Emails_data.id))
        .all()
    )
    task = "default task value"  # Set a default value
    today = datetime.today()
    # print("today", today)
    days_to_saturday = today.weekday()
    saturday = today - timedelta(days=days_to_saturday)
    friday = saturday + timedelta(days=6)
    weekstart = saturday.strftime("%Y-%m-%d")
    weekend = friday.strftime("%Y-%m-%d")
    # print("Week start:", weekstart)
    # print("Week end:", weekend)
    # arc_mails_auto()
    if role == "user":
        totalforms = allforms_data.query.filter(
            allforms_data.user_id == user_id, allforms_data.org_id == org_id
        ).count()
        candidateplace = recruiting_data.query.filter(
            or_(
                recruiting_data.did_you == "Candidate Placement",
                recruiting_data.person_starting == "Candidate Placement",
                recruiting_data.org_id == org_id,
            ),
            recruiting_data.user_id == user_id,
        ).count()
    else:
        totalforms = allforms_data.query.filter(allforms_data.org_id == org_id).count()
        candidateplace = recruiting_data.query.filter(
            or_(
                recruiting_data.did_you == "Candidate Placement",
                recruiting_data.person_starting == "Candidate Placement",
                recruiting_data.org_id == org_id,
            )
        ).count()

        existing_entries = Targets.query.filter(
            and_(
                Targets.weekstart == weekstart,
                Targets.weekend == weekend,
                Targets.target != 0,
                Targets.org_id == org_id,
            )
        ).first()

        if existing_entries:
            pass
        else:
            task = "task not set"
            # print(role, "role", task)

    jobsorder = (
        db.session.query(Joborder)
        .filter(
            Joborder.archived == False,
            Joborder.jobstatus == "active",
            Joborder.org_id == org_id,
        )
        .order_by(desc(Joborder.id))
        .all()
    )
    marketing_entries = (
        db.session.query(Marketing).filter(Marketing.org_id == org_id).all()
    )
    company_name_dict = {entry.id: entry.company for entry in marketing_entries}
    for job_order in jobsorder:
        company_id = job_order.company_id
        if company_id in company_name_dict:
            job_order.company = company_name_dict[company_id]
    data_array = DotDict(
        {
            "counters": {
                "total_users": total_users,
                "totalcandidate": totalcandidate,
                "totalforms": totalforms,
                "candidateplace": candidateplace,
            }
        }
    )
    # user_id = request.cookies.get('user_id')
    # role = request.cookies.get("role")
# Access global variables instead of session variables
    user_id = global_user_id
    role = global_role
    
    if role == "user":
        members_data = (
            Targets.query.filter(
                Targets.user_id == user_id,
                Targets.weekstart == weekstart,
                Targets.org_id == org_id,
            )
            .order_by(desc(Targets.id))
            .all()
        )
    else:
        # print(weekstart)
        members_data = (
            Targets.query.filter(
                Targets.weekstart == weekstart, Targets.org_id == org_id
            )
            .order_by(desc(Targets.id))
            .all()
        )
    for member in members_data:
        print(member.new_achieve, "members_data")
    return render_template(
        "index.html",
        sign=signed_data,
        notsign=notsigned_data,
        reopen=reopen_data,
        resumes=resume_data,
        interviews=interview_data,
        helps=help_data,
        placed=placed_data,
        allusers=allusers_data,
        data_array=data_array,
        jobsorder=jobsorder,
        alldata=alldata,
        weekstart=weekstart,
        weekend=weekend,
        msg=task,
        members_data=members_data,
        session= session
    )


country_prefixes = {
    "canada": [
        "+1",
        "647",
        "622",
        "1",
        "403",
        "587",
        "825",
        "368",
        "780",
        "604",
        "778",
        "236",
        "672",
        "250",
        "204",
        "289",
    ],
    "pakistan": ["+92", "03", "92"],
    "india": ["+91", "91"],
    "mexico": ["+52-187", "+52-800", "52-187", "52-800", "52-187", "+52", "52"],
    "philippines": ["+63-999", "+63-001", "63-001", "63-999", "+63", "63"],
    "united states": [
        "+1",
        "18",
        "1800",
        "1888",
        "1877",
        "1866",
        "1855",
        "1844",
        "1800",
        "1888",
        "+1-877",
        "+1-866",
        "+1-855",
        "+1-844",
    ],
}


phone_codes = {
    "AF": "+93",
    "AO": "+244",
    "AI": "+1-264",
    "AX": "+358",
    "AL": "+355",
    "AD": "+376",
    "AE": "+971",
    "AR": "+54",
    "AM": "+374",
    "AS": "+1-684",
    "TF": "+262",
    "AG": "+1-268",
    "AT": "+43",
    "AZ": "+994",
    "BI": "+257",
    "BE": "+32",
    "BJ": "+229",
    "BQ": "+599",
    "BF": "+226",
    "BD": "+880",
    "BG": "+359",
    "BH": "+973",
    "BS": "+1-242",
    "BA": "+387",
    "BL": "+590",
    "BZ": "+501",
    "BM": "+1-441",
    "BO": "+591",
    "BR": "+55",
    "BB": "+1-246",
    "BN": "+673",
    "BT": "+975",
    "BW": "+267",
    "CFR": "+236",  # Central African Republic
    "CAN": "+1",  # Canada
    "CCK": "+61",  # Cocos(Keeling) Islands
    "CH": "+41",  # Switzerland
    "CL": "+56",  # Chile
    "CN": "+86",  # China
    "CM": "+237",  # Cameroon
    "CD": "+243",  # Congo, The Democratic Republic of the
    "CG": "+242",  # Congo
    "CK": "+682",  # Cook Islands
    "CO": "+57",  # Colombia
    "KM": "+269",  # Comoros
    "CV": "+238",  # Cabo Verde(Cape Verde)
    "CR": "+506",  # Costa Rica
    "CU": "+53",  # Cuba
    "CW": "+599",  # Curaçao
    "CX": "+61",  # Christmas Island
    "KY": "+1-345",  # Cayman Islands
    "CY": "+357",  # Cyprus
    "CZ": "+420",  # Czechia(Czech Republic)
    "DEU": "+49",  # Germany
    "DJ": "+253",  # Djibouti
    "DM": "+1-767",  # Dominica
    "DK": "+45",  # Denmark
    "DO": "+1-809",  # Dominican Republic (and +1-829 and +1-849)
    "DZ": "+213",  # Algeria
    "EC": "+593",  # Ecuador
    "EG": "+20",  # Egypt
    "ER": "+291",  # Eritrea
    "EH": "+212",  # Western Sahara
    "ES": "+34",  # Spain
    "EE": "+372",  # Estonia
    "ET": "+251",  # Ethiopia
    "FI": "+358",  # Finland
    "FJ": "+679",  # Fiji
    "FK": "+500",  # Falkland Islands (Malvinas)
    "FR": "+33",  # France
    "FO": "+298",  # Faroe Islands
    "FM": "+691",  # Micronesia, Federated States of
    "GA": "+241",  # Gabon
    "GB": "+44",  # United Kingdom
    "GE": "+995",  # Georgia
    "GG": "+44-1481",  # Guernsey
    "GH": "+233",  # Ghana
    "GI": "+350",  # Gibraltar
    "GN": "+224",  # Guinea
    "GP": "+590",  # Guadeloupe
    "GM": "+220",  # Gambia
    "GW": "+245",  # Guinea-Bissau
    "GQ": "+240",  # Equatorial Guinea
    "GR": "+30",  # Greece
    "GD": "+1-473",  # Grenada
    "GL": "+299",  # Greenland
    "GT": "+502",  # Guatemala
    "GF": "+594",  # French Guiana
    "GU": "+1-671",  # Guam
    "GY": "+592",  # Guyana
    "HK": "+852",  # Hong Kong
    "HM": "",  # Heard Island and McDonald Islands: No specific dialing code; Australian external territory
    "HN": "+504",  # Honduras
    "HR": "+385",  # Croatia
    "HT": "+509",  # Haiti
    "HU": "+36",  # Hungary
    "ID": "+62",  # Indonesia
    "IM": "+44-1624",  # Isle of Man
    "IN": "+91",  # India
    "IO": "+246",  # British Indian Ocean Territory
    "IE": "+353",  # Ireland
    "IR": "+98",  # Iran, Islamic Republic of
    "IQ": "+964",  # Iraq
    "IS": "+354",  # Iceland
    "IL": "+972",  # Israel
    "IT": "+39",  # Italy
    "JM": "+1-876",  # Jamaica
    "JE": "+44-1534",  # Jersey
    "JO": "+962",  # Jordan
    "JP": "+81",  # Japan
    "KZ": "+7",  # Kazakhstan
    "KE": "+254",  # Kenya
    "KG": "+996",  # Kyrgyzstan
    "KH": "+855",  # Cambodia
    "KI": "+686",  # Kiribati
    "KN": "+1-869",  # Saint Kitts and Nevis
    "KR": "+82",  # Korea, Republic of
    "KW": "+965",  # Kuwait
    "LA": "+856",  # Lao People's Democratic Republic
    "LB": "+961",  # Lebanon
    "LR": "+231",  # Liberia
    "LY": "+218",  # Libya
    "LC": "+1-758",  # Saint Lucia
    "LI": "+423",  # Liechtenstein
    "LK": "+94",  # Sri Lanka
    "LS": "+266",  # Lesotho
    "LT": "+370",  # Lithuania
    "LU": "+352",  # Luxembourg
    "LV": "+371",  # Latvia
    "MO": "+853",  # Macao
    "MF": "+590",  # Saint Martin (French part)
    "MA": "+212",  # Morocco
    "MC": "+377",  # Monaco
    "MD": "+373",  # Moldova, Republic of
    "MG": "+261",  # Madagascar
    "MV": "+960",  # Maldives
    "MX": "+52",  # Mexico
    "MH": "+692",  # Marshall Islands
    "MK": "+389",  # North Macedonia
    "ML": "+223",  # Mali
    "MT": "+356",  # Malta
    "MM": "+95",  # Myanmar
    "ME": "+382",  # Montenegro
    "MN": "+976",  # Mongolia
    "MP": "+1-670",  # Northern Mariana Islands
    "MZ": "+258",  # Mozambique
    "MR": "+222",  # Mauritania
    "MS": "+1-664",  # Montserrat
    "MQ": "+596",  # Martinique
    "MU": "+230",  # Mauritius
    "MW": "+265",  # Malawi
    "MY": "+60",  # Malaysia
    "YT": "+262",  # Mayotte
    "NA": "+264",  # Namibia
    "NC": "+687",  # New Caledonia
    "NE": "+227",  # Niger
    "NF": "+672",  # Norfolk Island
    "NG": "+234",  # Nigeria
    "NI": "+505",  # Nicaragua
    "NU": "+683",  # Niue
    "NL": "+31",  # Netherlands
    "NO": "+47",  # Norway
    "NP": "+977",  # Nepal
    "NR": "+674",  # Nauru
    "NZ": "+64",  # New Zealand
    "OM": "+968",  # Oman
    "PK": "+92",  # Pakistan
    "PA": "+507",  # Panama
    "PN": "+64",  # Pitcairn
    "PE": "+51",  # Peru
    "PH": "+63",  # Philippines
    "PW": "+680",  # Palau
    "PG": "+675",  # Papua New Guinea
    "PL": "+48",  # Poland
    "PR": "+1-787",  # Puerto Rico
    "KP": "+850",  # Korea, Democratic People's Republic of
    "PT": "+351",  # Portugal
    "PY": "+595",  # Paraguay
    "PS": "+970",  # Palestine, State of
    "PF": "+689",  # French Polynesia
    "QA": "+974",  # Qatar
    "RE": "+262",  # Réunion
    "RO": "+40",  # Romania
    "RU": "+7",  # Russian Federation
    "RW": "+250",  # Rwanda
    "SA": "+966",  # Saudi Arabia
    "SD": "+249",  # Sudan
    "SN": "+221",  # Senegal
    "GS": "",  # South Georgia and the South Sandwich Islands
    "SH": "+290",  # Saint Helena, Ascension and Tristan da Cunha
    "SJ": "+47",  # Svalbard and Jan Mayen
    "SB": "+677",  # Solomon Islands
    "SL": "+232",  # Sierra Leone
    "SV": "+503",  # El Salvador
    "SM": "+378",  # San Marino
    "SO": "+252",  # Somalia
    "PM": "+508",  # Saint Pierre and Miquelon
    "RS": "+381",  # Serbia
    "SS": "+211",  # South Sudan
    "ST": "+239",  # Sao Tome and Principe
    "SR": "+597",  # Suriname
    "SK": "+421",  # Slovakia
    "SI": "+386",  # Slovenia
    "SE": "+46",  # Sweden
    "SZ": "+268",  # Eswatini
    "SX": "+1-721",  # Sint Maarten (Dutch part)
    "SC": "+248",  # Seychelles
    "SY": "+963",  # Syrian Arab Republic
    "TC": "+1-649",  # Turks and Caicos Islands
    "TD": "+235",  # Chad
    "TG": "+228",  # Togo
    "TH": "+66",  # Thailand
    "TJ": "+992",  # Tajikistan
    "TK": "+690",  # Tokelau
    "TM": "+993",  # Turkmenistan
    "TL": "+670",  # Timor-Leste
    "TO": "+676",  # Tonga
    "TT": "+1-868",  # Trinidad and Tobago
    "TN": "+216",  # Tunisia
    "TR": "+90",  # Turkey
    "TV": "+688",  # Tuvalu
    "TW": "+886",  # Taiwan, Province of China
    "TZ": "+255",  # Tanzania, United Republic of
    "UG": "+256",  # Uganda
    "UA": "+380",  # Ukraine
    "UM": "",  # United States Minor Outlying Islands
    "UY": "+598",  # Uruguay
    "UZ": "+998",  # Uzbekistan
    "VA": "+39",  # Holy See (Vatican City State)
    "VC": "+1-784",  # Saint Vincent and the Grenadines
    "VE": "+58",  # Venezuela, Bolivarian Republic of
    "VG": "+1-284",  # Virgin Islands, British
    "VI": "+1-340",  # Virgin Islands,U.S.
    "VN": "+84",  # Viet Nam
    "VU": "+678",  # Vanuatu
    "WF": "+681",  # Wallis and Futuna
    "WS": "+685",  # Samoa
    "YE": "+967",  # Yemen
    "ZA": "+27",  # South Africa
    "ZM": "+260",  # Zambia
    "ZW": "+263",  # Zimbabwe
    "AW": "+297",
    "AQ": "+672",
    "AU": "+61",
    "BY": "+375",
    "BV": "0055",
    "CF": "+236",
    "CA": "+1",
    "CC": "+61",
    "CI": "+225",
    "DE": "Germany",
    "US": "+1",
    "SG": "+65",
    # Add more country codes as needed
}
all_countries = list(pycountry.countries)
for country in all_countries:
    alpha2_code = country.alpha_2
    country_name = country.name
    phone_code = phone_codes.get(alpha2_code, "N/A")


@app.route("/candidate")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def candidate():
    org_id = request.cookies.get('org_id')
    print("canorg_id", org_id)
    selected_year = request.args.get("year_select")
    selected_country = request.args.get("country_select")
    selected_subject = request.args.get("subj_select")
    prev_form = request.args.get("prev_form")
    source = request.args.get("source")
    keyword = request.args.get("keyword")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))
    print(
        selected_year,
        selected_country,
        selected_subject,
        page,
        per_page,
        prev_form,
        source,
    )
    action = "Interested"
    status = "Candidate Placement"
    status1 = "applied"
    current_year = datetime.now().year

    with db.session() as db_session:
        query = db_session.query(Emails_data).filter(Emails_data.org_id == org_id)

        if action:
            query = query.filter(Emails_data.action != action)
        if status:
            query = query.filter(Emails_data.status != status)

        query = query.order_by(desc(Emails_data.id))
        if selected_year and selected_year != "":
            query = query.filter(Emails_data.formatted_date.ilike(f"%{selected_year}%"))
            print(f"Applying year filter: {selected_year}")
        else:
            query = query.filter(Emails_data.formatted_date.ilike(f"%{current_year}%"))
            print(f"Applying default year filter: {current_year}")
        if selected_subject and selected_subject != "":
            query = query.filter(
                Emails_data.subject_part2.ilike(f"%{selected_subject}%")
            )
            print(f"Applying subject filter: {selected_subject}")
        if source and source != "":
            query = query.filter(Emails_data.subject_part1.ilike(f"%{source}%"))
            print(f"Applying subject filter: {source}")
        if prev_form and prev_form != "":
            candidate_query = db_session.query(recruiting_data).filter(
                and_(
                    recruiting_data.candidate == Emails_data.sender_name,
                    recruiting_data.org_id == org_id,
                    recruiting_data.did_you == prev_form,
                )
            )
            matched_sender_names = [
                candidate.candidate for candidate in candidate_query
            ]
            query = query.filter(Emails_data.sender_name.in_(matched_sender_names))
            print(f"Applying filter based on prev_form: {prev_form}")
        if keyword:
            keyword_lower = keyword.lower()
            query = query.filter(
                or_(
                    Emails_data.sender_name.ilike(f"%{keyword_lower}%"),
                    Emails_data.email.ilike(f"%{keyword_lower}%"),
                    Emails_data.subject_part1.ilike(f"%{keyword_lower}%"),
                    Emails_data.subject_part2.ilike(f"%{keyword_lower}%"),
                )
            )
            results = query.all()
            if not results:
                for email in Emails_data.query.all():
                    pdf_content_json = email.pdf_content_json
                    if pdf_content_json:
                        pdf_data_dict = json.loads(pdf_content_json)
                        pdf_data_json_lower = json.dumps(pdf_data_dict).lower()
                        if keyword_lower in pdf_data_json_lower:
                            results.append(email)
        if selected_country and selected_country.strip().lower() in country_prefixes:
            print(f"Applying country filter for: {selected_country}")
            prefixes = country_prefixes[selected_country.strip().lower()]
            print(f"Prefixes for {selected_country}: {prefixes}")
            country_prefix_conditions = or_(
                *[
                    func.substr(Emails_data.phone_number, 1, len(prefix)) == prefix
                    for prefix in prefixes
                ]
            )
            print(f"Country prefix conditions: {country_prefix_conditions}")
            query = query.filter(country_prefix_conditions)
            print(f"Applied country filter for: {selected_country}")
        else:
            selected_country = ""
        total_items = query.count()
        total_pages = ceil(total_items / per_page)
        paginated_data = query.paginate(page=page, per_page=per_page)
        alldata = paginated_data.items
        print(total_items, total_pages)
        serialized_alldata = []
        if alldata:
            print("Data found after filtering:")
            serialized_alldata = [
                {
                    "id": email.id,
                    "email": email.email,
                    "sender_name": email.sender_name,
                    "subject_part1": email.subject_part1,
                    "subject_part2": email.subject_part2,
                    "formatted_date": email.formatted_date,
                    "pdf_content_json": base64.b64encode(
                        email.pdf_content_json.encode("utf-8")
                    ).decode("utf-8")
                    if isinstance(email.pdf_content_json, str)
                    else None,
                    "phone_number": email.phone_number,
                    "file_content": base64.b64encode(email.file_content).decode("utf-8")
                    if email.file_content
                    else None,
                    "status": email.status,
                    "action": email.action,
                }
                for email in alldata
            ]
        else:
            print("No data found after filtering.")

    unique_subjects = (
        db.session.query(
            distinct(Emails_data.subject_part2),
            Emails_data.id,
            Emails_data.subject_part1,
        )
        .filter(Emails_data.org_id == org_id)
        .order_by(desc(Emails_data.id))
        .all()
    )
    unique_lines_set = set()

    for subject_tuple in unique_subjects:
        subject_line = subject_tuple[0]
        subject_part1 = subject_tuple[2]

        if (
            subject_part1.strip() == "HandsHR website"
            or subject_part1 == "GeoxHR website"
            or subject_part1 == "manually"
            or subject_part1 == "registered from Geox hr"
        ):
            unique_lines_set.add(subject_line)

        if " for " in subject_line and " applied for " in subject_line:
            after_for = subject_line.split(" for ", 1)[1].strip()
            unique_lines_set.add(after_for)

    unique_lines = sorted(list(unique_lines_set))
    candidatehistory = (
        db.session.query(candidate_history)
        .filter(candidate_history.org_id == org_id)
        .order_by(desc(candidate_history.id))
        .all()
    )
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        filtered_data_html = render_template(
            "candidates.html",
            alldata=serialized_alldata,
            all_countries=all_countries,
            phone_codes=phone_codes,
            unique_lines=unique_lines,
            selected_year=selected_year,
            selected_country=selected_country,
            selected_subject=selected_subject,
            total_pages=total_pages,
            candidatehistory=candidatehistory,
        )
        return jsonify(
            {
                "html": filtered_data_html,
                "alldata": serialized_alldata,
                "total_pages": total_pages,
            }
        )
    else:
        # If regular request, render the template
        return render_template(
            "candidates.html",
            alldata=alldata,
            all_countries=all_countries,
            phone_codes=phone_codes,
            unique_lines=unique_lines,
            total_pages=total_pages,
            candidatehistory=candidatehistory,
        )  # Pass total_pages to the template


@app.route("/selecteddata")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def selecteddata():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    selected_year = request.args.get("year_select")
    selected_country = request.args.get("country_select")
    selected_subject = request.args.get("subj_select")
    prev_form = request.args.get("prev_form")
    source = request.args.get("source")
    keyword = request.args.get("keyword")
    page = int(request.args.get("page", 1))  # Get page number, default to 1
    per_page = int(request.args.get("per_page", 70))  # Get items per page, default to 5
    # Get items per page, default to 5
    print(selected_year, selected_country, selected_subject, page, per_page, prev_form)
    action = "Interested"
    status = "Candidate Placement"
    status1 = "Reject"
    current_year = datetime.now().year  # Get the current year

    with db.session() as db_session:
        query = db_session.query(Emails_data).filter(Emails_data.org_id == org_id)
        if action:
            query = query.filter(Emails_data.action == action)
        if status:
            query = query.filter(Emails_data.status != status)
        if status:
            query = query.filter(Emails_data.status != status1)

        query = query.order_by(desc(Emails_data.id))
        # Apply year filter if selected_year is provided, else default to current year
        if selected_year and selected_year != "":
            # Filter by selected year
            query = query.filter(Emails_data.formatted_date.ilike(f"%{selected_year}%"))
            print(f"Applying year filter: {selected_year}")
        else:
            query = query.filter(Emails_data.formatted_date.ilike(f"%{current_year}%"))
            print(f"Applying default year filter: {current_year}")

        # Apply subject filter if selected_subject is provided
        if selected_subject and selected_subject != "":
            query = query.filter(
                Emails_data.subject_part2.ilike(f"%{selected_subject}%")
            )
            print(f"Applying subject filter: {selected_subject}")
        if source and source != "":
            query = query.filter(Emails_data.subject_part1.ilike(f"%{source}%"))
            print(f"Applying subject filter: {source}")
        if prev_form and prev_form != "":
            candidate_query = db_session.query(recruiting_data).filter(
                and_(
                    recruiting_data.candidate == Emails_data.sender_name,
                    recruiting_data.did_you == prev_form,
                    recruiting_data.org_id == org_id,
                )
            )
            matched_sender_names = [
                candidate.candidate for candidate in candidate_query
            ]
            query = query.filter(Emails_data.sender_name.in_(matched_sender_names))
            print(f"Applying filter based on prev_form: {prev_form}")
        # Apply country filter if selected_country is provided
        # Inside the 'with db.session() as session:' block
        if keyword:
            keyword_lower = keyword.lower()
            query = query.filter(
                or_(
                    Emails_data.sender_name.ilike(f"%{keyword_lower}%"),
                    Emails_data.email.ilike(f"%{keyword_lower}%"),
                    Emails_data.subject_part1.ilike(f"%{keyword_lower}%"),
                    Emails_data.subject_part2.ilike(f"%{keyword_lower}%"),
                )
            )
            results = query.all()
            if not results:
                for email in Emails_data.query.all():
                    pdf_content_json = email.pdf_content_json
                    if pdf_content_json:
                        pdf_data_dict = json.loads(pdf_content_json)
                        pdf_data_json_lower = json.dumps(pdf_data_dict).lower()
                        if keyword_lower in pdf_data_json_lower:
                            results.append(email)
        # Apply country filter if selected_country is provided
        if selected_country and selected_country.strip().lower() in country_prefixes:
            print(f"Applying country filter for: {selected_country}")
            prefixes = country_prefixes[selected_country.strip().lower()]
            print(f"Prefixes for {selected_country}: {prefixes}")
            # Construct OR condition for country prefixes
            country_prefix_conditions = or_(
                *[
                    func.substr(Emails_data.phone_number, 1, len(prefix)) == prefix
                    for prefix in prefixes
                ]
            )
            print(f"Country prefix conditions: {country_prefix_conditions}")
            query = query.filter(country_prefix_conditions)
            print(f"Applied country filter for: {selected_country}")
        else:
            selected_country = ""

            # Count total number of pages
        total_items = query.count()
        total_pages = ceil(total_items / per_page)

        # Paginate the query results
        paginated_data = query.paginate(page=page, per_page=per_page)
        alldata = paginated_data.items  # Extract the items from the paginated object
        print(total_items, total_pages)
        serialized_alldata = []  # Initialize list to store serialized data

        # Serialize the data
        if alldata:
            print("Data found after filtering:")
            serialized_alldata = [
                {
                    "id": email.id,
                    "email": email.email,
                    "sender_name": email.sender_name,
                    "subject_part1": email.subject_part1,
                    "subject_part2": email.subject_part2,
                    "formatted_date": email.formatted_date,
                    "pdf_content_json": base64.b64encode(
                        email.pdf_content_json.encode("utf-8")
                    ).decode("utf-8")
                    if isinstance(email.pdf_content_json, str)
                    else None,
                    "phone_number": email.phone_number,
                    "file_content": base64.b64encode(email.file_content).decode("utf-8")
                    if email.file_content
                    else None,
                    "status": email.status,
                    "action": email.action,
                }
                for email in alldata
            ]
        else:
            print("No data found after filtering.")
    unique_subjects = (
        db.session.query(
            distinct(Emails_data.subject_part2),
            Emails_data.id,
            Emails_data.subject_part1,
        )
        .filter(Emails_data.org_id == org_id)
        .order_by(desc(Emails_data.id))
        .all()
    )
    unique_lines_set = set()

    for subject_tuple in unique_subjects:
        subject_line = subject_tuple[0]
        subject_part1 = subject_tuple[2]

        # Check if subject_part1 is equal to 'HandsHR website'
        if (
            subject_part1.strip() == "HandsHR website"
            or subject_part1 == "GeoxHR website"
        ):
            # Ensure to strip whitespace
            unique_lines_set.add(subject_line)

        # Check for "for" and "applied for" in subject_line
        if " for " in subject_line and " applied for " in subject_line:
            after_for = subject_line.split(" for ", 1)[1].strip()
            unique_lines_set.add(after_for)

    unique_lines = sorted(list(unique_lines_set))
    # print(unique_lines)
    candidatehistory = (
        db.session.query(candidate_history)
        .filter(candidate_history.org_id == org_id)
        .order_by(desc(candidate_history.id))
        .all()
    )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # If AJAX request, return JSON response
        filtered_data_html = render_template(
            "candidates.html",
            alldata=serialized_alldata,
            all_countries=all_countries,
            phone_codes=phone_codes,
            unique_lines=unique_lines,
            selected_year=selected_year,
            selected_country=selected_country,
            selected_subject=selected_subject,
            total_pages=total_pages,
            candidatehistory=candidatehistory,
        )  # Pass total_pages to the template
        return jsonify(
            {
                "html": filtered_data_html,
                "alldata": serialized_alldata,
                "total_pages": total_pages,
            }
        )
    else:
        # If regular request, render the template
        return render_template(
            "candidates.html",
            alldata=alldata,
            all_countries=all_countries,
            phone_codes=phone_codes,
            unique_lines=unique_lines,
            total_pages=total_pages,
            candidatehistory=candidatehistory,
        )  # Pass total_pages to the template


@app.route("/placedcandidates")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def placedcandidates():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    selected_year = request.args.get("year_select")
    selected_country = request.args.get("country_select")
    selected_subject = request.args.get("subj_select")
    prev_form = request.args.get("prev_form")
    source = request.args.get("source")
    keyword = request.args.get("keyword")
    page = int(request.args.get("page", 1))  # Get page number, default to 1
    per_page = int(request.args.get("per_page", 70))  # Get items per page, default to 5
    # Get items per page, default to 5
    print(selected_year, selected_country, selected_subject, page, per_page, prev_form)
    status = "Candidate Placement"
    action = ""
    current_year = datetime.now().year  # Get the current year

    with db.session() as db_session:
        query = db_session.query(Emails_data).filter(Emails_data.org_id == org_id)

        if action:
            query = query.filter(Emails_data.action != action)
        if status:
            query = query.filter(Emails_data.status == status)

        query = query.order_by(desc(Emails_data.id))

        if selected_year and selected_year != "":
            # Filter by selected year
            query = query.filter(Emails_data.formatted_date.ilike(f"%{selected_year}%"))
            print(f"Applying year filter: {selected_year}")
        else:
            query = query.filter(Emails_data.formatted_date.ilike(f"%{current_year}%"))
            print(f"Applying default year filter: {current_year}")

        # Apply subject filter if selected_subject is provided
        if selected_subject and selected_subject != "":
            query = query.filter(
                Emails_data.subject_part2.ilike(f"%{selected_subject}%")
            )
            print(f"Applying subject filter: {selected_subject}")
        if source and source != "":
            query = query.filter(Emails_data.subject_part1.ilike(f"%{source}%"))
            print(f"Applying subject filter: {source}")
        if prev_form and prev_form != "":
            candidate_query = db_session.query(recruiting_data).filter(
                and_(
                    recruiting_data.candidate == Emails_data.sender_name,
                    recruiting_data.did_you == prev_form,
                    recruiting_data.org_id == org_id,
                )
            )
            matched_sender_names = [
                candidate.candidate for candidate in candidate_query
            ]
            query = query.filter(Emails_data.sender_name.in_(matched_sender_names))
            print(f"Applying filter based on prev_form: {prev_form}")
        if keyword:
            keyword_lower = keyword.lower()
            query = query.filter(
                or_(
                    Emails_data.sender_name.ilike(f"%{keyword_lower}%"),
                    Emails_data.email.ilike(f"%{keyword_lower}%"),
                    Emails_data.subject_part1.ilike(f"%{keyword_lower}%"),
                    Emails_data.subject_part2.ilike(f"%{keyword_lower}%"),
                )
            )
            results = query.all()
            if not results:
                for email in Emails_data.query.all():
                    pdf_content_json = email.pdf_content_json
                    if pdf_content_json:
                        pdf_data_dict = json.loads(pdf_content_json)
                        pdf_data_json_lower = json.dumps(pdf_data_dict).lower()
                        if keyword_lower in pdf_data_json_lower:
                            results.append(email)
        # Apply country filter if selected_country is provided
        if selected_country and selected_country.strip().lower() in country_prefixes:
            print(f"Applying country filter for: {selected_country}")
            prefixes = country_prefixes[selected_country.strip().lower()]
            print(f"Prefixes for {selected_country}: {prefixes}")
            # Construct OR condition for country prefixes
            country_prefix_conditions = or_(
                *[
                    func.substr(Emails_data.phone_number, 1, len(prefix)) == prefix
                    for prefix in prefixes
                ]
            )
            print(f"Country prefix conditions: {country_prefix_conditions}")
            query = query.filter(country_prefix_conditions)
            print(f"Applied country filter for: {selected_country}")
        else:
            selected_country = ""

            # Count total number of pages
        total_items = query.count()
        total_pages = ceil(total_items / per_page)

        # Paginate the query results
        paginated_data = query.paginate(page=page, per_page=per_page)
        alldata = paginated_data.items  # Extract the items from the paginated object
        print(total_items, total_pages)
        serialized_alldata = []  # Initialize list to store serialized data

        # Serialize the data
        if alldata:
            print("Data found after filtering:")
            serialized_alldata = [
                {
                    "id": email.id,
                    "email": email.email,
                    "sender_name": email.sender_name,
                    "subject_part1": email.subject_part1,
                    "subject_part2": email.subject_part2,
                    "formatted_date": email.formatted_date,
                    "pdf_content_json": base64.b64encode(
                        email.pdf_content_json.encode("utf-8")
                    ).decode("utf-8")
                    if isinstance(email.pdf_content_json, str)
                    else None,
                    "phone_number": email.phone_number,
                    "file_content": base64.b64encode(email.file_content).decode("utf-8")
                    if email.file_content
                    else None,
                    "status": email.status,
                    "action": email.action,
                }
                for email in alldata
            ]
        else:
            print("No data found after filtering.")

    unique_subjects = (
        db.session.query(
            distinct(Emails_data.subject_part2),
            Emails_data.id,
            Emails_data.subject_part1,
        )
        .filter(Emails_data.org_id == org_id)
        .order_by(desc(Emails_data.id))
        .all()
    )
    unique_lines_set = set()

    for subject_tuple in unique_subjects:
        subject_line = subject_tuple[0]
        subject_part1 = subject_tuple[2]

        if (
            subject_part1.strip() == "HandsHR website"
            or subject_part1 == "GeoxHR website"
            or subject_part1 == "manually"
            or subject_part1 == "registered from Geox hr"
        ):
            unique_lines_set.add(subject_line)

        if " for " in subject_line and " applied for " in subject_line:
            after_for = subject_line.split(" for ", 1)[1].strip()
            unique_lines_set.add(after_for)

    unique_lines = sorted(list(unique_lines_set))
    candidatehistory = (
        db.session.query(candidate_history)
        .filter(candidate_history.org_id == org_id)
        .order_by(desc(candidate_history.id))
        .all()
    )

    # Check if the request is AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # If AJAX request, return JSON response
        filtered_data_html = render_template(
            "candidates.html",
            alldata=serialized_alldata,
            all_countries=all_countries,
            phone_codes=phone_codes,
            unique_lines=unique_lines,
            selected_year=selected_year,
            selected_country=selected_country,
            selected_subject=selected_subject,
            total_pages=total_pages,
            candidatehistory=candidatehistory,
        )  # Pass total_pages to the template
        return jsonify(
            {
                "html": filtered_data_html,
                "alldata": serialized_alldata,
                "total_pages": total_pages,
            }
        )
    else:
        # If regular request, render the template
        return render_template(
            "candidates.html",
            alldata=alldata,
            all_countries=all_countries,
            phone_codes=phone_codes,
            unique_lines=unique_lines,
            total_pages=total_pages,
            candidatehistory=candidatehistory,
        )  # Pass total_pages to the template


@app.route("/rejectcandidates")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def rejectcandidates():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    selected_year = request.args.get("year_select")
    selected_country = request.args.get("country_select")
    selected_subject = request.args.get("subj_select")
    prev_form = request.args.get("prev_form")
    source = request.args.get("source")
    keyword = request.args.get("keyword")
    page = int(request.args.get("page", 1))  # Get page number, default to 1
    per_page = int(request.args.get("per_page", 70))  # Get items per page, default to 5
    # Get items per page, default to 5
    print(selected_year, selected_country, selected_subject, page, per_page, prev_form)
    status = "Reject"
    action = ""
    current_year = datetime.now().year  # Get the current year

    with db.session() as db_session:
        query = db_session.query(Emails_data).filter(Emails_data.org_id == org_id)

        if action:
            query = query.filter(Emails_data.action != action)
        if status:
            query = query.filter(Emails_data.status == status)

        query = query.order_by(desc(Emails_data.id))
        # Apply year filter if selected_year is provided, else default to current year
        if selected_year and selected_year != "":
            # Filter by selected year
            query = query.filter(Emails_data.formatted_date.ilike(f"%{selected_year}%"))
            print(f"Applying year filter: {selected_year}")
        else:
            query = query.filter(Emails_data.formatted_date.ilike(f"%{current_year}%"))
            print(f"Applying default year filter: {current_year}")

        # Apply subject filter if selected_subject is provided
        if selected_subject and selected_subject != "":
            query = query.filter(
                Emails_data.subject_part2.ilike(f"%{selected_subject}%")
            )
            print(f"Applying subject filter: {selected_subject}")
        if source and source != "":
            query = query.filter(Emails_data.subject_part1.ilike(f"%{source}%"))
            print(f"Applying subject filter: {source}")
        if prev_form and prev_form != "":
            candidate_query = db_session.query(recruiting_data).filter(
                and_(
                    recruiting_data.candidate == Emails_data.sender_name,
                    recruiting_data.did_you == prev_form,
                    recruiting_data.org_id == org_id,
                )
            )
            matched_sender_names = [
                candidate.candidate for candidate in candidate_query
            ]
            query = query.filter(Emails_data.sender_name.in_(matched_sender_names))
            print(f"Applying filter based on prev_form: {prev_form}")
        if keyword:
            keyword_lower = keyword.lower()
            query = query.filter(
                or_(
                    Emails_data.sender_name.ilike(f"%{keyword_lower}%"),
                    Emails_data.email.ilike(f"%{keyword_lower}%"),
                    Emails_data.subject_part1.ilike(f"%{keyword_lower}%"),
                    Emails_data.subject_part2.ilike(f"%{keyword_lower}%"),
                )
            )
            results = query.all()
            if not results:
                for email in Emails_data.query.all():
                    pdf_content_json = email.pdf_content_json
                    if pdf_content_json:
                        pdf_data_dict = json.loads(pdf_content_json)
                        pdf_data_json_lower = json.dumps(pdf_data_dict).lower()
                        if keyword_lower in pdf_data_json_lower:
                            results.append(email)
        # Apply country filter if selected_country is provided
        if selected_country and selected_country.strip().lower() in country_prefixes:
            print(f"Applying country filter for: {selected_country}")
            prefixes = country_prefixes[selected_country.strip().lower()]
            print(f"Prefixes for {selected_country}: {prefixes}")
            # Construct OR condition for country prefixes
            country_prefix_conditions = or_(
                *[
                    func.substr(Emails_data.phone_number, 1, len(prefix)) == prefix
                    for prefix in prefixes
                ]
            )
            print(f"Country prefix conditions: {country_prefix_conditions}")
            query = query.filter(country_prefix_conditions)
            print(f"Applied country filter for: {selected_country}")
        else:
            selected_country = ""

            # Count total number of pages
        total_items = query.count()
        total_pages = ceil(total_items / per_page)

        # Paginate the query results
        paginated_data = query.paginate(page=page, per_page=per_page)
        alldata = paginated_data.items  # Extract the items from the paginated object
        print(total_items, total_pages)
        serialized_alldata = []  # Initialize list to store serialized data

        # Serialize the data
        if alldata:
            print("Data found after filtering:")
            serialized_alldata = [
                {
                    "id": email.id,
                    "email": email.email,
                    "sender_name": email.sender_name,
                    "subject_part1": email.subject_part1,
                    "subject_part2": email.subject_part2,
                    "formatted_date": email.formatted_date,
                    "pdf_content_json": base64.b64encode(
                        email.pdf_content_json.encode("utf-8")
                    ).decode("utf-8")
                    if isinstance(email.pdf_content_json, str)
                    else None,
                    "phone_number": email.phone_number,
                    "file_content": base64.b64encode(email.file_content).decode("utf-8")
                    if email.file_content
                    else None,
                    "status": email.status,
                    "action": email.action,
                }
                for email in alldata
            ]
        else:
            print("No data found after filtering.")
    unique_subjects = (
        db.session.query(
            distinct(Emails_data.subject_part2),
            Emails_data.id,
            Emails_data.subject_part1,
        )
        .filter(Emails_data.org_id == org_id)
        .order_by(desc(Emails_data.id))
        .all()
    )
    unique_lines_set = set()

    for subject_tuple in unique_subjects:
        subject_line = subject_tuple[0]
        subject_part1 = subject_tuple[2]

        if (
            subject_part1.strip() == "HandsHR website"
            or subject_part1 == "GeoxHR website"
            or subject_part1 == "manually"
            or subject_part1 == "registered from Geox hr"
        ):
            unique_lines_set.add(subject_line)

        if " for " in subject_line and " applied for " in subject_line:
            after_for = subject_line.split(" for ", 1)[1].strip()
            unique_lines_set.add(after_for)

    unique_lines = sorted(list(unique_lines_set))
    candidatehistory = (
        db.session.query(candidate_history)
        .filter(candidate_history.org_id == org_id)
        .order_by(desc(candidate_history.id))
        .all()
    )

    # Check if the request is AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # If AJAX request, return JSON response
        filtered_data_html = render_template(
            "candidates.html",
            alldata=serialized_alldata,
            all_countries=all_countries,
            phone_codes=phone_codes,
            unique_lines=unique_lines,
            selected_year=selected_year,
            selected_country=selected_country,
            selected_subject=selected_subject,
            total_pages=total_pages,
            candidatehistory=candidatehistory,
        )  # Pass total_pages to the template
        return jsonify(
            {
                "html": filtered_data_html,
                "alldata": serialized_alldata,
                "total_pages": total_pages,
            }
        )
    else:
        # If regular request, render the template
        return render_template(
            "candidates.html",
            alldata=alldata,
            all_countries=all_countries,
            phone_codes=phone_codes,
            unique_lines=unique_lines,
            total_pages=total_pages,
            candidatehistory=candidatehistory,
        )  # Pass total_pages to the template


@app.route("/candidateprofile/<int:id>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def candidateprofile(id):
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    with db.session() as db_session:
        # Query candidate data from the Emails_data table
        candidate_data = (
            db_session.query(Emails_data)
            .filter(Emails_data.id == id, Emails_data.org_id == org_id)
            .order_by(desc(Emails_data.created_at))
            .all()
        )

        if not candidate_data:
            return "Candidate not found", 404

        # Extracting sender_name, email, and phone from the first entry
        candidate = candidate_data[0]
        sender_name = candidate.sender_name
        email = candidate.email
        phone = candidate.phone_number

        additional_data = (
            db_session.query(Emails_data)
            .filter(
                or_(
                    and_(
                        Emails_data.sender_name == sender_name,
                        Emails_data.email == email,
                        Emails_data.org_id == org_id,
                        Emails_data.phone_number == phone,
                        not_(Emails_data.id == id),
                    )
                )
            )
            .distinct()
            .all()
        )

        # Combining initial candidate data with additional matching data
        alldata = candidate_data + additional_data

        # Querying recruiting data based on sender_name
        sender_name = (
            db_session.query(Emails_data.sender_name)
            .filter(Emails_data.id == id)
            .first()
        )
        if sender_name:
            sender_name = sender_name[0]
            recruiting = (
                db_session.query(recruiting_data)
                .filter(
                    recruiting_data.candidate == sender_name,
                )
                .all()
            )
        else:
            recruiting = []

        # Querying document data based on emails_data_id
        document_data = (
            db_session.query(Document)
            .join(Emails_data)
            .filter(Emails_data.id == id)
            .all()
        )
        notes_data = (
            db_session.query(Can_notes)
            .join(Emails_data)
            .filter(Emails_data.id == id)
            .all()
        )
    return render_template(
        "profile.html",
        alldata=alldata,
        recruiting=recruiting,
        document_data=document_data,
        notes_data=notes_data,
    )


@app.route("/upload_docs/<int:id>", methods=["GET", "POST"])
def upload_file(id):
    if request.method == "POST":
        org_id = request.cookies.get('org_id')
        uploaded_files = request.files.getlist("myFile")
        print(uploaded_files, "uploaded_files")
        for file in uploaded_files:
            file_content = file.read()
            new_document = Document(
                emails_data_id=id,
                file_name=file.filename,
                file_content=file_content,
                org_id=org_id,
            )
            db.session.add(new_document)
            db.session.commit()

        response = jsonify({"message": "success"})
        response.status_code = 200
        return response

    return render_template("profile.html")


@app.route("/fillnotes/<int:id>", methods=["GET", "POST"])
def fillnotes(id):
    if request.method == "POST":
        org_id = request.cookies.get('org_id')
        notes = request.form.get("notes")
        print(notes, "notes")
        if "user_id" in session:
            user_id = request.cookies.get('user_id')
            user_name = db.session.query(Users).filter_by(id=user_id).first()
            name = f"{user_name.fname} {user_name.lname}"
        new_document = Can_notes(
            emails_data_id=id,
            notes=notes,
            name=name,
            org_id=org_id,
        )
        db.session.add(new_document)
        can = db.session.query(Emails_data).filter_by(id=id).first()
        current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
        user_statement = f"Note added for candidate({can.sender_name}) by {user_name.fname} {user_name.lname} ({current_time}) "
        print(user_statement)
        candidate = candidate_history(
            candidate_id=id,  # Assuming 'order' is the newly added Joborder object
            notes=user_statement,
            org_id=org_id,
            created_at=datetime.utcnow(),
        )
        db.session.add(candidate)
        db.session.commit()

        response = jsonify({"message": "success"})
        response.status_code = 200
        return response

    return render_template("profile.html")


@app.route("/view_document/<int:email_id>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def view_document(email_id):
    email = Document.query.filter_by(id=email_id).first()

    if email and email.file_content:
        file_name = email.file_name
        file_content = email.file_content

        # Get the file extension
        _, file_extension = os.path.splitext(file_name)

        # Set the mimetype based on the file extension
        mimetype = mimetypes.types_map.get(
            file_extension.lower(), "application/octet-stream"
        )

        response = send_file(io.BytesIO(file_content), mimetype=mimetype)

        return response

    return jsonify({"error": "File not found"}), 404


@app.route("/editdeal/<int:id>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def editdeal(id):
    type = "edit"
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    formdata = Marketing.query.filter(Marketing.id == id).first()
    jobsdata = Joborder.query.filter(Joborder.company_id == id).all()
    return render_template(
        "marketing.html", type=type, formdata=formdata, jobsdata=jobsdata, session=session
    )


@app.route("/export_csv", methods=["POST"])
def export_csv():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    export_route = request.form["export_route"]

    action = ""
    status = ""
    subject_part1 = ""
    if export_route == "/candidate":
        action = ""
        columns_to_export = [
            "sender_name",
            "email",
            "subject_part1",
            "subject_part2",
            "formatted_date",
            "phone_number",
            "status",
        ]
    elif export_route == "/placedcandidates":
        status = "Candidate Placement"
        columns_to_export = [
            "sender_name",
            "email",
            "subject_part1",
            "subject_part2",
            "formatted_date",
            "phone_number",
            "status",
        ]
    elif export_route == "/rejectcandidates":
        status = "Reject"
        columns_to_export = [
            "sender_name",
            "email",
            "subject_part1",
            "subject_part2",
            "formatted_date",
            "phone_number",
            "status",
        ]
    elif export_route == "/selecteddata":
        action = "Interested"
        status = "Reject"  # Assuming this was meant to be set for 'selecteddata'
        columns_to_export = [
            "sender_name",
            "email",
            "subject_part1",
            "subject_part2",
            "formatted_date",
            "phone_number",
            "status",
            "action",
        ]

    with db.session() as rsession:
        data = rsession.query(Emails_data).filter(Emails_data.org_id == org_id).all()

    # Filter data based on export route conditions
    if export_route == "/candidate":
        data = [row for row in data if row.action == ""]
    elif export_route == "/placedcandidates":
        data = [row for row in data if row.status == "Candidate Placement"]
    elif export_route == "/selecteddata":
        data = [
            row
            for row in data
            if row.action == "Interested"
            and row.status != "Reject"
            and row.status != "Candidate Placement"
        ]
    elif export_route == "/rejectcandidates":
        data = [row for row in data if row.status == "Reject"]

    # Create a CSV file in-memory
    output = io.StringIO()
    csv_writer = csv.writer(output)

    # Write the header row with the selected columns
    csv_writer.writerow(columns_to_export)

    # Write the data rows
    for row in data:
        row_data = [getattr(row, column) for column in columns_to_export]
        csv_writer.writerow(row_data)

    output.seek(0)

    # Send the CSV file as a response
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=data.csv"},
    )


@app.route("/pdf_content/<int:email_id>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def get_pdf_content(email_id):
    email = Emails_data.query.filter_by(id=email_id).first()

    if email and email.file_content:
        file_name = email.file_name
        file_content = email.file_content

        # Get the file extension
        _, file_extension = os.path.splitext(file_name)

        # Set the mimetype based on the file extension
        mimetype = mimetypes.types_map.get(
            file_extension.lower(), "application/octet-stream"
        )

        # Mark the email as read when the user views the PDF
        if not email.is_read:
            email.is_read = True
            db.session.commit()

        response = send_file(io.BytesIO(file_content), mimetype=mimetype)

        return response

    return jsonify({"error": "PDF not found"}), 404


# read/unread
@app.route("/check_is_read/<int:email_id>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def check_is_read(email_id):
    email = Emails_data.query.get(email_id)
    if email:
        return jsonify({"is_read": email.is_read})
    return jsonify({"error": "Email not found"}), 404


@app.route("/filter_emails")
def filter_emails():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    keyword = request.args.get("country_code")
    # print(keyword, "keyword")
    pdf_data = Emails_data.query.order_by(
        desc(Emails_data.id, Emails_data.org_id == org_id)
    ).all()
    matching_emails = []
    for email in pdf_data:
        pdf_content_json = email.pdf_content_json
        if pdf_content_json:
            pdf_data_dict = json.loads(pdf_content_json)
            pdf_data_json_lower = json.dumps(pdf_data_dict).lower()
            pdf_words = pdf_data_json_lower.split()
            if keyword in pdf_words:
                matching_emails.append(
                    {
                        "id": email.id,
                        "email": email.email,
                        "status": email.status,
                        "action": email.action,
                        "sender_name": email.sender_name,
                        "subject_part1": email.subject_part1,
                        "subject_part2": email.subject_part2,
                        "formatted_date": email.formatted_date,
                        "pdf_content_json": pdf_content_json,
                        "phone_number": email.phone_number,
                    }
                )

    # Print the search results to the console for debugging
    # print(f"Search results: {matching_emails}")

    return jsonify(matching_emails)


@app.route("/search_pdf")
def search_pdf():
    keyword = request.args.get("keyword")
    current_url = request.args.get("currentUrl")
    keyword_lower = keyword.lower()
    pdf_data = Emails_data.query.order_by(desc(Emails_data.id)).all()
    matching_emails = []

    # First, search in all columns except pdf_content_json
    for email in pdf_data:
        if (
            (current_url == "candidate" and email.action != "Interested")
            or (
                current_url == "selecteddata"
                and email.action == "Interested"
                and email.status != "Candidate Placement"
                and email.status != "Reject"
            )
            or (
                current_url == "placedcandidates"
                and email.status == "Candidate Placement"
                and email.status != "Reject"
            )
            or (
                current_url == "rejectcandidates"
                and email.status == "Reject"
                and email.status != "Candidate Placement"
            )
            or current_url
            not in ["candidate", "selecteddata", "placedcandidates", "rejectcandidates"]
        ):
            if (
                email.email
                and keyword_lower in email.email.lower()
                or email.sender_name
                and keyword_lower in email.sender_name.lower()
                or email.subject_part1
                and keyword_lower in email.subject_part1.lower()
                or email.subject_part2
                and keyword_lower in email.subject_part2.lower()
                or email.formatted_date
                and keyword_lower in email.formatted_date.lower()
                or email.phone_number
                and keyword_lower in email.phone_number.lower()
                or email.status
                and keyword_lower in email.status.lower()
                or email.action
                and keyword_lower in email.action.lower()
            ):
                matching_emails.append(
                    {
                        "id": email.id,
                        "email": email.email,
                        "sender_name": email.sender_name,
                        "subject_part1": email.subject_part1,
                        "subject_part2": email.subject_part2,
                        "formatted_date": email.formatted_date,
                        "phone_number": email.phone_number,
                        "pdf_content_json": base64.b64encode(
                            email.pdf_content_json.encode("utf-8")
                        ).decode("utf-8")
                        if isinstance(email.pdf_content_json, str)
                        else None,
                        "file_content": base64.b64encode(email.file_content).decode(
                            "utf-8"
                        )
                        if email.file_content
                        else None,
                        "status": email.status,
                        "action": email.action,
                    }
                )

    # If no result is found, search in pdf_content_json
    if not matching_emails:
        for email in pdf_data:
            pdf_content_json = email.pdf_content_json
            if pdf_content_json:
                pdf_data_dict = json.loads(pdf_content_json)
                pdf_data_json_lower = json.dumps(pdf_data_dict).lower()
                if (
                    (current_url == "candidate" and email.action != "Interested")
                    or (
                        current_url == "selecteddata"
                        and email.action == "Interested"
                        and email.status != "Candidate Placement"
                        and email.status != "Reject"
                    )
                    or (
                        current_url == "placedcandidates"
                        and email.status == "Candidate Placement"
                    )
                    or (current_url == "rejectcandidates" and email.status == "Reject")
                    or current_url
                    not in [
                        "candidate",
                        "selecteddata",
                        "placedcandidates",
                        "rejectcandidates",
                    ]
                ):
                    if keyword_lower in pdf_data_json_lower:
                        matching_emails.append(
                            {
                                "id": email.id,
                                "email": email.email,
                                "sender_name": email.sender_name,
                                "subject_part1": email.subject_part1,
                                "subject_part2": email.subject_part2,
                                "formatted_date": email.formatted_date,
                                "phone_number": email.phone_number,
                                "pdf_content_json": base64.b64encode(
                                    email.pdf_content_json.encode("utf-8")
                                ).decode("utf-8")
                                if isinstance(email.pdf_content_json, str)
                                else None,
                                "file_content": base64.b64encode(
                                    email.file_content
                                ).decode("utf-8")
                                if email.file_content
                                else None,
                                "status": email.status,
                                "action": email.action,
                            }
                        )

    return jsonify(matching_emails)


@app.route("/updatemail", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def updatemail():
    try:
        org_id = request.cookies.get('org_id')
        data = request.get_json()
        id = data.get("id")
        user = db.session.query(Emails_data).filter_by(id=id).first()

        selected_option = data.get("selectedOption")
        print("selected_option", selected_option)

        if selected_option == "Reverse changes":
            user.status = "applied"
            user.created_at = datetime.now()  # Set created_at to the current timestamp
        elif selected_option == "Interested":
            user.action = "Interested"
            user.status = "applied"
            user.created_at = datetime.now()  # Set created_at to the current timestamp
        elif selected_option == "move to applied":
            user.action = ""
            user.status = (
                "applied" if user.status == "Candidate Placement" else user.status
            )
            user.created_at = datetime.now()  # Set created_at to the current timestamp

        db.session.add(user)
        db.session.commit()

        if "user_id" in session:
            user_id = request.cookies.get('user_id')
            user_name = db.session.query(Users).filter_by(id=user_id).first()
            current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
            if selected_option == "Interested":
                selected_option = "Selected"
            elif selected_option == "move to applied":
                selected_option = "Unselected"

            user_statement = f"Candidate name as {user.sender_name} is {selected_option} by {user_name.fname} {user_name.lname} ({current_time}) "

            # Check if a similar statement exists in candidate history
            existing_statement = (
                db.session.query(candidate_history)
                .filter_by(candidate_id=id, org_id=org_id, notes=user_statement)
                .first()
            )
            if not existing_statement:
                # If not, create a new history entry
                candidate = candidate_history(
                    candidate_id=id,
                    notes=user_statement,
                    org_id=org_id,
                    created_at=datetime.utcnow(),
                )
                db.session.add(candidate)
                db.session.commit()
                print(user_statement)

        return jsonify({"message": "Update successful"}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred: " + str(e)}), 500


@app.route("/deletemail", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def deletemail():
    try:
        data = request.get_json()
        id = data.get("id")
        # Query the database to find the Users record by ID
        user = db.session.query(Emails_data).filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "record deleted successfully"}), 200
        else:
            return jsonify({"Record not found for uid:", id})
    except Exception as e:
        # Handle any other unexpected errors
        return jsonify({"error": "An error occurred: " + str(e)}), 500


@app.route("/members")
# @role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def members():
    user_idd = request.cookies.get('user_id')
    print("useris found in cookies", user_idd)
    org_id = request.cookies.get('org_id')
    org_name = request.cookies.get('org_name')
    print("org_idorg_name", org_name)
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    members_data = (
        Users.query.filter(Users.org_id == org_id).order_by(desc(Users.id)).all()
    )
    memberhistory = (
        db.session.query(member_history)
        .filter(member_history.org_id == org_id)
        .order_by(desc(member_history.id))
        .all()
    )

    return render_template(
        "members.html",
        members_data=members_data,
        memberhistory=memberhistory,
        org_name=org_name,
        session=session,
    )


@app.route("/organizations")
@role_required(allowed_roles=["CEO"])
def organizations():
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    organization_data = organization.query.order_by(desc(organization.id)).all()
    print("organization_data", organization_data)
    return render_template("organization.html", organizations=organization_data, session=session)


@app.route("/apporg", methods=["POST"])
# @role_required(allowed_roles=["CEO"])
def apporg():
    if request.method == "POST":
        id = request.form.get("id")
        company = request.form.get("company")
        com_email = request.form.get("com_email")
        com_web = request.form.get("com_web")
        com_address = request.form.get("com_address")
        num_employee = request.form.get("num_employee")
        com_number = request.form.get("com_number")
        linkedin = True if request.form.get("lkd") == "1" else False
        ziprecuiter = True if request.form.get("zpr") == "2" else False
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        notiemail = request.form.get("notiemail")
        phone_number = request.form.get("phone_number")
        note = request.form.get("note")
        cred_id = request.form.get("cred_id")

        existing_entry = organization.query.filter_by(id=id, company=company).first()
        print("existing_entry", existing_entry)
        if existing_entry:
            organizations_data = (
                db.session.query(organization).filter(organization.id == id).first()
            )
            existing_entry.company = company
            existing_entry.com_email = com_email
            existing_entry.com_web = com_web
            existing_entry.com_address = com_address
            existing_entry.linkedin = linkedin
            existing_entry.ziprecuiter = ziprecuiter
            existing_entry.num_employee = num_employee
            existing_entry.fname = fname
            existing_entry.com_number = com_number
            existing_entry.lname = lname
            existing_entry.phone_number = phone_number
            existing_entry.email = email
            existing_entry.status = "Approved"
            existing_entry.note = note
            if email and cred_id:
                print("email, cred_id", email, cred_id)
                existing_user = Users.query.filter(
                    Users.email == email, Users.org_name == company
                ).first()
                existing_cred = org_cred.query.filter(
                    org_cred.id == cred_id, org_cred.company == company
                ).first()
                print("email, existing_user", existing_cred, existing_user)
                if existing_user and existing_cred:
                    print("done")
                    existing_user.role = "owner"
                    existing_user.fname = organizations_data.fname
                    existing_user.lname = organizations_data.lname
                    existing_user.email = organizations_data.com_email
                    existing_user.password = organizations_data.password
                    existing_user.designation = "owner"
                    existing_user.status = "Active"
                    existing_user.org_name = company
                    existing_user.org_id = id
                    existing_cred.org_id = id
                    existing_cred.company = company
                    existing_cred.noti_email = notiemail
                    existing_cred.iemail = request.form.get("iemail")
                    existing_cred.zemail = request.form.get("zemail")
                    existing_cred.ipassword = request.form.get("ipassword")
                    existing_cred.zpassword = request.form.get("zpassword")
                    existing_cred.status = "Active"
                    print("done2")
                    db.session.commit()
                    return jsonify({"message": "Save successfully!"})

            else:
                credentry = org_cred(
                    org_id=id,
                    company=company,
                    noti_email=notiemail,
                    iemail=request.form.get("iemail"),
                    zemail=request.form.get("zemail"),
                    ipassword=request.form.get("ipassword"),
                    zpassword=request.form.get("zpassword"),
                    status="Active",
                )
                db.session.add(credentry)
                usrentry = Users(
                    role="owner",
                    fname=fname,
                    lname=lname,
                    email=com_email,
                    password=existing_entry.password,
                    designation="owner",
                    status="Active",
                    org_name=company,
                    org_id=id,
                )
                db.session.add(usrentry)
                email_subject = f"""Registration Approved"""
                print(email_subject)
                email_body = f"""
                                                                     <!DOCTYPE html>
                                                                     <html>
                                                                     <head>
                                                                          <style>
                                                                             body {{
                                                                                 font-family: Arial, sans-serif;
                                                                             }}
                                                                             .container {{
                                                                                 background-color: #f2f2f2;
                                                                                 padding: 20px;
                                                                                 border-radius: 10px;
                                                                                 max-width: 800px;
                                                                                 margin: auto;
                                                                             }}
                                                                             .cont-img{{
                                                                                 width: 34%;
                                                                                 margin: auto;
                                                                                 display: block;
                                                                                 margin-bottom:20px
                                                                             }}
                                                                             .details {{
                                                                                 margin-top: 10px;
                                                                             }}
                                                                             .details p {{
                                                                                 margin: 0;
                                                                             }}
                                                                             .bold {{
                                                                                 font-weight: bold;
                                                                             }}
                                                                             .signature {{
                                                                  margin-top: 20px;
                                                                  font-size:15px
                                                              }}
                                                              .signature p {{
                                                                    margin: 0px;
                                                              }}
                                                              .signature2 p {{
                                                                    margin: 0px;
                                                                    text-align: center;
                                                              }}
                                                              .hello{{
                                                                     border: 1px solid #19355f;
                                                                     margin-bottom: 28px;
                                                              }}
                                                              .signature2 {{
                                                                      padding: 7px;
                                                                      background: #ffff;
                                                                      margin-top: 21px;
                                                              }}
                                                                             .geoxhr {{
                                                                                    width: 100px;
                                                                                   margin-top: 10px;
                                                                             }}
                                                                         </style>
                                                                     </head>
                                                                     <body>
                                                                         <div class="container">
                                                                             <img class="cont-img" src="{{ url_for('static', filename='img/clickhr.png') }}">
                                                                             <div class="hello"></div>
                                                                             
                                                                             <h1>Sign in Now to Access Click-HR!</h1>

                                                                             <p>We are pleased to inform you that your registration with <span class="bold">Click-HR </span> has been approved! You are now ready to access our comprehensive range of services tailored to meet your business needs.</p>
                                                                             <p>To get started, simply sign in to your account using the following link: https://www.click-hr.com/login Once logged in, you will gain access to a host of features designed to streamline your operations, enhance productivity, and drive growth.</p>
                                                                             <p>Thank you for choosing <span class="bold">Click-HR </span>. We're excited to embark on this journey with you and support your success every step of the way.</p>

                                                                             <div class="signature">
                                                                  <p>Thankyou.</p>

                                                               </div>
                                                              <div class="signature2">
                                                                   <p>If assistance is required, feel free to reach out to us at:</p>
                                                                   <p>clickhr@click-hr.com.</p>
                                                                   <p> +1 647-930-0988</p>
                                                              </div>
                                                                         </div>
                                                                     </body>
                                                                     </html>
                                                                     """
                recipients = ["nhoorain161@gmail.com", com_email]

                msg = Message(
                    subject=email_subject, recipients=recipients, html=email_body
                )
                mail.send(msg)
                db.session.commit()

                return jsonify({"message": "Approved successfully!"})

        else:
            return jsonify({"error": "Organization Not Found"}), 400

        db.session.commit()

    return jsonify({"error": f"Error saving Organization"})


@app.route("/pendingorg/<int:id>")
def pendingorg(id):
    org_id = request.cookies.get('org_id')
    try:
        if id is not None:
            organizations = (
                db.session.query(organization).filter(organization.id == id).first()
            )
            if organizations:
                if organizations.status == "Request":
                    organizations.status = "Pending"
                else:
                    organizations.status = "Pending"
            db.session.commit()  # Commit the changes to the database
            return jsonify({"message": "Updated!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error updating : {str(e)}"}), 500


@app.route("/delorg/<int:id>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def delorg(id):
    if id is not None:
        try:
            db.session.query(organization).filter(organization.id == id).delete()
            db.session.query(org_cred).filter(org_cred.org_id == id).delete()
            db.session.query(Users).filter(Users.org_id == id).delete()
            db.session.commit()
            return jsonify({"message": "Request Removed!"}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting request: {str(e)}"}), 500


@app.route("/moredetails/<int:id>")
@role_required(allowed_roles=["CEO"])
def moredetails(id):
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    org_data = organization.query.filter(organization.id == id).first()
    org_datcre = org_cred.query.filter(org_cred.org_id == id).first()
    print("org_datcre", org_datcre)
    return render_template("org_detail.html", org_data=org_data, org_datcre=org_datcre, session=session)


@app.route("/addmembers")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def addmembers():
    org_name = request.cookies.get('org_name')
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    print("org_idorg_name", org_name)
    designation = userdesignation_data.query.all()
    role = Role.query.all()
    return render_template(
        "addmember.html", designations=designation, roles=role, org_name=org_name, session=session
    )


@app.route("/updatemembers/<int:id>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def updatemembers(id):
    if id is not None:
        designation = userdesignation_data.query.all()
        role = Role.query.all()
        user = db.session.query(Users).filter_by(id=id).first()
        return render_template(
            "addmember.html", data=user, designations=designation, roles=role
        )


@app.route("/savemember", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def savemember():
    if request.method == "POST":
        id = request.form.get("id")
        org_id = request.cookies.get('org_id')
        print(org_id, "org_id")
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        role = request.form.get("selected_role")
        designation = request.form.get("selected_designation")
        password = request.form.get("password")
        if password == "hello":
            encpassword = ""
        else:
            encpassword = sha256_crypt.encrypt(password)

        try:
            if id is not None:
                old_member = db.session.query(Users).filter_by(id=id).first()

                if old_member:
                    changes = {}  # Store changes here

                    # Check if each field is being updated and store the changes
                    if old_member.fname != fname:
                        changes["fname"] = {"from": old_member.fname, "to": fname}
                    if old_member.lname != lname:
                        changes["lname"] = {"from": old_member.lname, "to": lname}
                    if old_member.email != email:
                        changes["email"] = {"from": old_member.email, "to": email}
                    if old_member.role != role:
                        changes["role"] = {"from": old_member.role, "to": role}
                    if old_member.designation != designation:
                        changes["designation"] = {
                            "from": old_member.designation,
                            "to": designation,
                        }
                    if encpassword != "" and old_member.password != encpassword:
                        print({"from": old_member.password, "to": encpassword})
                        changes["password"] = {
                            "from": old_member.password,
                            "to": encpassword,
                        }

                    # Print changes
                    if changes:
                        print("Changes before update:")
                        change_statements = []  # Store change statements

                        for field, values in changes.items():
                            print("field", field)
                            if field == "password":
                                change_statements.append("Password changed")
                            elif field == "fname":
                                field = "First name"
                                change_statement = (
                                    f"{field}: {values['from']} to {values['to']}"
                                )
                                change_statements.append(change_statement)
                            elif field == "lname":
                                field = "Last name"
                                change_statement = (
                                    f"{field}: {values['from']} to {values['to']}"
                                )
                                change_statements.append(change_statement)
                            else:
                                if (
                                    values["from"] != values["to"]
                                ):  # Exclude printing when values are the same
                                    if isinstance(
                                        values["from"], int
                                    ):  # Check if value is an integer
                                        old_value_str = str(
                                            values["from"]
                                        )  # Convert integer to string
                                    else:
                                        old_value_str = values["from"]

                                    if isinstance(
                                        values["to"], int
                                    ):  # Check if value is an integer
                                        new_value_str = str(
                                            values["to"]
                                        )  # Convert integer to string
                                    else:
                                        new_value_str = values["to"]

                                    change_statement = (
                                        f"{field}: {old_value_str} to {new_value_str}"
                                    )
                                    change_statements.append(change_statement)

                        if change_statements:
                            if "user_id" in session:
                                user_id = request.cookies.get('user_id')
                                user_name = (
                                    db.session.query(Users)
                                    .filter_by(id=user_id)
                                    .first()
                                )
                                current_time = datetime.utcnow().strftime(
                                    "%b %d, %Y %I:%M%p"
                                )  # Format current time

                                user_statement = (
                                    f"{user_name.fname} {user_name.lname} made the following changes for {fname} {lname} as "
                                    + " and ".join(change_statements)
                                    + f" ({current_time})"
                                )
                                print(user_statement)

                                # Save change statement to Member history
                                memberhistory = member_history(
                                    member_id=old_member.id,
                                    notes=user_statement,
                                    org_id=org_id,  # Ensure org_id is set properly
                                    created_at=datetime.utcnow(),
                                )
                                db.session.add(memberhistory)
                                db.session.commit()

                entry = db.session.query(Users).filter_by(id=id).first()
                if entry:
                    entry.id = id
                    entry.role = role
                    entry.org_id = org_id
                    entry.fname = fname
                    entry.lname = lname
                    entry.email = email
                    entry.designation = designation
                    if encpassword != "":
                        entry.password = encpassword
                    else:
                        entry.password = old_member.password

                    db.session.commit()  # Update existing user
                    response = jsonify({"message": "Member updated successfully!"})
                else:
                    response = (
                        jsonify({"error": "Member with specified ID not found"}),
                        404,
                    )
            else:
                org_name = db.session.query(organization).filter_by(id=org_id).first()
                email_exists = db.session.query(
                    exists().where(Users.email == email)
                ).scalar()
                if not email_exists:
                    entry = Users(
                        fname=fname,
                        lname=lname,
                        email=email,
                        password=encpassword,
                        role=role,
                        designation=designation,
                        org_name=org_name.company,
                        org_id=org_id,
                    )
                    db.session.add(entry)
                    db.session.commit()
                    if "user_id" in session:
                        user_id = request.cookies.get('user_id')
                        user_name = (
                            db.session.query(Users).filter_by(id=user_id).first()
                        )
                        current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
                        user_statement = f"New Member named {fname} {lname} is created by {user_name.fname} {user_name.lname} ({current_time}) "
                        print(user_statement)

                        # After creating the history entry
                        memberhistory = member_history(
                            member_id=entry.id,
                            notes=user_statement,
                            org_id=org_id,
                            created_at=datetime.utcnow(),
                        )
                        db.session.add(memberhistory)
                        db.session.commit()
                    response = jsonify({"message": "Member created successfully!"})
                else:
                    response = jsonify({"error": "Email already exists"}), 400

        except Exception as e:
            # Handle any errors that occurred during database operations
            db.session.rollback()
            response = jsonify({"error": f"Error saving member: {str(e)}"})
            response.status_code = 500

        return response


@app.route("/deletemembers/<int:id>", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def deletemembers(id):
    org_id = request.cookies.get('org_id')
    if id is not None:
        try:
            member_name = db.session.query(Users).filter(Users.id == id).first()
            if member_name:
                if member_name.status == "Active":
                    member_name.status = "Inactive"
                    print("prv", member_name.updated_at)
                    member_name.updated_at = datetime.utcnow()
                    print("updt", member_name.updated_at)

                else:
                    member_name.status = "Active"
            db.session.commit()
            if "user_id" in session:
                user_id = request.cookies.get('user_id')
                user_name = db.session.query(Users).filter_by(id=user_id).first()
                current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
                user_statement = f"Memeber {member_name.fname} {member_name.lname} is Archive  by {user_name.fname} {user_name.lname} ({current_time}) "
                print(user_statement)

                # After creating the history entry
                memberhistory = member_history(
                    member_id=id,
                    notes=user_statement,
                    org_id=org_id,
                    created_at=datetime.utcnow(),
                )
                db.session.add(memberhistory)
                db.session.commit()
            return jsonify({"message": "Member Archive!"}), 200
        except Exception as e:
            return jsonify({"message": f"Error archiving member: {str(e)}"}), 500


@app.route("/unarchivedmember/<int:id>", methods=["POST"])
def unarchivedmember(id):
    org_id = request.cookies.get('org_id')
    try:
        if id is not None:
            member_name = db.session.query(Users).filter(Users.id == id).first()
            if member_name:
                if member_name.status == "Inactive":
                    member_name.status = "Active"
                else:
                    member_name.status = "Inactive"
            db.session.commit()  # Commit the changes to the database

            if "user_id" in session:
                user_id = request.cookies.get('user_id')
                user_name = db.session.query(Users).filter_by(id=user_id).first()
                current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
                user_statement = f"Memeber {member_name.fname} {member_name.lname} is restore  by {user_name.fname} {user_name.lname} ({current_time}) "
                print(user_statement)

                # After creating the history entry
                memberhistory = member_history(
                    member_id=id,
                    notes=user_statement,
                    org_id=org_id,
                    created_at=datetime.utcnow(),
                )
                db.session.add(memberhistory)
                db.session.commit()
            return jsonify({"message": "Member Restore!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error restoring member: {str(e)}"}), 500


@app.route("/deletedocuments/<int:id>", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def deletedocuments(id):
    if id is not None:
        try:
            db.session.query(Document).filter(Document.id == id).delete()
            db.session.commit()
            return jsonify({"message": "Document Deleted!"}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting member: {str(e)}"}), 500


@app.route("/restpassword/<int:id>", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def reset_password(id):
    if id is not None:
        try:
            user = db.session.query(Users).filter(Users.id == id).first()
            print(user, "user")
            if user:
                user.password = (
                    ""  # You may want to use a more secure method to reset the password
                )
                db.session.commit()
                return jsonify({"message": "Password reset successfully!"}), 200
            else:
                return jsonify({"message": "User not found"}), 404
        except Exception as e:
            return jsonify({"message": f"Error resetting password: {str(e)}"}), 500


@app.route("/user")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def user():
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    return render_template("/user.html", session=session)


@app.route("/changepassword", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def chnagepassword():
    if request.method == "POST":
        user_id = request.cookies.get('user_id')
        oldpassword = request.form.get("oldps")
        newpassword = request.form.get("newps")
        confirmpassword = request.form.get("confirmpswrd")
        check = db.session.query(Users).filter_by(id=user_id).first()
        varify = sha256_crypt.verify(oldpassword.encode('utf-8'), check.password.encode('utf-8'))
        # bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
        # print(varify)
        if varify:
            # print("varify")
            if newpassword == confirmpassword:
                # print("password confirm")
                password = sha256_crypt.encrypt(confirmpassword)
                check.password = password
                db.session.add(check)
                db.session.commit()
                return render_template("user.html", msg="password changed successfully")
            else:
                return render_template(
                    "user.html", msg="confirm password did not match"
                )
        else:
            return render_template("user.html", msg="old password did not match")


# @app.route('/onereporting')
# @role_required(allowed_roles=['user', 'admin','owner', 'CEO'])
# def onereporting():
#     return render_template('/onereporting-form.html')


# @app.route('/onereporting_form/<int:candidate_id>/job/<int:jobid>/OrderId/<int:OrderId>')
# @app.route('/onereporting_form/<int:id>')
# @app.route('/onereporting_form/<int:id>/<string:status>')
# @role_required(allowed_roles=['user', 'admin','owner', 'CEO'])
# def onereporting_form(id=None, candidate_id=None, jobid=None, OrderId=None,status=None):
#     if id is not None:
#         user = db.session.query(Emails_data).filter_by(id=id).first()
#         companydata = None
#     else:
#         pass
#     # company = Marketing.query.all()
#     members = Users.query.filter(Users.designation != 'admin').all()
#     company = Joborder.query.filter(Joborder.jobstatus == 'active').all()
#     positions = Joborder.query.filter_by(company_id=companydata.id, id=OrderId,
#                                          archived=False).all() if companydata else []
#     print("positions",company)
#     company = [c for c in company if c.company_name is not None]
#     company = sorted(company, key=lambda x: x.company_name)
#     return render_template('recruiting.html', data=user, company=company, companydata=companydata, positions=positions,
#                            members=members)


@app.route("/onereporting_form/<int:id>/<string:status>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def onereporting_form(id=None, status=None):
    org_id = request.cookies.get('org_id')
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    if id is not None:
        print(status)
        user = db.session.query(Emails_data).filter_by(id=id).first()
    else:
        pass
    members = Users.query.filter(
        Users.designation != "owner", Users.status == "Active", Users.org_id == org_id
    ).all()
    company = Joborder.query.filter(
        Joborder.jobstatus == "active", Joborder.org_id == org_id
    ).all()
    # print("positions",companydata, company)
    company = [c for c in company if c.company_name is not None]
    company = sorted(company, key=lambda x: x.company_name)
    return render_template(
        "resume.html", data=user, company=company, status=status, members=members, session=session
    )


from flask_mail import Mail, Message

app.config["MAIL_SERVER"] = "smtp.mail.us-east-1.awsapps.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "clickhr@click-hr.com"
app.config["MAIL_PASSWORD"] = "I8is123??"

# Specify the default sender email address
app.config["MAIL_DEFAULT_SENDER"] = "clickhr@click-hr.com"

mail = Mail(app)


def check_existing_job_order(title, company, org_id):
    existing_job_order = Joborder.query.filter(
        Joborder.title == title,
        Joborder.company_name == company,
        Joborder.jobstatus == "active",
        Joborder.org_id == org_id,
    ).first()
    return existing_job_order is not None


@app.route("/marketing", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def marketing():
    if request.method == "POST":
        org_id = request.cookies.get('org_id')
        rcpt = ["nisa@i8is.com"]
        if org_id:
            tocred = org_cred.query.filter(org_cred.org_id == org_id).first()
            if tocred:
                toemail = tocred.noti_email
                rcpt.append(toemail)
        print("org_id", org_id)
        id = request.form.get("id")
        user_id = request.form.get("user_id")
        name = request.form.get("name")
        company = request.form.get("company")
        selected_company = request.form.get("selected_company")
        print(company, "company1", selected_company, "company")
        cperson = request.form.get("cperson")
        phone = request.form.get("phone")
        location = request.form.get("location")
        markup = request.form.get("markup")
        jobid = request.form.get("jobid")
        active = "active"
        job_titles = request.form.getlist("job_title")
        jobids = request.form.getlist("jobid")
        pay_rates = request.form.getlist("pay_rate")
        pay_rate_types = request.form.getlist("pay_rate_type")
        shifts_start = request.form.getlist("shift_start")
        shifts_end = request.form.getlist("shift_end")
        total_vacancies = request.form.getlist("total_vacancies")
        Status = request.form.get("Status")
        substatus = request.form.get("substatus")
        if substatus is None:
            if Status == "New deal and contract not signed":
                substatus = "not Signed"
            elif Status == "New deal opened and contract signed":
                substatus = "Signed"

        # print(job_titles,"job_titles",jobid,pay_rates,pay_rate_types,shifts_start,shifts_end,total_vacancies)

        other_report = request.form.get("otherreport")
        notes = request.form.get("notes")
        if company == "" and selected_company != "":
            company_parts = selected_company.split("|")
            if len(company_parts) == 2:
                company = company_parts[1]
            else:
                pass

        # print(Status, "status")
        print(company, "company")

        formtype = "Marketing"
        if id is not None:
            entry = db.session.query(Marketing).filter_by(id=id).first()
            entry.company = company
            entry.status = Status
            entry.cperson = cperson
            entry.cphone = phone
            entry.Markup = markup
            entry.location = location
            entry.otherReport = other_report
            entry.Notes = notes
            entry.org_id = org_id
            db.session.add(entry)
            db.session.commit()
            forms = (
                db.session.query(allforms_data)
                .filter_by(form_id=id, form_type=formtype)
                .first()
            )
            forms.belongsto = cperson
            forms.status = Status
            forms.org_id = org_id
            db.session.add(forms)
            db.session.commit()

            for i in range(len(job_titles)):
                print(i, "length of jobs")
                for jobids in jobids:
                    updatejob = (
                        db.session.query(Joborder)
                        .filter(Joborder.company_id == id, Joborder.id == jobids)
                        .first()
                    )
                    if updatejob:
                        updatejob.title = job_titles[i]
                        updatejob.payrate = pay_rates[i]
                        updatejob.salarytype = pay_rate_types[i]
                        updatejob.starttime = shifts_start[i]
                        updatejob.endtime = shifts_end[i]
                        updatejob.vacancy = total_vacancies[i]
                        updatejob.jobstatus = active
                        selected_days = request.form.getlist(f"days-{i + 1}[]")
                        selected_days_str = ",".join(selected_days)
                        updatejob.days = selected_days_str
                        print(
                            "selected_days_strwith0",
                            updatejob.title,
                            updatejob.payrate,
                            updatejob.salarytype,
                            updatejob.starttime,
                            updatejob.endtime,
                            updatejob.vacancy,
                            updatejob.jobstatus,
                            updatejob.org_id,
                            updatejob.days,
                        )

                        db.session.add(updatejob)
                        db.session.commit()
        else:
            # Now, insert the list data
            entry = Marketing(
                user_id=user_id,
                name=name,
                company=company,
                status=Status,
                substatus=substatus,
                cperson=cperson,
                company_status=active,
                cphone=phone,
                location=location,
                Markup=markup,
                otherReport=other_report,
                Notes=notes,
                org_id=org_id,
            )

            db.session.add(entry)
            db.session.commit()

            submitted_id = entry.id
            forms = allforms_data(
                user_id=user_id,
                form_id=submitted_id,
                filledby=name,
                belongsto=cperson,
                form_type=formtype,
                status=Status,
                org_id=org_id,
            )
            db.session.add(forms)
            db.session.commit()
            db.session.commit()
            current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
            user_statement = f"{Status} by {name} with {company} ({current_time}) "
            print(user_statement)

            # After creating the history entry
            candidate = Deals_history(
                marketing_id=entry.id,  # Assuming 'order' is the newly added Joborder object
                notes=user_statement,
                org_id=org_id,
                created_at=datetime.utcnow(),
            )
            db.session.add(candidate)
            db.session.commit()

            try:
                # Check if the user_id exists in the Users table and is not an admin
                user = Users.query.filter(
                    Users.id == user_id,
                    Users.designation != "owner",
                    Users.status == "Active",
                ).first()
                if user:
                    today = datetime.today()
                    print("today", today)
                    days_to_saturday = today.weekday()
                    saturday = today - timedelta(days=days_to_saturday)
                    friday = saturday + timedelta(days=6)
                    weekstart = saturday.strftime("%Y-%m-%d")
                    weekend = friday.strftime("%Y-%m-%d")
                    print("Week start:", weekstart, user_id)
                    print("Week end:", weekend, user_id)

                    target_entry = Targets.query.filter(
                        Targets.user_id == user_id,
                        Targets.weekstart == weekstart,
                        Targets.weekend == weekend,
                        Targets.org_id == org_id,
                    ).all()
                    print("Target entry:", target_entry)

                    if not target_entry:
                        users = Users.query.filter(
                            Users.designation != "owner", Users.status == "Active"
                        ).all()
                        for user in users:
                            target_data = Targets(
                                user_id=user.id,
                                name=f"{user.fname} {user.lname}",
                                new=0,
                                notsigned=0,
                                reopen=0,
                                resume=0,
                                interview=0,
                                placement=0,
                                helping=0,
                                target=0,
                                score=0,
                                weekstart=weekstart,
                                weekend=weekend,
                                org_id=org_id,
                            )
                            db.session.add(target_data)

                        db.session.commit()

                        target_entry = Targets.query.filter(
                            Targets.user_id == user_id,
                            Targets.org_id == org_id,
                            Targets.weekstart == weekstart,
                            Targets.weekend == weekend,
                        ).all()
                        print("Target entry:", target_entry)

                    for entry in target_entry:
                        if Status == "New deal opened and contract signed":
                            entry.new_achieve += 1
                            entry.target_achieve += 1
                            entry.score_achieve += 3
                        elif Status == "New deal and contract not signed":
                            entry.notsigned_achieve += 1
                            entry.target_achieve += 1
                            entry.score_achieve += 2
                        elif Status == "Reopened deals":
                            entry.reopen_achieve += 1
                            entry.target_achieve += 1
                            entry.score_achieve += 1

                        print(
                            " entry.achieve_percentage ",
                            entry.achieve_percentage,
                            entry.score,
                            entry.score_achieve,
                        )
                        if entry.score != 0:  # Check if entry.score is not zero
                            if (
                                entry.score_achieve != 0
                            ):  # Check if entry.score_achieve is not zero
                                entry.achieve_percentage = (
                                    entry.score_achieve / entry.score * 100
                                )
                                print(
                                    " entry.achieve_percentage1 ",
                                    entry.achieve_percentage,
                                )
                            else:
                                entry.achieve_percentage = (
                                    0  # If entry.score_achieve is zero
                                )
                                print(
                                    " entry.achieve_percentage2 ",
                                    entry.achieve_percentage,
                                )
                        else:
                            entry.achieve_percentage = 0  # If entry.score is zero
                            print(
                                " entry.achieve_percentage3 ", entry.achieve_percentage
                            )

                    db.session.commit()
                    print("Targets updated successfully")
                else:
                    pass
            except Exception as e:
                print(f"Error updating/inserting Targets: {e}")

            for i in range(len(job_titles)):
                if check_existing_job_order(job_titles[i], company, org_id):
                    alert_message = "A job order with the same title for this company already exists. Please consider changing the title or deactivating the existing order."
                    return jsonify({"message": alert_message}), 400
                else:
                    job_title = job_titles[i]
                    pay_rate = pay_rates[i]
                    pay_rate_type = pay_rate_types[i]
                    shift_start = shifts_start[i]
                    shift_end = shifts_end[i]
                    selected_days = request.form.getlist(f"days-{i + 1}[]")
                    selected_days_str = ",".join(selected_days)
                    selected_days = request.form.getlist(
                        f"days-{i + 1}[]"
                    )  # Use the unique field name
                    selected_days_str = ",".join(selected_days)
                    # print(f"Selected days for job {i + 1}: {selected_days_str}")
                    total_vacancy = total_vacancies[i]

                    order = Joborder(
                        user_id=user_id,
                        company_id=submitted_id,
                        company_name=company,
                        payrate=pay_rate,
                        salarytype=pay_rate_type,
                        jobstatus=active,
                        title=job_title,
                        starttime=shift_start,
                        endtime=shift_end,
                        vacancy=total_vacancy,
                        days=selected_days_str,
                        filled_vacancy=0,
                        org_id=org_id,
                    )
                    # jobstatus = jobstatuss,
                    db.session.add(order)
                    db.session.commit()
                    if "user_id" in session:
                        user_id = request.cookies.get('user_id')
                    user_name = db.session.query(Users).filter_by(id=user_id).first()
                    current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
                    user_statement = f"Joborder name as {order.title} is created by {user_name.fname} {user_name.lname} ({current_time}) "
                    print(user_statement)

                    # After creating the history entry
                    history_entry = Joborder_history(
                        joborder_id=order.id,  # Assuming 'order' is the newly added Joborder object
                        notes=user_statement,
                        org_id=org_id,
                        created_at=datetime.utcnow(),
                    )
                    db.session.add(history_entry)
                    db.session.commit()

            recipients = rcpt
            # recipients = ['nhoorain161@gmail.com']

            if Status == "New deal opened and contract signed":
                email_subject = f"""New Contract Signed"""
                email_body = f"""
                  <!DOCTYPE html>
                  <html>
                  <head>
                       <style>
                          body {{
                              font-family: Arial, sans-serif;
                          }}
                          .container {{
                              background-color: #f2f2f2;
                              padding: 20px;
                              border-radius: 10px;
                              max-width: 800px;
                              margin: auto;
                          }}
                          .cont-img{{
                            width: 34%;
                            margin: auto;
                            display: block;
                            margin-bottom:20px
                          }}
                          .details {{
                              margin-top: 10px;
                          }}
                          .details p {{
                              margin: 0;
                          }}
                          .bold {{
                              font-weight: bold;
                          }}
                          .signature {{
                              margin-top: 20px;
                              font-size:15px
                          }}
                          .signature p {{
                                margin: 0px;
                          }}
                          .signature2 p {{
                                margin: 0px;
                                text-align: center;
                          }}
                          .hello{{
                                 border: 1px solid #19355f;
                                 margin-bottom: 28px;
                          }}
                          .signature2 {{
                                  padding: 7px;
                                  background: #ffff;
                                  margin-top: 21px;
                          }}
                          
                          .geoxhr {{
                                 width: 100px;
                                margin-top: 10px;
                          }}
                      </style>
                  </head>
                  <body>
                      <div class="container">
                          <img class="cont-img" src="{{ url_for('static', filename='img/clickhr.png') }}">
                                         <div class="hello"></div>
                          <p> A new contract signed with {company} filled by {name}</p>
                          <div class="details">
                              <p><span class="bold">Company Name:</span> {company}</p>
                              <p><span class="bold">FilledBy:</span> {name}</p>
                              <p><span class="bold">Markup:</span> {markup}%</p>
                          </div>

                          {"" if len(job_titles) == 0 else '<p class="bold">Job Titles and Total Vacancies:</p>'}

                          <div class="details">
                              {"" if len(job_titles) == 0 else '<ul>'}
                              {"".join([f'<li> Job Titles: <span class="bold">{job_title}</span>, Total Vacancies: <span class="bold">{vacancy}</span></li>' for i, (job_title, vacancy) in enumerate(zip(job_titles, total_vacancies))])}
                              {"" if len(job_titles) == 0 else '</ul>'}
                          </div>

                          <div class="signature">
                              <p>Thankyou.</p>

                           </div>
                          <div class="signature2">
                               <p>If assistance is required, feel free to reach out to us at:</p>
                               <p>clickhr@click-hr.com.</p>
                               <p> +1 647-930-0988</p>
                          </div>
                      </div>
                  </body>
                  </html>
                  """
            elif Status == "New deal and contract not signed":
                email_subject = f"""Deal Contract not Signed """
                email_body = f"""
                  <!DOCTYPE html>
                  <html>
                  <head>
                       <style>
                          body {{
                              font-family: Arial, sans-serif;
                          }}
                          .container {{
                              background-color: #f2f2f2;
                              padding: 20px;
                              border-radius: 10px;
                              max-width: 800px;
                              margin: auto;
                          }}
                          .cont-img{{
                            width: 34%;
                            margin: auto;
                            display: block;
                            margin-bottom:20px
                          }}
                          .details {{
                              margin-top: 10px;
                          }}
                          .details p {{
                              margin: 0;
                          }}
                          .bold {{
                              font-weight: bold;
                          }}
                          .signature {{
                              margin-top: 20px;
                              font-size:15px
                          }}
                          .signature p {{
                                margin: 0px;
                          }}
                          .signature2 p {{
                                margin: 0px;
                                text-align: center;
                          }}
                          .hello{{
                                 border: 1px solid #19355f;
                                 margin-bottom: 28px;
                          }}
                          .signature2 {{
                                  padding: 7px;
                                  background: #ffff;
                                  margin-top: 21px;
                          }}
                          .geoxhr {{
                                 width: 100px;
                                margin-top: 10px;
                          }}
                      </style>
                  </head>
                  <body>
                      <div class="container">
                           <img class="cont-img" src="{{ url_for('static', filename='img/clickhr.png') }}">
                                         <div class="hello"></div>

                            <p> Deal Contract not signed with {company} filled by {name}</p>                         
                          <div class="details">
                              <p><span class="bold">Company Name:</span> {company}</p>
                              <p><span class="bold">FilledBy:</span> {name}</p>
                              <p><span class="bold">Markup:</span> {markup}%</p>
                          </div>

                          {"" if len(job_titles) == 0 else '<p class="bold">Job Titles and Total Vacancies:</p>'}

                          <div class="details">
                              {"" if len(job_titles) == 0 else '<ul>'}
                              {"".join([f'<li> Job Titles: <span class="bold">{job_title}</span>, Total Vacancies: <span class="bold">{vacancy}</span></li>' for i, (job_title, vacancy) in enumerate(zip(job_titles, total_vacancies))])}
                              {"" if len(job_titles) == 0 else '</ul>'}
                          </div>

                          <div class="signature">
                              <p>Thankyou.</p>

                           </div>
                          <div class="signature2">
                               <p>If assistance is required, feel free to reach out to us at:</p>
                               <p>clickhr@click-hr.com.</p>
                               <p> +1 647-930-0988</p>
                          </div>
                      </div>
                  </body>
                  </html>
                  """
            elif Status == "Reopened deals":
                email_subject = f"""Reopened Deal"""
                email_body = f"""
                  <!DOCTYPE html>
                  <html>
                  <head>
                      <style>
                          body {{
                              font-family: Arial, sans-serif;
                          }}
                          .container {{
                              background-color: #f2f2f2;
                              padding: 20px;
                              border-radius: 10px;
                              max-width: 800px;
                              margin: auto;
                          }}
                          .cont-img{{
                            width: 34%;
                            margin: auto;
                            display: block;
                            margin-bottom:20px
                          }}
                          .details {{
                              margin-top: 10px;
                          }}
                          .details p {{
                              margin: 0;
                          }}
                          .bold {{
                              font-weight: bold;
                          }}
                          .signature {{
                              margin-top: 20px;
                              font-size:15px
                          }}
                          .signature p {{
                                margin: 0px;
                          }}
                          .signature2 p {{
                                margin: 0px;
                                text-align: center;
                          }}
                          .hello{{
                                 border: 1px solid #19355f;
                                 margin-bottom: 28px;
                          }}
                          .signature2 {{
                                  padding: 7px;
                                  background: #ffff;
                                  margin-top: 21px;
                          }}
                          .geoxhr {{
                                 width: 100px;
                                margin-top: 10px;
                          }}
                      </style>
                  </head>
                  <body>
                      <div class="container">
                            <img class="cont-img" src="{{ url_for('static', filename='img/clickhr.png') }}">
                                         <div class="hello"></div>
                          <p> Reopen Deal signed with {company} filled by {name}</p>

                            
                            <div class="details">
                              <p><span class="bold">Company Name:</span> {company}</p>
                              <p><span class="bold">FilledBy:</span> {name}</p>
                              <p><span class="bold">Markup:</span> {markup}%</p>
                          </div>

                          {"" if len(job_titles) == 0 else '<p class="bold">Job Titles and Total Vacancies:</p>'}

                          <div class="details">
                              {"" if len(job_titles) == 0 else '<ul>'}
                              {"".join([f'<li> Job Titles: <span class="bold">{job_title}</span>, Total Vacancies: <span class="bold">{vacancy}</span></li>' for i, (job_title, vacancy) in enumerate(zip(job_titles, total_vacancies))])}
                              {"" if len(job_titles) == 0 else '</ul>'}
                          </div>

                          <div class="signature">
                              <p>Thankyou.</p>

                           </div>
                          <div class="signature2">
                               <p>If assistance is required, feel free to reach out to us at:</p>
                               <p>clickhr@click-hr.com.</p>
                               <p> +1 647-930-0988</p>
                          </div>
                      </div>
                  </body>
                  </html>
                  """
            else:
                email_subject = "New Form Submission"

            msg = Message(subject=email_subject, recipients=recipients, html=email_body)
            mail.send(msg)

        response = jsonify({"message": "success"})
        response.status_code = 200
        return response
    else:
        return "Unsupported method"


@app.route("/hrforms", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def hrforms():
    if request.method == "POST":
        org_id = request.cookies.get('org_id')
        print("org_id", org_id)
        id = request.form.get("id")
        user_id = request.form.get("user_id")
        name = request.form.get("name")
        candidate = request.form.get("cname")
        late = request.form.get("Late/absent")
        Informed = request.form.get("Informed/uninformed")
        reasonvacation = request.form.get("reasonvacation")
        notes = request.form.get("notes")
        formtype = "HR Forms"
        status = late + " " + Informed
        if late != "request for leave":
            reasonvacation = ""
        if id is not None:
            entry = db.session.query(Hrforms).filter_by(id=id).first()
            entry.candidate_name = candidate
            entry.late = late
            entry.informed = Informed
            entry.reason_vacation = reasonvacation
            entry.notes = notes
            entry.org_id = org_id
            db.session.add(entry)
            db.session.commit()
            forms = (
                db.session.query(allforms_data)
                .filter_by(form_id=id, form_type=formtype)
                .first()
            )
            forms.belongsto = candidate
            forms.status = status
            forms.org_id = org_id
        else:
            entry = Hrforms(
                user_id=user_id,
                name=name,
                candidate_name=candidate,
                late=late,
                informed=Informed,
                reason_vacation=reasonvacation,
                notes=notes,
                org_id=org_id,
            )
            db.session.add(entry)
            db.session.commit()
            submitted_id = entry.id
            if "user_id" in session:
                user_id = request.cookies.get('user_id')
            user_name = db.session.query(Users).filter_by(id=user_id).first()
            current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
            user_statement = f"HR form is filled by {user_name.fname} {user_name.lname} ({current_time}) "
            print(user_statement)

            hr_report = hr_history(
                hr_id=submitted_id,
                notes=user_statement,
                org_id=org_id,
                created_at=datetime.utcnow(),
            )
            db.session.add(hr_report)
            db.session.commit()
            forms = allforms_data(
                user_id=user_id,
                form_id=submitted_id,
                filledby=name,
                belongsto=candidate,
                form_type=formtype,
                status=status,
                org_id=org_id,
            )
        db.session.add(forms)
        db.session.commit()
        response = jsonify({"message": "success"})
        response.status_code = 200
        return response
    else:
        return "Unsupported method"


@app.route("/resumesent", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def resumesent():
    if request.method == "POST":
        org_id = request.cookies.get('org_id')
        print("org_id", org_id)
        formid = request.form.get("formid")
        id = request.form.get("id")
        user_id = request.form.get("user_id")
        name = request.form.get("name")
        candidate = request.form.get("cname")
        phone = request.form.get("cphone")
        position = request.form.get("selected_position")
        did_you = request.form.get("Didyou")
        companydate = request.form.get("companydate")
        content = ""
        status = ""
        filename = ""
        selected_value = request.form.get("selected_company")
        # company_id, company_name = selected_value.split('|')
        interviewdate = request.form.get("interviewdate")
        other_report = request.form.get("Otherreport")
        if position == "select" or not position:
            response = jsonify(
                {
                    "error": "Please fill in all required fields marked with an asterisk (*)"
                }
            )
            return response
            print(position, "l90")
        else:
            company_id, company_name = selected_value.split("|")
            if did_you == "Help Another":
                help = request.form.get("help")
                person_starting = request.form.get("person_starting")
                status = did_you
                belongsto_value = help

            elif did_you != "Help Another":
                help = ""
                person_starting = ""
                status = did_you
                belongsto_value = (
                    candidate  # Use 'belongsto_value' instead of 'candidate'
                )

            if did_you == "Candidate Placement":
                ecname = request.form.get("ecname")
                ecnumber = request.form.get("ecnumber")
                location = request.form.get("Location")
                locationcgoing = request.form.get("clocation")
                starttime = request.form.get("starttime")
                needmember = request.form.get("needteam")
                file = request.files["myFile"]
                filename = file.filename
                if file and filename:  # Check if the file has a valid extension
                    content = file.read()
                else:
                    content = None
                    filename = ""

            elif did_you != "Candidate Placement":
                file = ""
                ecname = ""
                ecnumber = ""
                location = ""
                locationcgoing = ""
                starttime = ""
                needmember = ""
                content = None
                filename = ""
            notes = request.form.get("notes")
            rnotes = request.form.get("rnotes")
            formtype = "Person Placement"
            if formid is not None:
                entry = db.session.query(recruiting_data).filter_by(id=formid).first()
                entry.candidate = candidate
                entry.phone = phone
                entry.company = company_name
                entry.did_you = did_you
                entry.ecname = ecname
                entry.ecnumber = ecnumber
                entry.location = location
                entry.locationcgoing = locationcgoing
                entry.starttime = starttime
                entry.needmember = needmember
                entry.interviewdate = interviewdate
                entry.companydate = companydate
                entry.help = help
                entry.person_starting = person_starting
                entry.other_report = other_report
                entry.position = position
                entry.notes = notes
                entry.org_id = org_id

                if file:
                    filename = file.filename
                    content = file.read()

                db.session.add(entry)
                db.session.commit()

                forms = (
                    db.session.query(allforms_data)
                    .filter_by(form_id=formid, form_type=formtype)
                    .first()
                )
                forms.belongsto = candidate
                forms.status = status
                forms.org_id = org_id
                db.session.add(forms)
                db.session.commit()
                if status == "Candidate Placement":
                    with Session() as rsession:
                        companyy = (
                            rsession.query(Marketing)
                            .filter(Marketing.id == company_id)
                            .first()
                        )
                        updatevacancy = (
                            rsession.query(Joborder)
                            .filter(
                                Joborder.company_id == companyy.id,
                                Joborder.title == position,
                                Joborder.jobstatus == "active",
                            )
                            .first()
                        )
                        if updatevacancy:
                            updatevacancy.filled_vacancy += 1
                            if updatevacancy.filled_vacancy == updatevacancy.vacancy:
                                updatevacancy.jobstatus = "inactive"
                                rsession.add(updatevacancy)
                                rsession.commit()

                else:
                    hello = "No matching record found for updating vacancy"
                db.session.commit()
                response = jsonify({"message": "success"})
                response.status_code = 200
                return response
            else:
                entry = recruiting_data(
                    user_id=user_id,
                    name=name,
                    candidate=candidate,
                    phone=phone,
                    company=company_name,
                    did_you=did_you,
                    ecname=ecname,
                    ecnumber=ecnumber,
                    location=location,
                    locationcgoing=locationcgoing,
                    starttime=starttime,
                    needmember=needmember,
                    interviewdate=interviewdate,
                    companydate=companydate,
                    help=help,
                    person_starting=person_starting,
                    other_report=other_report,
                    position=position,
                    notes=notes,
                    rnotes=rnotes,
                    file_name=filename,
                    content=content,
                    org_id=org_id,
                )
                db.session.add(entry)
                db.session.commit()
                submitted_id = entry.id
                forms = allforms_data(
                    user_id=user_id,
                    form_id=submitted_id,
                    filledby=name,
                    belongsto=belongsto_value,
                    form_type=formtype,
                    status=status,
                    org_id=org_id,
                )
                db.session.add(forms)
                db.session.commit()
                if status == "Candidate Placement":
                    with Session() as rsession:
                        companyy = (
                            rsession.query(Marketing)
                            .filter(Marketing.id == company_id)
                            .first()
                        )
                        updatevacancy = (
                            rsession.query(Joborder)
                            .filter(
                                Joborder.company_id == companyy.id,
                                Joborder.title == position,
                                Joborder.jobstatus == "active",
                            )
                            .first()
                        )
                        if updatevacancy:
                            updatevacancy.filled_vacancy += 1
                            if updatevacancy.filled_vacancy == updatevacancy.vacancy:
                                updatevacancy.jobstatus = "inactive"
                                rsession.add(updatevacancy)
                                rsession.commit()

                else:
                    hello = "No matching record found for updating vacancy"
                db.session.commit()
                current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
                user_statement = ""
                if status == "Candidate Placement":
                    status = "Candidate Placement"
                    user_statement = f"Candidate ({candidate}) is Placed in {entry.company} for {entry.position} by {name} ({current_time}) "
                elif status == "Help Another":
                    status = "Help Another"
                    user_statement = f"Candidate ({candidate}) is selected by {name} for Help to {help} ({current_time}) "

                elif status == "Interview Scheduled":
                    status = "Interview Scheduled"
                    user_statement = f"Candidate ({candidate}) is selected for Interview in {entry.company} for {entry.position} by {name} ({current_time}) "

                elif status == "Resume Sent":
                    status = "Resume Sent"
                    user_statement = f"Resume is sent  of Candidate  ({candidate}) at {entry.company} for {entry.position} by {name} ({current_time}) "

                elif status == "Reject":
                    status = "Reject"
                    user_statement = f"Rejection is filled for Candidate  ({candidate}) at {entry.company} for {entry.position} by {name} ({current_time}) "
                print(user_statement)

                # After creating the history entry
                candidatehis = candidate_history(
                    candidate_id=entry.id,  # Assuming 'order' is the newly added Joborder object
                    notes=user_statement,
                    org_id=org_id,
                    created_at=datetime.utcnow(),
                )
                db.session.add(candidatehis)
                db.session.commit()
                try:
                    # Check if the user_id exists in the Users table and is not an admin
                    user = Users.query.filter(
                        Users.id == user_id,
                        Users.designation != "owner",
                        Users.status == "Active",
                    ).first()
                    if user:
                        today = datetime.today()
                        print("today", today)
                        days_to_saturday = today.weekday()
                        saturday = today - timedelta(days=days_to_saturday)
                        friday = saturday + timedelta(days=6)
                        weekstart = saturday.strftime("%Y-%m-%d")
                        weekend = friday.strftime("%Y-%m-%d")
                        print("Week start:", weekstart)
                        print("Week end:", weekend)

                        target_entry = Targets.query.filter(
                            Targets.user_id == user_id,
                            Targets.org_id == org_id,
                            Targets.weekstart == weekstart,
                            Targets.weekend == weekend,
                        ).all()
                        print("Target entry:", target_entry)
                        if not target_entry:
                            users = Users.query.filter(
                                Users.designation != "owner",
                                Users.org_id == org_id,
                                Users.status == "Active",
                            ).all()
                            for user in users:
                                target_data = Targets(
                                    user_id=user.id,
                                    name=f"{user.fname} {user.lname}",
                                    new=0,
                                    notsigned=0,
                                    reopen=0,
                                    resume=0,
                                    interview=0,
                                    placement=0,
                                    helping=0,
                                    target=0,
                                    score=0,
                                    weekstart=weekstart,
                                    weekend=weekend,
                                    org_id=org_id,
                                )
                                db.session.add(target_data)

                            db.session.commit()

                            target_entry = Targets.query.filter(
                                Targets.user_id == user_id,
                                Targets.org_id == org_id,
                                Targets.weekstart == weekstart,
                                Targets.weekend == weekend,
                            ).all()
                            print("Target entry:", target_entry)
                        for entry in target_entry:
                            if did_you == "Resume Sent":
                                entry.resume_achieve += 1
                                entry.target_achieve += 1
                                entry.score_achieve += 2
                            elif did_you == "Interview Scheduled":
                                entry.interview_achieve += 1
                                entry.target_achieve += 1
                                entry.score_achieve += 2
                            elif did_you == "Candidate Placement":
                                entry.placement_achieve += 1
                                entry.target_achieve += 1
                                entry.score_achieve += 3
                            elif did_you == "Help Another":
                                entry.helping_achieve += 1
                                entry.target_achieve += 1
                                entry.score_achieve += 1
                            print(
                                " entry.achieve_percentage ",
                                entry.achieve_percentage,
                                entry.score,
                                entry.score_achieve,
                            )
                            # print(" entry.achieve_percentage ", entry.achieve_percentage, entry.score, entry.score_achieve)
                            if entry.score != 0:  # Check if entry.score is not zero
                                if (
                                    entry.score_achieve != 0
                                ):  # Check if entry.score_achieve is not zero
                                    entry.achieve_percentage = (
                                        entry.score_achieve / entry.score * 100
                                    )
                                    print(
                                        " entry.achieve_percentage1 ",
                                        entry.achieve_percentage,
                                    )
                                else:
                                    entry.achieve_percentage = (
                                        0  # If entry.score_achieve is zero
                                    )
                                    print(
                                        " entry.achieve_percentage2 ",
                                        entry.achieve_percentage,
                                    )
                            else:
                                entry.achieve_percentage = 0  # If entry.score is zero
                                print(
                                    " entry.achieve_percentage3 ",
                                    entry.achieve_percentage,
                                )

                        db.session.commit()
                        print("Targets updated successfully")
                    else:
                        pass
                except Exception as e:
                    print(f"Error updating Targets: {e}")
                    pass
                if status == "Candidate Placement" or status == "Reject":
                    print(status, "if")
                    user = db.session.query(Emails_data).filter_by(id=id).first()
                    user.status = status
                    user.action = "Interested"
                    db.session.add(user)
                    db.session.commit()

                else:
                    print(status, "el")
                    user = db.session.query(Emails_data).filter_by(id=id).first()
                    user.status = did_you
                    user.action = ""
                    db.session.add(user)
                    db.session.commit()
                if status == "Candidate Placement":
                    with Session() as rsession:  # Start a transaction
                        companyy = (
                            rsession.query(Marketing)
                            .filter(Marketing.id == company_id)
                            .first()
                        )
                        updatevacancy = (
                            rsession.query(Joborder)
                            .filter(
                                Joborder.company_id == companyy.id,
                                Joborder.title == position,
                                Joborder.jobstatus == "active",
                            )
                            .first()
                        )
                        if updatevacancy:
                            updatevacancy.filled_vacancy += 1
                            if updatevacancy.filled_vacancy == updatevacancy.vacancy:
                                updatevacancy.jobstatus = "inactive"
                                rsession.add(updatevacancy)
                                rsession.commit()
                            else:
                                updatevacancy.jobstatus = "active"
                                rsession.add(updatevacancy)
                                rsession.commit()
                    print(candidate)
                    email_subject = f"""Candidate Placement """
                    print(email_subject)
                    email_body = f"""
                                 <!DOCTYPE html>
                                 <html>
                                 <head>
                                      <style>
                                         body {{
                                             font-family: Arial, sans-serif;
                                         }}
                                         .container {{
                                             background-color: #f2f2f2;
                                             padding: 20px;
                                             border-radius: 10px;
                                             max-width: 800px;
                                             margin: auto;
                                         }}
                                         .cont-img{{
                                             width: 34%;
                                             margin: auto;
                                             display: block;
                                             margin-bottom:20px
                                         }}
                                         .details {{
                                             margin-top: 10px;
                                         }}
                                         .details p {{
                                             margin: 0;
                                         }}
                                         .bold {{
                                             font-weight: bold;
                                         }}
                                         .signature {{
                              margin-top: 20px;
                              font-size:15px
                          }}
                          .signature p {{
                                margin: 0px;
                          }}
                          .signature2 p {{
                                margin: 0px;
                                text-align: center;
                          }}
                          .hello{{
                                 border: 1px solid #19355f;
                                 margin-bottom: 28px;
                          }}
                          .signature2 {{
                                  padding: 7px;
                                  background: #ffff;
                                  margin-top: 21px;
                          }}
                                         .geoxhr {{
                                                width: 100px;
                                               margin-top: 10px;
                                         }}
                                     </style>
                                 </head>
                                 <body>
                                     <div class="container">
						<img class="cont-img" src="{{ url_for('static', filename='img/clickhr.png') }}">
                                         <div class="hello"></div>
                                         <p>A new Candidate({candidate}) is Placed at company({company_name}) filled by {name}</p>
                                         <div class="details">
                                            <p><span class="bold">company Name:</span> {company_name}</p>
                                             <p><span class="bold">candidate Name:</span> {candidate}</p>
                                             <p><span class="bold">position:</span> {position}</p>
                                             <p><span class="bold">FilledBy:</span> {name}</p>

                                         </div>

                                         <div class="signature">
                                            <p>Thankyou.</p>
                                         </div>
					<div class="signature2">
                               <p>If assistance is required, feel free to reach out to us at:</p>
                               <p>clickhr@click-hr.com.</p>
                               <p> +1 647-930-0988</p>
                          </div>
                                     </div>
                                 </body>
                                 </html>
                                 """
                    # recipients = ['nhoorain161@gmail.com']
                    rcpt = ["nisa@i8is.com"]
                    if org_id:
                        tocred = org_cred.query.filter(
                            org_cred.org_id == org_id
                        ).first()
                        if tocred:
                            toemail = tocred.noti_email
                            rcpt.append(toemail)
                    recipients = rcpt
                    # recipients = ['nhoorain161@gmail.com']

                    msg = Message(
                        subject=email_subject, recipients=recipients, html=email_body
                    )
                    mail.send(msg)
                else:
                    hello2 = "No matching record found for updating vacancy."
                db.session.commit()
                response = jsonify({"message": "success"})
                response.status_code = 200
                return response
    else:
        # Handle other HTTP methods, if needed
        return "Unsupported method"


@app.route("/jobs")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def jobs():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    
    alljobs = Jobs.query.filter(Jobs.org_id == org_id).order_by(desc(Jobs.id)).all()
    return render_template("jobs.html", alljobs=alljobs, session=session)


@app.route("/deletejobs/<int:id>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def deletejob(id):
    if id is not None:
        try:
            db.session.query(Jobs).filter(Jobs.id == id).delete()
            db.session.commit()
            # print(f'Successfully deleted job with ID {id}')
            return jsonify({"message": "Job Deleted!"}), 200
        except Exception as e:
            # print(f'Error deleting job with ID {id}: {str(e)}')
            return jsonify({"message": f"Error job delete: {str(e)}"}), 500


def convert_unix_to_local(timestamp):
    # Convert Unix timestamp to local datetime
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp)


@app.route("/postnewjobs")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def postnewjobs():
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    return render_template("/postnewjobs.html", session=session)


@app.route("/selectjob/<int:id>", methods=["POST", "GET"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def selectjob(id):
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    if request.method == "POST":
        jobid = request.form.get("jobid")
        # print(jobid)
        user = db.session.query(Emails_data).filter_by(id=id).first()
        jobdata = db.session.query(Jobs).filter_by(id=jobid).first()
        return render_template("recruiting.html", data=user, jobdata=jobdata, session=session)
    else:
        alljobs = Jobs.query.all()
        return render_template("jobs.html", alljobs=alljobs, id=id, session=session)


@app.route("/editjob/<int:id>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def editjob(id):
    job = db.session.query(Jobs).filter(Jobs.id == id).first()
    post_job_history = (
        db.session.query(postjob_history)
        .filter(postjob_history.postjod_id == id)
        .order_by(desc(postjob_history.id))
        .all()
    )
    print(post_job_history, "post_job_history")
    
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    return render_template(
        "postnewjobs.html", job=job, postjob_history=post_job_history, session=session
    )


@app.route("/activity_log")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def activity_log():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    filter_option = request.args.get("filter", "")
    start_date_str = request.args.get("startDate", "")
    end_date_str = request.args.get("endDate", "")

    start_date = (
        datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
    )
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None

    if filter_option == "users":
        history_data = (
            db.session.query(member_history)
            .filter(member_history.org_id == org_id)
            .order_by(desc(member_history.created_at))
            .all()
        )
    elif filter_option == "candidate":
        history_data = (
            db.session.query(candidate_history)
            .filter(candidate_history.org_id == org_id)
            .order_by(desc(candidate_history.created_at))
            .all()
        )
    elif filter_option == "orders":
        history_data = (
            db.session.query(Joborder_history)
            .filter(Joborder_history.org_id == org_id)
            .order_by(desc(Joborder_history.created_at))
            .all()
        )
    elif filter_option == "post":
        history_data = (
            db.session.query(postjob_history)
            .filter(postjob_history.org_id == org_id)
            .order_by(desc(postjob_history.created_at))
            .all()
        )
    elif filter_option == "deals":
        history_data = (
            db.session.query(Deals_history)
            .filter(Deals_history.org_id == org_id)
            .order_by(desc(Deals_history.created_at))
            .all()
        )
    elif filter_option == "hr":
        history_data = (
            db.session.query(hr_history)
            .filter(hr_history.org_id == org_id)
            .order_by(desc(hr_history.created_at))
            .all()
        )
    elif filter_option == "other":
        history_data = (
            db.session.query(otherreport_history)
            .filter(otherreport_history.org_id == org_id)
            .order_by(desc(otherreport_history.created_at))
            .all()
        )
    elif filter_option == "del":
        history_data = (
            db.session.query(Deletedata)
            .filter(Deletedata.org_id == org_id)
            .order_by(desc(Deletedata.created_at))
            .all()
        )
    else:
        history_data = (
            db.session.query(member_history).filter(member_history.org_id == org_id),
            db.session.query(candidate_history).filter(
                candidate_history.org_id == org_id
            ),
            db.session.query(Joborder_history).filter(
                Joborder_history.org_id == org_id
            ),
            db.session.query(postjob_history).filter(postjob_history.org_id == org_id),
            db.session.query(Deals_history).filter(Deals_history.org_id == org_id),
            db.session.query(hr_history).filter(hr_history.org_id == org_id),
            db.session.query(otherreport_history).filter(
                otherreport_history.org_id == org_id
            ),
            db.session.query(Deletedata).filter(Deletedata.org_id == org_id),
        )
        history_data = list(chain(*history_data))

    filtered_notes = []
    for entry in history_data:
        if hasattr(entry, "notes"):
            if start_date and end_date:
                if start_date <= entry.created_at <= end_date + timedelta(days=1):
                    filtered_notes.append((entry.notes, entry.created_at))
            elif start_date and not end_date:
                if start_date <= entry.created_at:
                    filtered_notes.append((entry.notes, entry.created_at))
            elif not start_date and end_date:
                if entry.created_at <= end_date + timedelta(days=1):
                    filtered_notes.append((entry.notes, entry.created_at))
            else:
                filtered_notes.append((entry.notes, entry.created_at))

    if start_date or end_date:  # Check if filtering by date is applied
        filtered_notes.sort(key=lambda x: x[1])  # Sort in ascending order based on date
    else:
        filtered_notes.sort(
            key=lambda x: x[1], reverse=True
        )  # Sort in descending order by default

    all_notes = [note[0] for note in filtered_notes]

    return render_template("activity.html", all_notes=all_notes)


def format_date(date):
    return date.strftime("%b %d, %Y %I:%M%p")


# Example usage:
date_str = "2024-03-08 10:31:10.657603"
date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
formatted_date = format_date(date_obj)
print(formatted_date)


@app.route("/updatejoborder", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def updatejoborder():
    if request.method == "POST":
        org_id = request.cookies.get('org_id')
        print("org_id", org_id)
        id = request.form.get("id")
        company = request.form.get("company")
        title = request.form.get("title")
        payrate = int(request.form.get("payrate"))
        pay_rate_type = request.form.get("pay_rate_type")
        vacancy = int(request.form.get("vacancy"))
        days = request.form.getlist("days[]")
        shift_start = request.form.get("shift_start")
        shift_end = request.form.get("shift_end")
        print(request.method, id, "ge", pay_rate_type, type(pay_rate_type))
        try:
            if id is not None:
                old_job_order = db.session.query(Joborder).filter_by(id=id).first()
                if "user_id" in session:
                    user_id = request.cookies.get('user_id')
                user_name = db.session.query(Users).filter_by(id=user_id).first()

                if old_job_order:
                    changes = {}  # Store changes here

                    # Check if each field is being updated and store the changes
                    if old_job_order.company_name != company:
                        changes["company_name"] = {
                            "from": old_job_order.company_name,
                            "to": company,
                        }
                    if old_job_order.title != title:
                        changes["title"] = {"from": old_job_order.title, "to": title}
                    if old_job_order.payrate != payrate:
                        changes["payrate"] = {
                            "from": old_job_order.payrate,
                            "to": payrate,
                        }
                    if old_job_order.salarytype != pay_rate_type:
                        print(
                            old_job_order.salarytype,
                            type(old_job_order.salarytype),
                            "old_job_order.salarytype",
                        )

                        changes["salarytype"] = {
                            "from": old_job_order.salarytype,
                            "to": pay_rate_type,
                        }
                    if old_job_order.vacancy != vacancy:
                        changes["vacancy"] = {
                            "from": old_job_order.vacancy,
                            "to": vacancy,
                        }
                    if old_job_order.days != ",".join(days):
                        changes["days"] = {
                            "from": old_job_order.days,
                            "to": ",".join(days),
                        }
                    if old_job_order.starttime != shift_start:
                        changes["starttime"] = {
                            "from": old_job_order.starttime,
                            "to": shift_start,
                        }
                    if old_job_order.endtime != shift_end:
                        changes["endtime"] = {
                            "from": old_job_order.endtime,
                            "to": shift_end,
                        }
                    # Add more fields to check for changes as needed

                    # Print changes
                    if changes:
                        print("Changes before update:")
                        change_statements = []  # Store change statements

                        for field, values in changes.items():
                            if (
                                values["from"] != values["to"]
                            ):  # Exclude printing when values are the same
                                if isinstance(
                                    values["from"], int
                                ):  # Check if value is an integer
                                    old_value_str = str(
                                        values["from"]
                                    )  # Convert integer to string
                                else:
                                    old_value_str = values["from"]

                                if isinstance(
                                    values["to"], int
                                ):  # Check if value is an integer
                                    new_value_str = str(
                                        values["to"]
                                    )  # Convert integer to string
                                else:
                                    new_value_str = values["to"]

                                change_statement = (
                                    f"{field}: {old_value_str} to {new_value_str}"
                                )
                                change_statements.append(change_statement)

                        if change_statements:
                            current_time = datetime.utcnow().strftime(
                                "%b %d, %Y %I:%M%p"
                            )  # Format current time
                            user_statement = (
                                f"'{title}' joborder is updated with "
                                + " and ".join(change_statements)
                                + f" by {user_name.fname} {user_name.lname}  ({current_time})"
                            )
                            print(user_statement)

                            # Save change statement to Joborder_history
                            history_entry = Joborder_history(
                                joborder_id=id,
                                notes=user_statement,
                                org_id=org_id,
                                created_at=datetime.utcnow(),
                            )
                            db.session.add(history_entry)

                    # Update the job order with new data
                    old_job_order.company_name = company
                    old_job_order.title = title
                    old_job_order.payrate = payrate
                    old_job_order.salarytype = pay_rate_type
                    old_job_order.vacancy = vacancy
                    old_job_order.days = ",".join(days)
                    old_job_order.starttime = shift_start
                    old_job_order.endtime = shift_end
                    old_job_order.created_at = old_job_order.created_at
                    old_job_order.updated_at = datetime.utcnow()

                    db.session.commit()

                    response = jsonify({"message": "Job order updated successfully"})
                else:
                    response = jsonify({"error": "Job order not found"}), 404

            else:
                response = jsonify({"error": "ID parameter is missing"}), 400

        except Exception as e:
            # Handle any errors that occurred during database operations
            db.session.rollback()
            response = jsonify({"error": f"Error updating job order: {str(e)}"})
            response.status_code = 500

        return response


@app.route("/postjob", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def postjob():
    if request.method == "POST":
        org_id = request.cookies.get('org_id')
        print("org_id", org_id)
        id = request.form.get("id")
        title = request.form.get("title")
        name = request.form.get("name")
        selected_companies = request.form.getlist("company_name")
        user_id = request.form.get("user_id")
        location = request.form.get("location")
        experience = request.form.get("experience")
        JobType = request.form.get("Job-Type")
        duration = request.form.get("duration")
        onsite = request.form.get("onsite")
        salarytypes = request.form.get("salarytypes")
        Salary = request.form.get("Salary")
        date = request.form.get("date")
        job_status = request.form.get("active")
        description = request.form.get("description")
        responsibility = request.form.get("responsibility")
        eligibility = request.form.get("eligibility")
        notes = request.form.get("notes")
        relative_file_path = ""
        # print(selected_companies, "company")

        if (
            "Geox hr" in selected_companies
            and "Hands hr" in selected_companies
            and "i8is" in selected_companies
        ):
            company_code = "123"
        elif "Geox hr" in selected_companies and "Hands hr" in selected_companies:
            company_code = "12"
        elif "i8is" in selected_companies and "Hands hr" in selected_companies:
            company_code = "23"
        elif "i8is" in selected_companies and "Geox hr" in selected_companies:
            company_code = "13"
        elif "Geox hr" in selected_companies:
            company_code = "1"
        elif "Hands hr" in selected_companies:
            company_code = "2"
        elif "i8is" in selected_companies:
            company_code = "3"
        else:
            company_code = ""

        if id is not None:
            print(id)

            old_job = db.session.query(Jobs).filter_by(id=id).first()
            print(old_job)
            if old_job:
                changes = {}  # Store changes here

                # Check if each field is being updated and store the changes
                if old_job.title != title:
                    changes["title"] = {"from": old_job.title, "to": title}
                if old_job.company != company_code:
                    changes["company"] = {"from": old_job.company, "to": company_code}
                if old_job.experience != experience:
                    changes["experience"] = {
                        "from": old_job.experience,
                        "to": experience,
                    }
                if old_job.location != location:
                    changes["location"] = {"from": old_job.location, "to": location}
                if old_job.job_type != JobType:
                    changes["JobType"] = {"from": old_job.job_type, "to": JobType}
                if old_job.duration != duration:
                    changes["duration"] = {"from": old_job.duration, "to": duration}
                if old_job.onsite != onsite:
                    changes["onsite"] = {"from": old_job.onsite, "to": onsite}
                if old_job.salary_type != salarytypes:
                    changes["salary_type"] = {
                        "from": old_job.salary_type,
                        "to": salarytypes,
                    }
                if old_job.salary != Salary:
                    changes["salary"] = {"from": old_job.salary, "to": Salary}
                if old_job.job_date != date:
                    changes["job_date"] = {"from": old_job.job_date, "to": date}
                if old_job.job_status != job_status:
                    changes["job_status"] = {
                        "from": old_job.job_status,
                        "to": job_status,
                    }
                if old_job.description != description:
                    changes["description"] = {
                        "from": old_job.description,
                        "to": description,
                    }
                if old_job.responsibility != responsibility:
                    changes["responsibility"] = {
                        "from": old_job.responsibility,
                        "to": responsibility,
                    }
                if old_job.eligibility != eligibility:
                    changes["eligibility"] = {
                        "from": old_job.eligibility,
                        "to": eligibility,
                    }
                if old_job.notes != notes:
                    changes["notes"] = {"from": old_job.notes, "to": notes}
                company_names = {
                    "1": "Geox hr",
                    "2": "Hands hr",
                    "3": "i8is",
                    "12": "Geox hr, Hands hr",
                    "13": "Geox hr, i8is",
                    "23": "Hands hr, i8is",
                    "123": "Geox hr, Hands hr, i8is",
                }
                # Print changes
                if changes:
                    print("Changes before update:")
                    change_statements = []  # Store change statements

                    for field, values in changes.items():
                        print("field", field)
                        if (
                            field == "description"
                            or field == "responsibility"
                            or field == "eligibility"
                            or field == "notes"
                        ):
                            change_statements.append(field + " updated")
                        elif field == "company":
                            from_value, to_value = (
                                str(values["from"]),
                                str(values["to"]),
                            )
                            # Find the difference between the 'to' and 'from' values
                            missing_in_from = "".join(
                                [x for x in from_value if x not in to_value]
                            )
                            missing_in_to = "".join(
                                [x for x in to_value if x not in from_value]
                            )

                            if missing_in_from:
                                diff_location = "from_value"
                                missing_code = company_names.get(
                                    missing_in_from, "Unknown"
                                )
                                change_statement = f"{field}: {missing_code} is removed"
                                change_statements.append(change_statement)
                                print(change_statements)

                            elif missing_in_to:
                                diff_location = "to_value"
                                missing_code = company_names.get(
                                    missing_in_to, "Unknown"
                                )
                                change_statement = f"{field}: {missing_code} is added"
                                change_statements.append(change_statement)
                                print(change_statements)
                            else:
                                diff_location = "none"
                                missing_code = ""
                            print(missing_code, diff_location)
                        else:
                            if (
                                values["from"] != values["to"]
                            ):  # Exclude printing when values are the same
                                if isinstance(
                                    values["from"], int
                                ):  # Check if value is an integer
                                    old_value_str = str(
                                        values["from"]
                                    )  # Convert integer to string
                                else:
                                    old_value_str = values["from"]

                                if isinstance(
                                    values["to"], int
                                ):  # Check if value is an integer
                                    new_value_str = str(
                                        values["to"]
                                    )  # Convert integer to string
                                else:
                                    new_value_str = values["to"]

                                change_statement = (
                                    f"{field}: {old_value_str} to {new_value_str}"
                                )
                                change_statements.append(change_statement)

                    if change_statements:
                        if "user_id" in session:
                            user_id = request.cookies.get('user_id')
                            user_name = (
                                db.session.query(Users).filter_by(id=user_id).first()
                            )
                            current_time = datetime.utcnow().strftime(
                                "%b %d, %Y %I:%M%p"
                            )  # Format current time

                            user_statement = (
                                f"Job name '{title}' is updated with the following changes:"
                                + " and ".join(change_statements)
                                + f" by {user_name.fname} {user_name.lname} ({current_time})"
                            )
                            print(user_statement)

                            # Save change statement to Member history
                            postjobhistory = postjob_history(
                                postjod_id=id,
                                notes=user_statement,
                                org_id=org_id,
                                created_at=datetime.utcnow(),
                            )
                            db.session.add(postjobhistory)
                            db.session.commit()
            entry = db.session.query(Jobs).filter_by(id=id).first()
            entry.title = title
            entry.company = company_code
            entry.experience = experience
            entry.location = location
            entry.job_type = JobType
            entry.duration = duration
            entry.onsite = onsite
            entry.salary_type = salarytypes
            entry.salary = Salary
            entry.job_date = date
            entry.job_status = job_status
            entry.description = description
            entry.responsibility = responsibility
            entry.eligibility = eligibility
            entry.notes = notes

        else:
            entry = Jobs(
                user_id=user_id,
                name=name,
                title=title,
                image=relative_file_path,
                company=company_code,
                location=location,
                job_type=JobType,
                duration=duration,
                onsite=onsite,
                salary_type=salarytypes,
                salary=Salary,
                job_date=date,
                job_status=job_status,
                description=description,
                responsibility=responsibility,
                eligibility=eligibility,
                experience=experience,
                org_id=org_id,
                notes=notes,
            )
            db.session.add(entry)
            if "user_id" in session:
                user_id = request.cookies.get('user_id')
                user_name = db.session.query(Users).filter_by(id=user_id).first()
                current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
                user_statement = f"This Job name {title} is created by {user_name.fname} {user_name.lname} for {selected_companies}  ({current_time}) "
                print(user_statement)

                # After creating the history entry
                postjob = postjob_history(
                    postjod_id=entry.id,
                    notes=user_statement,
                    org_id=org_id,
                    created_at=datetime.utcnow(),
                )
                db.session.add(postjob)
                db.session.commit()
        db.session.commit()
        response = jsonify({"message": "success"})
        response.status_code = 200
        return response
    else:
        return "Unsupported method"


@app.route("/editjoborder/<int:id>/<string:str>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def editjoborder(id, str):
    print("hello", str)
    org_id = request.cookies.get('org_id')
    print("org_id", id, "id", org_id)
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    job_data = Joborder.query.filter(
        Joborder.id == id, Joborder.org_id == org_id
    ).first()
    print("job_data", job_data)
    job_history = (
        db.session.query(Joborder_history)
        .filter(Joborder_history.joborder_id == id)
        .order_by(desc(Joborder_history.id))
        .all()
    )
    print(job_history, "job_history")

    return render_template(
        "editjoborder.html", jobsdata=job_data, job_history=job_history, session=session
    )


@app.route("/jobOders")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def jobOders():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    jobsorders = (
        Joborder.query.filter(
            Joborder.archived == False,
            Joborder.jobstatus == "active",
            Joborder.org_id == org_id,
        )
        .order_by(desc(Joborder.id))
        .all()
    )
    print(jobsorders)
    return render_template("jobsorder.html", jobsorders=jobsorders)


# @app.route('/jobOders')
# @role_required(allowed_roles=['user', 'admin','owner', 'CEO'])
# def jobOders():
#     joborder_history = Joborder_history.query.all()
#     joborder = Joborder.query.all()
#     return render_template('jobsorder.html')


@app.route("/completed_orders")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def completed_orders():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id, type(org_id))
    completed_job_orders = (
        Joborder.query.filter(
            Joborder.vacancy == Joborder.filled_vacancy, Joborder.org_id == org_id
        )
        .order_by(desc(Joborder.id))
        .all()
    )
    # for completed_job_orders in completed_job_orders:
    #     print(type(completed_job_orders.org_id))

    return render_template("jobsorder.html", completed_job_orders=completed_job_orders)


@app.route("/archived_orders")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def archived_orders():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    archived_orders = (
        Joborder.query.filter(
            Joborder.archived == True,
            Joborder.jobstatus == "inactive",
            Joborder.org_id == org_id,
        )
        .order_by(desc(Joborder.id))
        .all()
    )
    return render_template("jobsorder.html", archived_orders=archived_orders)


@app.route("/Companies")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def Companies():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    page = request.args.get("page", default=1, type=int)
    per_page = 35
    unique_companies = {}
    all_companies = (
        Marketing.query.filter(Marketing.org_id == org_id)
        .order_by(desc(Marketing.created_at))
        .all()
    )
    company_activity = (
        db.session.query(Deals_history)
        .filter(Deals_history.org_id == org_id)
        .order_by(desc(Deals_history.id))
        .all()
    )

    for company in all_companies:
        if company.company not in unique_companies:
            unique_companies[company.company] = company
        else:
            if company.created_at > unique_companies[company.company].created_at:
                unique_companies[company.company] = company

    companies = list(unique_companies.values())

    total_records = len(companies)
    total_pages = ceil(total_records / per_page)
    start_page = max(1, page - 5)
    end_page = min(total_pages, start_page + 10)

    # Slice the companies list to get the subset for the current page
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    displayed_companies = companies[start_index:end_index]

    return render_template(
        "/companies.html",
        company_activity=company_activity,
        companies=displayed_companies,
        page=page,
        total_pages=total_pages,
        start_page=start_page,
        end_page=end_page,
    )


@app.route("/company_detail/<int:id>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def company_detail(id):
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    with db.session() as rsession:
        company_data = (
            rsession.query(Marketing)
            .filter(Marketing.id == id, Marketing.org_id == org_id)
            .order_by(desc(Marketing.created_at))
            .all()
        )

        if not company_data:
            return "Company not found", 404

        candidate = company_data[0]
        company = candidate.company

        # Retrieve job orders associated with the specified company from company_data
        company_job_orders = (
            rsession.query(Joborder)
            .filter(Joborder.company_id == id, Joborder.org_id == org_id)
            .all()
        )

        person = candidate.cperson
        phone = candidate.cphone

        additional_data = (
            rsession.query(Marketing)
            .filter(
                or_(
                    and_(
                        Marketing.company == company,
                        not_(and_(Marketing.id == id, Marketing.org_id == org_id)),
                    ),
                    and_(
                        Marketing.cperson == person,
                        not_(and_(Marketing.id == id, Marketing.org_id == org_id)),
                    ),
                    and_(
                        Marketing.cphone == phone,
                        not_(and_(Marketing.id == id, Marketing.org_id == org_id)),
                    ),
                )
            )
            .distinct()
            .all()
        )

        # Retrieve job orders associated with companies in additional_data
        additional_job_orders = []
        for data in additional_data:
            additional_company = data.id
            additional_job_orders.extend(
                rsession.query(Joborder)
                .filter(Joborder.company_id == additional_company)
                .all()
            )

        # Combining initial company data with additional matching data
        alldata = company_data + additional_data

    # Combining all job orders
    all_job_orders = company_job_orders + additional_job_orders
    print(all_job_orders, "all_job_orders")

    return render_template(
        "company_detail.html", alldata=alldata, job_orders=all_job_orders
    )


@app.route("/archive_jobs", methods=["POST"])
def archive_jobs():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    selected_job_ids = [
        int(job_id) for job_id in request.form.getlist("selected_jobs[]")
    ]
    print(
        "Selected Job IDs:", selected_job_ids
    )  # Print the list of selected job IDs for debugging purposes

    for job_id in selected_job_ids:
        job = Joborder.query.get(job_id)
        if job:
            print(job)
            if job.archived:  # If job is archived, unarchive it
                job.archived = False
                job.jobstatus = "active"
            else:  # If job is not archived, archive it
                job.archived = True
                job.jobstatus = "inactive"

            if "user_id" in session:
                user_id = request.cookies.get('user_id')
                user_name = db.session.query(Users).filter_by(id=user_id).first()
                current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
                archive_status = "archived" if job.archived else "unarchived"
                user_statement = f"joborder '{job.title}'  is {archive_status}  by {user_name.fname} {user_name.lname} ({current_time}) "
                print(user_statement)

                # After creating the history entry
                memberhistory = Joborder_history(
                    joborder_id=job.id,
                    notes=user_statement,
                    org_id=org_id,
                    created_at=datetime.utcnow(),
                )
                db.session.add(memberhistory)
                db.session.commit()

            db.session.commit()  # Commit the changes to the database

    return redirect(url_for("jobOders"))


@app.route("/archive_companies", methods=["POST"])
def archive_companies():
    selected_company_ids = [
        int(company_id) for company_id in request.form.getlist("selected_company[]")
    ]
    print(
        "Selected Company IDs:", selected_company_ids
    )  # Print the list of selected company IDs for debugging purposes

    for company_id in selected_company_ids:
        company = Marketing.query.get(company_id)
        if company:
            print(company)
            # Toggle the company status
            if company.company_status == "active":
                company.company_status = "inactive"
            else:
                company.company_status = "active"

            # Update associated job orders based on the new status of the company
            job_orders = Joborder.query.filter_by(company_id=company_id).all()
            for job_order in job_orders:
                job_order.archived = company.company_status == "inactive"

            db.session.commit()  # Commit the changes to the database

    return redirect(url_for("Companies"))


@app.route("/position", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def position():
    data = request.get_json()
    selectedOption = data.get("companyName")
    # print(selectedOption)
    positions = Joborder.query.filter(
        and_(
            Joborder.company_name == selectedOption,
            Joborder.jobstatus == "active",
            Joborder.archived == False,
        )
    ).all()
    positions_list = [{"position_name": position.title} for position in positions]

    return jsonify({"positions": positions_list})


@app.route("/otherfinal", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def otherfinal():
    if request.method == "POST":
        org_id = request.cookies.get('org_id')
        print("org_id", org_id)
        user_id = request.form.get("user_id")
        name = request.form.get("name")
        otherreport = request.form.get("otherreport")
        notes = request.form.get("notes")
        formtype = "Other Final"
        status = "Other Report"
        candidate = "-"
        id = request.form.get("id")
        if id is not None:
            entry = db.session.query(Otherfinal).filter_by(id=id).first()
            entry.other_report = otherreport
            entry.notes = notes
            db.session.add(entry)
            db.session.commit()
        else:
            entry = Otherfinal(
                user_id=user_id,
                name=name,
                other_report=otherreport,
                notes=notes,
                org_id=org_id,
            )

            db.session.add(entry)
            db.session.commit()
            submitted_id = entry.id

            forms = allforms_data(
                user_id=user_id,
                form_id=submitted_id,
                filledby=name,
                belongsto=candidate,
                form_type=formtype,
                status=status,
                org_id=org_id,
            )
            db.session.add(forms)
            db.session.commit()
            if "user_id" in session:
                user_id = request.cookies.get('user_id')
            user_name = db.session.query(Users).filter_by(id=user_id).first()
            current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
            user_statement = f"Other report is filled by {user_name.fname} {user_name.lname} ({current_time}) "
            print(user_statement)

            other_report = otherreport_history(
                other_id=submitted_id,
                notes=user_statement,
                org_id=org_id,
                created_at=datetime.utcnow(),
            )
            db.session.add(other_report)
            db.session.commit()
        response = jsonify({"message": "success"})
        response.status_code = 200
        return response
    else:
        # Handle other HTTP methods, if needed
        return "Unsupported method"


@app.route("/forms")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def forms():
    page = request.args.get("page", default=1, type=int)
    per_page = 150
    user_filter = request.args.get("userFilter")
    start_date = request.args.get("startDate")
    end_date = request.args.get("endDate")
    org_id = request.cookies.get('org_id')

    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    
    query = allforms_data.query.filter(allforms_data.org_id == org_id)

    if request.cookies.get("role") == "user":
        user_id = request.cookies.get('user_id')
        query = query.filter(allforms_data.user_id == user_id)
    elif user_filter:
        query = query.filter(allforms_data.user_id == user_filter)

    if start_date and end_date:
        # Convert start_date and end_date from strings to datetime objects
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(
            days=1
        )  # Extend end_date to include the whole day
        query = query.filter(
            allforms_data.created_at >= start_datetime,
            allforms_data.created_at < end_datetime,
        )

    # Calculate counts for different statuses
    status_counts = {
        "New deal opened and contract signed": query.filter_by(
            status="New deal opened and contract signed"
        ).count(),
        "New deal and contract not signed": query.filter_by(
            status="New deal and contract not signed"
        ).count(),
        "Reopened deals": query.filter_by(status="Reopened deals").count(),
        "Resume Sent": query.filter_by(status="Resume Sent").count(),
        "Interview Scheduled": query.filter_by(status="Interview Scheduled").count(),
        "Candidate Placement": query.filter_by(status="Candidate Placement").count(),
        "Help Another": query.filter_by(status="Help Another").count(),
    }

    total_records = query.count()
    total_pages = ceil(total_records / per_page)
    start_page = max(1, page - 5)
    end_page = min(total_pages, start_page + 10)

    alldata = (
        query.order_by(desc(allforms_data.id))
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    alldata_with_marketing_or_recruiting = []
    for data in alldata:
        marketing = Marketing.query.filter_by(
            id=data.form_id, name=data.filledby
        ).first()
        recruiting = recruiting_data.query.filter_by(
            id=data.form_id, name=data.filledby
        ).first()
        otherfinal = Otherfinal.query.filter_by(
            id=data.form_id, name=data.filledby
        ).first()
        hrforms = Hrforms.query.filter_by(id=data.form_id, name=data.filledby).first()

        appendable = marketing or recruiting or otherfinal or hrforms
        if appendable:
            alldata_with_marketing_or_recruiting.append((data, appendable))

    users = Users.query.filter(Users.org_id == org_id).all()

    return render_template(
        "forms.html",
        alldata_with_marketing_or_recruiting=alldata_with_marketing_or_recruiting,
        page=page,
        total_pages=total_pages,
        start_page=start_page,
        end_page=end_page,
        users=users,
        status_counts=status_counts,
        session= session,
    )


@app.route("/onereporting")
@app.route("/OneReportingForm")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def OneReportingForm():
    org_id = request.cookies.get('org_id')
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')

    print("org_id", org_id)
    companies = Marketing.query.filter(
        Marketing.company_status == "active", Marketing.org_id == org_id
    ).all()

    # Convert each Marketing object to a dictionary representation
    company_data = []
    for company in companies:
        company_dict = {
            "id": company.id,
            "company_name": company.company,
            "contact_person": company.cperson,
            "contact_person_name": company.cphone,
            "substatus": company.substatus,
            # Add more attributes as needed
        }
        company_data.append(company_dict)

    return render_template(
        "/onereporting-form.html", company=company_data, companies=companies
    )


@app.route("/getregistered")
def getregistered(data=None):
    return render_template("getregistered.html", data=data)


UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/addnewemployeetodata", methods=["POST"])
def addnewemployeetodata():
    if request.method == "POST":
        org_id = request.cookies.get('org_id')
        print("org_id", org_id)
        sender_name = request.form.get("candidate_name")
        email = request.form.get("email")
        current_date = request.form.get("date")
        phone = request.form.get("phone_number")
        description = request.form.get("description")
        notes = request.form.get("notes")
        uploaded_file = request.files["myFile"]

        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            file_content = uploaded_file.read()

        else:
            filename = "manually"
            file_content = None

        apply = Emails_data(
            sender_name=sender_name,
            email=email,
            phone_number=phone,
            subject_part2=description,
            formatted_date=current_date,
            file_name=filename,
            file_content=file_content,
            pdf_content_json=None,
            subject_part1="registered from Geox hr",
            action="",
            notes=notes,
            org_id=org_id,
        )

        db.session.add(apply)
        db.session.commit()

        response = jsonify({"message": "success"})
        response.status_code = 200
        return response
    else:
        return redirect("/getregistered")


@app.route("/addmanualemployee")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def addmanualemployee(data=None):
    return render_template("addnewemployee.html", data=data)


@app.route("/addmanualemployeetodata", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def addmanualemployeetodata():
    if request.method == "POST":
        org_id = request.cookies.get('org_id')
        print("org_id", org_id)
        sender_name = request.form.get("candidate_name")
        email = request.form.get("email")
        existing_record = Emails_data.query.filter_by(
            sender_name=sender_name, email=email
        ).first()
        if existing_record:
            response = jsonify({"message": "Already exists"})
            response.status_code = 400  # Bad Request
            return response

        current_date = request.form.get("date")
        phone = request.form.get("phone_number")
        description = request.form.get("description")
        notes = request.form.get("notes")

        uploaded_file = request.files["myFile"]
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            file_content = uploaded_file.read()
        else:
            filename = "manually"
            file_content = None

        apply = Emails_data(
            sender_name=sender_name,
            email=email,
            phone_number=phone,
            subject_part2=description,
            formatted_date=current_date,
            file_name=filename,
            file_content=file_content,  # Store the file content as BLOB
            pdf_content_json=None,  # You can handle PDF content as needed
            subject_part1="manually",
            action="",
            org_id=org_id,  # Empty notes field in Emails_data since notes are saved in Can_notes table
            notes="",
        )

        db.session.add(apply)
        db.session.commit()
        if notes:
            if "user_id" in session:
                user_id = request.cookies.get('user_id')
                user_name = db.session.query(Users).filter_by(id=user_id).first()
                name = f"{user_name.fname} {user_name.lname}"
            new_document = Can_notes(
                emails_data_id=apply.id, notes=notes, name=name, org_id=org_id
            )
            db.session.add(new_document)
            db.session.commit()
        if "user_id" in session:
            user_id = request.cookies.get('user_id')
            user_name = db.session.query(Users).filter_by(id=user_id).first()
            current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
            user_statement = f"Candidate name as {sender_name} is manually added by {user_name.fname} {user_name.lname} ({current_time}) "
            print(user_statement)

            # After creating the history entry
            candidate = candidate_history(
                candidate_id=apply.id,  # Assuming 'order' is the newly added Joborder object
                notes=user_statement,
                org_id=org_id,
                created_at=datetime.utcnow(),
            )
            db.session.add(candidate)
            db.session.commit()

        response = jsonify({"message": "success"})
        response.status_code = 200
        return response
    else:
        return redirect("/addmanualemployee")


@app.route("/view/<int:form_id>/<string:form_type>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def view(form_id, form_type):
    type = "view"
    org_id = request.cookies.get('org_id')
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')

    print("org_id", org_id)
    if form_type == "New Deals Contract Signed" or form_type == "Marketing":
        formdata = Marketing.query.filter(
            Marketing.id == form_id, Marketing.org_id == org_id
        ).first()
        jobsdata = Joborder.query.filter(
            Joborder.company_id == form_id, Joborder.org_id == org_id
        ).all()
        # print(*jobsdata)
        return render_template(
            "marketing.html", type=type, formdata=formdata, jobsdata=jobsdata, session=session
        )
    elif form_type == "Person Placement":
        formdata = recruiting_data.query.filter(
            recruiting_data.id == form_id, recruiting_data.org_id == org_id
        ).first()
        content = (
            b64encode(formdata.content).decode("utf-8") if formdata.content else None
        )

        company = Marketing.query.filter(Marketing.org_id == org_id).all()
        return render_template(
            "recruiting.html",
            type=type,
            formdata=formdata,
            company=company,
            content=content,
            session=session,
        )

    elif form_type == "HR Forms":
        formdata = Hrforms.query.filter(
            Hrforms.id == form_id, Hrforms.org_id == org_id
        ).first()
        return render_template("hrforms.html", type=type, formdata=formdata, session=session)
    elif form_type == "Other Final":
        formdata = Otherfinal.query.filter(
            Otherfinal.id == form_id, Otherfinal.org_id == org_id
        ).first()
        return render_template("otherreport.html", type=type, formdata=formdata, session=session)


@app.route("/placecontent/<int:email_id>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def placecontent(email_id):
    email = recruiting_data.query.filter(recruiting_data.id == email_id).first()

    if email and email.content:
        file_name = email.file_name
        file_content = email.content

        # Get the file extension
        _, file_extension = os.path.splitext(file_name)

        # Set the mimetype based on the file extension
        mimetype = mimetypes.types_map.get(
            file_extension.lower(), "application/octet-stream"
        )

        response = send_file(io.BytesIO(file_content), mimetype=mimetype)

        return response

    return jsonify({"error": "PDF not found"}), 404


@app.route("/editforms/<int:form_id>/<string:form_type>")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def editforms(form_id, form_type):
    type = "edit"
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    session = {}
    session["user_id"] = request.cookies.get('user_id')
    session["role"] = request.cookies.get('role')
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    if form_type == "New Deals Contract Signed":
        formdata = Marketing.query.filter(Marketing.id == form_id).first()
        jobsdata = Joborder.query.filter(
            Joborder.company_id == form_id, Joborder.org_id == org_id
        ).all()
        return render_template(
            "marketing.html", type=type, formdata=formdata, jobsdata=jobsdata, session=session
        )
    elif form_type == "Person Placement":
        formdata = recruiting_data.query.filter(recruiting_data.id == form_id).first()
        company = Marketing.query.all()
        return render_template(
            "recruiting.html", type=type, formdata=formdata, company=company, session=session
        )
    elif form_type == "HR Forms":
        formdata = Hrforms.query.filter(Hrforms.id == form_id).first()
        return render_template("hrforms.html", type=type, formdata=formdata, session=session)
    elif form_type == "Other Final":
        formdata = Otherfinal.query.filter(Otherfinal.id == form_id).first()
        return render_template("otherreport.html", type=type, formdata=formdata, session=session)


@app.route("/candidate_login")
def candidate_login():
    return render_template("candidate_login.html")


@app.route("/logincandidate", methods=["GET", "POST"])
def logincandidate():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = candidateLogin.query.filter_by(email=email).first()
        if user and user.password == password:
            return redirect(url_for("viewhistory", email=email))
        else:
            return render_template("candidate_login.html", msg="Invalid credentials")

    return render_template("candidate_login.html")


@app.route("/viewhistory/<string:email>")
def viewhistory(email):
    with db.session() as session:
        org_id = request.cookies.get('org_id')
        print("org_id", org_id)
        alldata = (
            session.query(Emails_data)
            .filter(Emails_data.email == email, Emails_data.org_id == org_id)
            .order_by(desc(Emails_data.created_at))
            .all()
        )
        sender_name = (
            session.query(Emails_data.sender_name)
            .filter(Emails_data.email == email, Emails_data.org_id == org_id)
            .first()
        )
        if sender_name:
            sender_name = sender_name[0]
            recruiting = (
                session.query(recruiting_data)
                .filter(
                    recruiting_data.candidate == sender_name,
                    recruiting_data.org_id == org_id,
                )
                .all()
            )
        else:
            recruiting = []
    # return render_template('forcandidate_view.html', alldata=alldata, recruiting=recruiting)
    return render_template("viewhistory.html", alldata=alldata, recruiting=recruiting)


@app.route("/deleteform/<int:form_id>/<string:form_type>", methods=["POST"])
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def deleteform(form_id, form_type):
    org_id = request.cookies.get('org_id')
    user_name = request.cookies.get("user")
    current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
    print("org_id", form_type, user_name, org_id)
    user_statement = ""  # Initialize user_statement with a default value
    cleaned_user_statement = ""
    try:
        db.session.query(allforms_data).filter(
            allforms_data.form_id == form_id, allforms_data.form_type == form_type
        ).delete()
        db.session.commit()

        if form_type == "Marketing":
            marketing_data = (
                db.session.query(Marketing.company)
                .filter(Marketing.id == form_id)
                .first()
            )
            marketing_status = (
                db.session.query(Marketing.status)
                .filter(Marketing.id == form_id)
                .first()
            )
            joborder_data = (
                db.session.query(Joborder.title)
                .filter(Joborder.company_id == form_id)
                .all()
            )

            # Delete the form from allforms_data table
            db.session.query(allforms_data).filter(
                allforms_data.form_id == form_id, allforms_data.form_type == form_type
            ).delete()
            db.session.commit()

            # Construct user statement with joborder names
            joborder_names = ", ".join(job[0] for job in joborder_data)
            user_statement = f"{user_name} deleted {marketing_status} for company '{marketing_data[0]}' with joborders: {joborder_names} ({current_time})"

        elif form_type == "Person Placement":
            placement_can = (
                db.session.query(recruiting_data.candidate)
                .filter(recruiting_data.id == form_id)
                .first()
            )
            placement_did = (
                db.session.query(recruiting_data.did_you)
                .filter(recruiting_data.id == form_id)
                .first()
            )
            placement_comp = (
                db.session.query(recruiting_data.company)
                .filter(recruiting_data.id == form_id)
                .first()
            )

            db.session.query(recruiting_data).filter(
                recruiting_data.id == form_id
            ).delete()
            user_statement = f"{user_name} deleted {placement_did} of {placement_can} ({current_time}) "

        elif form_type == "HR Forms":
            hr_can = (
                db.session.query(Hrforms.candidate_name)
                .filter(Hrforms.id == form_id)
                .first()
            )
            db.session.query(Hrforms).filter(Hrforms.id == form_id).delete()
            user_statement = (
                f"{user_name} deleted HR Form of {hr_can} ({current_time}) "
            )

        elif form_type == "Other Final":
            ot_can = (
                db.session.query(Otherfinal.name)
                .filter(Otherfinal.id == form_id)
                .first()
            )
            db.session.query(Otherfinal).filter(Otherfinal.id == form_id).delete()
            user_statement = (
                f"{user_name} deleted Other report of {ot_can} ({current_time}) "
            )

        cleaned_user_statement = re.sub(r"[,\(\)]", "", user_statement)
        print(cleaned_user_statement)
        deldata = Deletedata(
            delete_id=form_id,  # Assuming 'order' is the newly added Joborder object
            notes=user_statement,
            org_id=org_id,
            created_at=datetime.utcnow(),
        )
        db.session.add(deldata)
        db.session.commit()
        return jsonify({"message": "Form Deleted!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error deleting form: {str(e)}"}), 500


@app.route("/target")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def target():
    user_id = request.cookies.get('user_id')
    role = request.cookies.get("role")
    org_id = request.cookies.get('org_id')
    session = {}
    session["user_id"] = user_id
    session["role"] = role
    session["org_id"] = request.cookies.get('org_id')
    session["email"] = request.cookies.get('email')
    session["user"] = request.cookies.get('user')
    print("org_id", org_id)
    if role == "user":
        members_data = (
            Targets.query.filter(Targets.user_id == user_id, Targets.org_id == org_id)
            .order_by(desc(Targets.id))
            .all()
        )
    else:
        members_data = (
            Targets.query.filter(Targets.org_id == org_id)
            .order_by(desc(Targets.id))
            .all()
        )

    # Iterate over each item in members_data
    for member in members_data:
        print(member.new_achieve, "members_data")

    return render_template("/target.html", members_data=members_data, session=session)


@app.route("/addtarget")
@role_required(allowed_roles=["user", "admin", "owner", "CEO"])
def addtarget():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    members_data = (
        Users.query.filter(
            Users.designation != "owner",
            Users.org_id == org_id,
            Users.status == "Active",
        )
        .order_by(desc(Users.id))
        .all()
    )
    score_data = score_board.query.all()
    return render_template(
        "/addtarget.html", members_data=members_data, score_data=score_data
    )


@app.route("/edit_target")
def edit_target():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    selected_week = request.args.get("selectedWeek")
    selected_week_data = (
        Targets.query.filter(
            Targets.weekstart == selected_week, Targets.org_id == org_id
        )
        .order_by(desc(Targets.id))
        .all()
    )
    print("Selected Week:", selected_week, selected_week_data)

    return render_template("/addtarget.html", selected_week_data=selected_week_data)


@app.route("/resettarget", methods=["POST"])
def resettarget():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    if request.method == "POST":
        ids = request.form.getlist("id")
        weekstart = request.form.getlist("weekstart")
        weekend = request.form.getlist("weekend")
        user_ids = request.form.getlist("user_id")
        names = request.form.getlist("name")
        news = request.form.getlist("new")
        notsigneds = request.form.getlist("notsigned")
        reopens = request.form.getlist("reopen")
        resumes = request.form.getlist("resume")
        interviews = request.form.getlist("interview")
        placements = request.form.getlist("placement")
        helpings = request.form.getlist("helping")
        targets = request.form.getlist("target")
        scores = request.form.getlist("score")
        blue = 3
        green = 2
        yellow = 1
        print(
            "Lengths:",
            len(user_ids),
            len(names),
            len(news),
            len(notsigneds),
            len(reopens),
            len(resumes),
            len(interviews),
            len(placements),
            len(helpings),
            len(targets),
            len(scores),
        )
        print("User IDs:", user_ids)
        print("Names:", names)

        print("Week start:", ids, weekstart, weekend, user_ids, names, news)
        print(weekstart, weekend)
        for i in range(len(user_ids)):
            id = int(ids[i])  # Convert id to integer
            user_id = user_ids[i]
            name = names[i]
            new = int(news[i]) if news[i] else 0
            notsigned = int(notsigneds[i]) if notsigneds[i] else 0
            reopen = int(reopens[i]) if reopens[i] else 0
            resume = int(resumes[i]) if resumes[i] else 0
            interview = int(interviews[i]) if interviews[i] else 0
            placement = int(placements[i]) if placements[i] else 0
            helping = int(helpings[i]) if helpings[i] else 0
            target = new + notsigned + reopen + resume + interview + placement + helping
            score = (
                new * blue
                + notsigned * green
                + reopen * yellow
                + resume * green
                + interview * green
                + placement * blue
                + helping * yellow
            )
            print(type(new), "type")

            # Use update method
            weekstart_date = datetime.strptime(weekstart[i], "%Y-%m-%d %H:%M:%S").date()
            weekend_date = datetime.strptime(weekend[i], "%Y-%m-%d %H:%M:%S").date()

            # Use update method
            Targets.query.filter(
                and_(
                    Targets.id == id,
                    Targets.user_id == user_id,
                    Targets.weekstart == weekstart_date,
                    Targets.weekend == weekend_date,
                )
            ).update(
                {
                    "new": new,
                    "notsigned": notsigned,
                    "reopen": reopen,
                    "resume": resume,
                    "interview": interview,
                    "placement": placement,
                    "helping": helping,
                    "target": target,
                    "score": score,
                }
            )

        db.session.commit()
        response = jsonify({"message": "success"})
        response.status_code = 200
        return response
    else:
        return redirect("/target")


@app.route("/savetarget", methods=["POST"])
def savetarget():
    org_id = request.cookies.get('org_id')
    print("org_id", org_id)
    if request.method == "POST":
        user_ids = request.form.getlist("user_id")
        names = request.form.getlist("name")
        news = request.form.getlist("new")
        notsigneds = request.form.getlist("notsigned")
        reopens = request.form.getlist("reopen")
        resumes = request.form.getlist("resume")
        interviews = request.form.getlist("interview")
        placements = request.form.getlist("placement")
        helpings = request.form.getlist("helping")
        targets = request.form.getlist("target")
        scores = request.form.getlist("score")
        blue = 3
        green = 2
        yellow = 1
        print(
            "Lengths:",
            len(user_ids),
            len(names),
            len(news),
            len(notsigneds),
            len(reopens),
            len(resumes),
            len(interviews),
            len(placements),
            len(helpings),
            len(targets),
            len(scores),
        )
        print("User IDs:", user_ids)
        print("Names:", names)

        today = datetime.today()
        print("today", today)
        days_to_saturday = today.weekday()
        saturday = today - timedelta(days=days_to_saturday)
        friday = saturday + timedelta(days=6)
        weekstart = saturday.strftime("%Y-%m-%d")
        weekend = friday.strftime("%Y-%m-%d")
        print("Week start:", weekstart)
        print("Week end:", weekend)

        print(weekstart, weekend)
        for i in range(len(user_ids)):
            user_id = user_ids[i]
            name = names[i]
            new = int(news[i]) if news[i] else 0
            notsigned = int(notsigneds[i]) if notsigneds[i] else 0
            reopen = int(reopens[i]) if reopens[i] else 0
            resume = int(resumes[i]) if resumes[i] else 0
            interview = int(interviews[i]) if interviews[i] else 0
            placement = int(placements[i]) if placements[i] else 0
            helping = int(helpings[i]) if helpings[i] else 0
            target = new + notsigned + reopen + resume + interview + placement + helping
            score = (
                new * blue
                + notsigned * green
                + reopen * yellow
                + resume * green
                + interview * green
                + placement * blue
                + helping * yellow
            )
            print(type(new), "type")
            existing_entry = Targets.query.filter_by(
                org_id=org_id, user_id=user_id, weekstart=weekstart, weekend=weekend
            ).first()

            if existing_entry:
                # Update existing entry
                existing_entry.new = new
                existing_entry.notsigned = notsigned
                existing_entry.reopen = reopen
                existing_entry.resume = resume
                existing_entry.interview = interview
                existing_entry.placement = placement
                existing_entry.helping = helping
                existing_entry.target = target
                existing_entry.score = score
            else:
                # Add new entry
                target_data = Targets(
                    org_id=org_id,
                    user_id=user_id,
                    name=name,
                    new=new,
                    notsigned=notsigned,
                    reopen=reopen,
                    resume=resume,
                    interview=interview,
                    placement=placement,
                    helping=helping,
                    target=target,
                    score=score,
                    weekstart=weekstart,
                    weekend=weekend,
                )
                db.session.add(target_data)

        db.session.commit()
        # Now, retrieve emails based on the user_ids
        user_emails = (
            Users.query.filter(
                Users.id.in_(user_ids),
                Users.designation != "owner",
                Users.status == "Active",
                Users.org_id == org_id,
            )
            .with_entities(Users.email)
            .all()
        )

        # Extract the emails from the query result
        emails = [email[0] for email in user_emails]
        print(emails)
        # recipients = ['nhoorain161@gmail.com']
        rcpt = ["nisa@i8is.com"]
        if org_id:
            tocred = org_cred.query.filter(org_cred.org_id == org_id).first()
            if tocred:
                toemail = tocred.noti_email
                rcpt.append(toemail)
        recipients = rcpt
        # recipients = ['nhoorain161@gmail.com']

        recipients2 = emails
        user_name = request.cookies.get("user")
        user_email = request.cookies.get("email")

        try:
            user_name = request.cookies.get("user")
            user_email = request.cookies.get("email")
            email_subject = f"""Weekly Target Added """
            email_body = f"""
                               <!DOCTYPE html>
                               <html>
                               <head>
                                   <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f0f0f0;
                margin: 0;
                padding: 0; 
            }}
            .container {{
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                overflow: hidden;
                margin: 15px 0px;
                padding: 20px;
                max-width: 800px;
                margin:auto;

            }}
            .cont-img{{
                            width: 34%;
                            margin: auto;
                            display: block;
                            margin-bottom:20px
            }}
            .header {{
                background-color: #007bff;
                color: #ffffff;
                padding: 10px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            h2 {{
                margin: 0;
            }}
            p {{
                margin: 10px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #dddddd;
                text-align:center;
                padding:3px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .signature {{
                                              margin-top: 20px;
                                              font-size:15px
                                          }}
                                          .signature p {{
                                              margin: 0px;
                                          }}
                                          .signature2 p {{
                                              margin: 0px;
                                              text-align: center;
                                          }}
                                          .hello{{
                                            border: 1px solid #19355f;
                                            margin-bottom: 28px;
                                          }}
                                          .signature2 {{
                                                  padding: 7px;
                                                background: #ffff;
                                                margin-top: 21px;
                                          }}
            .geoxhr {{
                width: 100px;
                margin-top: 10px;
            }}
        </style>
                               </head>
                               <body>
                                   <div class="container">
					<img class="cont-img" src="{{ url_for('static', filename='img/clickhr.png') }}">
                                         <div class="hello"></div>
                                       
                                       <p>I hope this email finds you well. I wanted to inform you that weekly tasks have been assigned {user_name} to our users for the current week. This includes a breakdown of tasks for each user to ensure clarity and accountability.Dive into the details below:</p>

                                       <table id="targetTable">
                                           <tr>
                                               <th>Name</th>
                                               <th>New Contrat</th>
                                               <th>Not signed</th>
                                               <th>ReopenDeals</th>
                                               <th>ResumeSents</th>
                                               <th>Interviews</th>
                                               <th>Placements</th>
                                               <th>Helpings</th>
                                               <th>Total</th>
                                           </tr>
                               """
            for i in range(len(user_ids)):
                new_target = int(news[i]) if news[i] else 0
                notsigned_target = int(notsigneds[i]) if notsigneds[i] else 0
                reopen_target = int(reopens[i]) if reopens[i] else 0
                resume_target = int(resumes[i]) if resumes[i] else 0
                interview_target = int(interviews[i]) if interviews[i] else 0
                placement_target = int(placements[i]) if placements[i] else 0
                helping_target = int(helpings[i]) if helpings[i] else 0

                target = (
                    new_target
                    + notsigned_target
                    + reopen_target
                    + resume_target
                    + interview_target
                    + placement_target
                    + helping_target
                )
                score = (
                    new_target * blue
                    + notsigned_target * green
                    + reopen_target * yellow
                    + resume_target * green
                    + interview_target * green
                    + placement_target * blue
                    + helping_target * yellow
                )

                email_body += f"""
                    <tr>
                        <td>{names[i]}</td>
                        <td>{new_target}</td>
                        <td>{notsigned_target}</td>
                        <td>{reopen_target}</td>
                        <td>{resume_target}</td>
                        <td>{interview_target}</td>
                        <td>{placement_target}</td>
                        <td>{helping_target}</td>
                        <td>Target: {target}<br>Score: {score}</td>
                    </tr>
                """
            email_body += f"""
                                       </table>

                                       
                                     <div class="signature2">
                                             <p>If assistance is required, feel free to reach out to us at:</p>
                                             <p>clickhr@click-hr.com.</p>
                                             <p> +1 647-930-0988</p>
                                          </div>
                                   </div>
                               </body>
                               </html>
                           """
        except:
            pass
        msg = Message(subject=email_subject, recipients=recipients, html=email_body)
        mail.send(msg)
        try:
            user_email_subject = "Weekly Tasks Assigned"
            user_email_body = f"""
             
             <!DOCTYPE html>
                                 <html>
                                 <head>
                                      <style>
                                         body {{
                                             font-family: Arial, sans-serif;
                                         }}
                                         .container {{
                                             background-color: #f2f2f2;
                                             padding: 20px;
                                             border-radius: 10px;
                                             max-width: 800px;
                                             margin: auto;
                                         }}
                                         .cont-img{{
                                             width: 34%;
                                             margin: auto;
                                             display: block;
                                             margin-bottom:20px
                                         }}
                                         .details {{
                                             margin-top: 10px;
                                         }}
                                         .details p {{
                                             margin: 0;
                                         }}
                                         .bold {{
                                             font-weight: bold;
                                         }}
                                         .signature {{
                              margin-top: 20px;
                              font-size:15px
                          }}
                          .signature p {{
                                margin: 0px;
                          }}
                          .signature2 p {{
                                margin: 0px;
                                text-align: center;
                          }}
                          .hello{{
                                 border: 1px solid #19355f;
                                 margin-bottom: 28px;
                          }}
                          .signature2 {{
                                  padding: 7px;
                                  background: #ffff;
                                  margin-top: 21px;
                          }}
                                         .geoxhr {{
                                                width: 100px;
                                               margin-top: 10px;
                                         }}
                                     </style>
                                 </head>
                                 <body>
                                     <div class="container">
                                         <img class="cont-img" src="{{ url_for('static', filename='img/clickhr.png') }}">
                                         <div class="hello"></div>

                                        <p>We hope this email finds you well. We wanted to inform you that your weekly tasks have been assigned by {user_name} </p>


                                         <div class="signature">
                              <p>Thankyou.</p>

                           </div>
                          <div class="signature2">
                               <p>If assistance is required, feel free to reach out to us at:</p>
                               <p>clickhr@click-hr.com.</p>
                               <p> +1 647-930-0988</p>
                          </div>
                                     </div>
                                 </body>
                                 </html>
                """
            user_msg = Message(
                subject=user_email_subject, recipients=emails, html=user_email_body
            )
            mail.send(user_msg)
        except Exception as e:
            pass
            print(f"Error sending user email to {user_email}: {str(e)}")

        response = jsonify({"message": "success"})
        response.status_code = 200
        return response
    else:
        return redirect("/target")


@app.route("/bugreport", methods=["POST"])
def bugreport():
    org_id = request.cookies.get('org_id')
    org_name = request.cookies.get('org_name')
    print("org_id", org_id)
    if request.method == "POST":
        user_name = request.form.get("user_name")
        user_email = request.form.get("user_email")
        description = request.form.get("description")
        myfiles = request.files.getlist("myfiles")
        print(request.files, myfiles)  # This will show all file data received
        if "myfiles" in request.files:
            file = request.files["myfiles"]
            print(file.filename)

        try:
            email_subject = f"""Bug Report from {org_name} """
            email_body = f"""
                               <!DOCTYPE html>
                               <html>
                               <head>
                                   <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f0f0f0;
                margin: 0;
                padding: 0; 
            }}
            .container {{
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                overflow: hidden;
                margin: 15px 0px;
                padding: 20px;
                max-width: 800px;
                margin:auto;
            }}
            .cont-img{{
                            width: 34%;
                            margin: auto;
                            display: block;
                            margin-bottom:20px
            }}
            .header {{
                background-color: #007bff;
                color: #ffffff;
                padding: 10px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            h2 {{
                margin: 0;
            }}
            p {{
                margin: 10px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #dddddd;
                text-align:center;
                padding:3px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .signature {{
                margin-top: 20px;
                font-style: italic;
                font-size: 15px;
            }}
            .geoxhr {{
                width: 100px;
                margin-top: 10px;
            }}
            </style>
                               </head>
                               <body>
                                   <div class="container">
                                       <img class="cont-img" src="{{ url_for('static', filename='img/clickhr.png') }}">
                                         <div class="hello"></div>
                                       <p>Bug report send by  {user_name} with ({user_email}). </p>
                                       <p>Description:{description}</p>

                               </body>
                               </html>
            """
            msg = Message(
                subject=email_subject, recipients=["nisa@i8is.com"], html=email_body
            )
            # print(msg)
            # Attach files if any
            if "myfiles" in request.files:
                for screenshot in myfiles:
                    msg.attach(screenshot.filename, "image/png", screenshot.read())
            mail.send(msg)
            return jsonify({"msg": "Thank you for your report"}), 200
        except:
            print(f"Error sending user email to {user_email}")
            return jsonify({"msg": "Report not sent, try later!"}), 500
    else:
        pass


processed_orgs = []
processed_orgs_lock = threading.Lock()


def arc_mails_auto():
    with app.app_context():
        active_orgs = org_cred.query.filter_by(status="Active").all()
        if not active_orgs:
            print("No active organizations found.")
            return

        for org in active_orgs:
            rcpt = ["nisa@i8is.com", "contact@handshr.com"]
            # toem = org.noti_email
            # rcpt.append(toem)
            org_id = org.org_id
            active_jobs = Joborder.query.filter_by(
                org_id=org_id, archived=False, jobstatus="active"
            ).all()
            jobs_to_archive = []
            archived_count = 0

            for job in active_jobs:
                if (datetime.utcnow() - job.created_at) >= timedelta(days=45):
                    job.archived = True
                    job.jobstatus = "inactive"
                    jobs_to_archive.append(job)
                    current_time = datetime.utcnow().strftime("%b %d, %Y %I:%M%p")
                    user_statement = f"Joborder titled '{job.title}' has been archived because it has been active for more than 45 days ({current_time})"
                    print(user_statement)
                    history_entry = Joborder_history(
                        joborder_id=job.id,
                        notes=user_statement,
                        org_id=org_id,
                        created_at=datetime.utcnow(),
                    )
                    db.session.add(history_entry)
                    archived_count += 1

            db.session.commit()

            if not jobs_to_archive:
                print(f"No jobs found for archiving for organization {org_id}.")
                continue

            email_body = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            font-family: 'Arial', sans-serif;
                            background-color: #f0f0f0;
                            margin: 0;
                            padding: 0;
                        }}
                        .container {{
                            background-color: #ffffff;
                            border-radius: 10px;
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                            overflow: hidden;
                            margin: 15px 0px;
                            padding: 20px;
                            max-width: 800px;
                            margin:auto;
                        }}
                        .cont-img{{
                            width: 34%;
                            margin: auto;
                            display: block;
                            margin-bottom:20px
                          }}
                        .header {{
                            background-color: #007bff;
                            color: #ffffff;
                            padding: 10px;
                            text-align: center;
                            border-radius: 10px 10px 0 0;
                        }}
                        h2 {{
                            margin: 0;
                        }}
                        p {{
                            margin: 10px 0;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 20px;
                        }}
                        th, td {{
                            border: 1px solid #dddddd;
                            text-align: center;
                            padding: 3px;
                        }}
                        th {{
                            background-color: #f2f2f2;
                        }}
                        .signature {{
                            margin-top: 20px;
                            font-style: italic;
                            font-size: 15px;
                        }}
                        .geoxhr {{
                            width: 100px;
                            margin-top: 10px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                       <img class="cont-img" src="{{ url_for('static', filename='img/clickhr.png') }}">
                                         <div class="hello"></div>
                        <p>I hope this email finds you well. Here are the {archived_count} job orders from your organization that have been archived due to being active for more than 45 days:</p>
                        <table id="targetTable">
                            <tr>
                                <th>Company Name</th>
                                <th>Job Name</th>
                                <th>Created at</th>
                            </tr>
            """

            for job in jobs_to_archive:
                email_body += f"""
                            <tr>
                                <td>{job.company_name}</td>
                                <td>{job.title}</td>
                                <td>{job.created_at}</td>
                            </tr>
                """

            email_body += """
                        </table>
                        <div class="signature">
                              <p>Thank you.</p>

                           </div>
                          <div class="signature2">
                               <p>If assistance is required, feel free to reach out to us at:</p>
                               <p>clickhr@click-hr.com</p>
                               <p> +1 647-930-0988</p>
                          </div>
                    </div>
                </body>
                </html>
            """

            subj = "Archived Job Orders - Alert"
            recipients = rcpt
            user_email_subject = subj
            user_msg = Message(
                subject=user_email_subject, recipients=recipients, html=email_body
            )
            mail.send(user_msg)

            print(f"Email sent to {rcpt}")


def send_email():
    global processed_orgs
    with app.app_context():
        active_orgs = org_cred.query.filter_by(status="Active").all()

        if not active_orgs:
            print("No active organizations found.")
            return

        for org in active_orgs:
            org_id = org.org_id

            with processed_orgs_lock:
                if org_id in processed_orgs:
                    print(
                        f"Organization {org_id} has already been processed. Skipping."
                    )
                    continue
                processed_orgs.append(org_id)

            rcpt = ["nisa@i8is.com"]

            today = datetime.today()
            days_to_saturday = today.weekday()
            saturday = today - timedelta(days=days_to_saturday)
            friday = saturday + timedelta(days=6)
            weekstart = saturday.strftime("%Y-%m-%d")
            weekend = friday.strftime("%Y-%m-%d")
            print(f"Current Week: {weekstart} to {weekend}")

            members_data = (
                Targets.query.filter_by(
                    weekstart=weekstart, weekend=weekend, org_id=org_id
                )
                .order_by(Targets.id.desc())
                .all()
            )

            if not members_data:
                print(
                    f"No target data found for organization {org_id} for the week {weekstart} - {weekend}."
                )
                continue

            subj = f"Weekly Target Report ({weekstart} - {weekend})"
            email_body = """
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {
                            font-family: 'Arial', sans-serif;
                            background-color: #f0f0f0;
                            margin: 0;
                            padding: 0;
                        }
                        .container {
                            background-color: #ffffff;
                            border-radius: 10px;
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                            overflow: hidden;
                            margin: 15px 0px;
                            padding: 20px;
                            max-width: 800px;
                            margin:auto;
                        }
                        .cont-img {
                            width: 34%;
                            margin: auto;
                            display: block;
                            margin-bottom:20px
                        }
                        .header {
                            background-color: #007bff;
                            color: #ffffff;
                            padding: 10px;
                            text-align: center;
                            border-radius: 10px 10px 0 0;
                        }
                        h2 {
                            margin: 0;
                        }
                        p {
                            margin: 10px 0;
                        }
                        table {
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 20px;
                        }
                        th, td {
                            border: 1px solid #dddddd;
                            text-align:center;
                            padding:3px;
                        }
                        th {
                            background-color: #f2f2f2;
                        }
                        .signature {
                            margin-top: 20px;
                            font-style: italic;
                            font-size: 15px;
                        }
                        .geoxhr {
                            width: 100px;
                            margin-top: 10px;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <img class="cont-img" src="{{ url_for('static', filename='img/clickhr.png') }}">
                        <p>I hope this email finds you well. Here is the comprehensive weekly target report showcasing the remarkable achievements and progress of our dedicated team. Your insights and feedback are highly appreciated.</p>
                        <table id="targetTable">
                            <tr>
                                <th>Name</th>
                                <th>Target</th>
                                <th>Score</th>
                                <th>Score Percentage</th>
                            </tr>
            """
            for user in members_data:
                name = user.name
                total_target = user.target
                achieved_target = user.target_achieve
                total_score = user.score
                achieved_score = user.score_achieve
                achieved_percentage = user.achieve_percentage

                email_body += f"""
                            <tr>
                                <td>{name}</td>
                                <td>{achieved_target}/{total_target}</td>
                                <td>{achieved_score}/{total_score}</td>
                                <td>{achieved_percentage}%</td>
                            </tr>
                """

            email_body += """
                        </table>
                        <div class="signature">
                            <p>Thank you.</p>
                        </div>
                        <div class="signature2">
                            <p>If assistance is required, feel free to reach out to us at:</p>
                            <p>clickhr@click-hr.com</p>
                            <p>+1 647-930-0988</p>
                        </div>
                    </div>
                </body>
                </html>
            """

            user_email_subject = subj
            user_msg = Message(
                subject=user_email_subject, recipients=rcpt, html=email_body
            )
            try:
                mail.send(user_msg)
                print(f"Email sent to {rcpt}")
            except Exception as e:
                print(f"Failed to send email to {rcpt}: {e}")

            db.session.commit()



def reset_processed_orgs():
    global processed_orgs
    with processed_orgs_lock:
        processed_orgs = []
        print("Processed organizations list has been reset.")


def start_scheduler():
    schedule.every().day.at("09:30").do(send_email)
    schedule.every().day.at("09:30").do(arc_mails_auto)
    schedule.every().monday.at("00:00").do(reset_processed_orgs)
    while True:
        schedule.run_pending()
        time.sleep(60)


scheduler_thread = threading.Thread(target=start_scheduler)
scheduler_thread.start()