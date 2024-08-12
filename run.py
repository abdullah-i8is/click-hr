from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Text, Boolean, DateTime, or_
from sqlalchemy.orm import declarative_base, sessionmaker
import imaplib
import email
import io
from email.header import decode_header
import pdfplumber
from dateutil import parser
import json
from datetime import datetime, timedelta
import re
from flask import Flask
from flask_mail import Mail, Message
import requests
import os
from flask import Flask, render_template, send_file, jsonify, make_response
from flask_migrate import Migrate
from flask_minify import Minify
from sys import exit
from config import config_dict
from app import create_app, db
import schedule
import time
from app.model import *
from datetime import datetime, timedelta
from threading import Thread
import time
import pytesseract
from io import BytesIO
from PyPDF2 import PdfReader
from flask_cors import CORS

app = Flask(__name__)
# Initialize CORS


IMAP_SERVER = 'imap.gmail.com'
EMAIL_CREDENTIALS = []

app.config['MAIL_SERVER'] = 'smtp.mail.us-east-1.awsapps.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'clickhr@click-hr.com'
app.config['MAIL_PASSWORD'] = 'I8is123??'
app.config['MAIL_DEFAULT_SENDER'] = 'clickhr@click-hr.com'

mail = Mail(app)
Base = declarative_base()

class Emails_data(Base):
    __tablename__ = 'emails_data'
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, nullable=False)
    sender_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    subject_part1 = Column(String(255), nullable=False)
    subject_part2 = Column(String(255), nullable=False)
    formatted_date = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_content = Column(LargeBinary, nullable=True)
    pdf_content_json = Column(Text, nullable=True)
    phone_number = Column(String(255), nullable=True)
    action = Column(String(500), nullable=False, default='user')
    status = Column(String(500), nullable=False, default='applied')
    is_read = Column(Boolean, default=False)
    message_id = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.sender_name, self.subject_part2)

class OrgCred(Base):
    __tablename__ = 'org_cred'
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, nullable=False)
    company = Column(String(250), unique=False)
    noti_email = Column(String(250), unique=False)
    iemail = Column(String(250), unique=False)
    ipassword = Column(String(250))
    zemail = Column(String(250), unique=True)
    zpassword = Column(String(250))
    status = Column(String(250), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# engine = create_engine(
#      'mysql+pymysql://hayat:Hayat_admin123@35.183.134.169/geoxhrdb')
engine = create_engine('mysql+pymysql://hayat:Hayat_admin123@35.183.134.169/Clickhrin')
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

DEBUG = (os.getenv('DEBUG', 'False') == 'True')
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

if DEBUG:
    app.logger.info('DEBUG       = ' + str(DEBUG))
    app.logger.info('DBMS        = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT = ' + app_config.ASSETS_ROOT)

CORS(app)

last_email_sent = {}

def email_already_processed(message_id, org_id):
    existing_entry = session.query(Emails_data).filter_by(message_id=message_id, org_id=org_id).first()
    return existing_entry is not None

def fetch_data():
    try:
        with app.app_context():
            all_cred = session.query(OrgCred).filter(OrgCred.status == 'Active').all()
            for cred in all_cred:
                obj = {
                    'address': cred.iemail,
                    'password': cred.ipassword,
                    'org_id': cred.org_id
                }
                EMAIL_CREDENTIALS.append(obj)
                print(EMAIL_CREDENTIALS)
            for email_credentials in EMAIL_CREDENTIALS:
                email_address = email_credentials['address']
                password = email_credentials['password']
                if not email_address or not password:
                    continue
                org_id = email_credentials['org_id']
                server = imaplib.IMAP4_SSL(IMAP_SERVER, port=993)

                try:
                    server.login(email_address, password)
                    server.select('INBOX')

                    current_datetime = datetime.now()
                    current_date = current_datetime.strftime('%d-%b-%Y')
                    search_criteria = f'(SINCE {current_date})'
                    _, msg_ids = server.search(None, search_criteria)
                    recent_msg_ids = msg_ids[0].split()

                    for msg_id in recent_msg_ids:
                        try:
                            _, msg_data = server.fetch(msg_id, '(RFC822)')
                            raw_message = msg_data[0][1]
                            if raw_message is None:
                                print(f"No data fetched for email with ID: {msg_id}")
                                continue
                            message = email.message_from_bytes(raw_message)
                            message_id = message.get('Message-ID')
                            if email_already_processed(message_id, org_id):
                                continue
                            if '=?' in message.get('Subject'):
                                continue
                            sender_name = email.utils.parseaddr(message.get('From'))[0]
                            image_email = email.utils.parseaddr(message.get('From'))[1]
                            subject = message.get('Subject')
                            date_raw = message.get('Date')
                            date_obj = parser.parse(date_raw).date()
                            formatted_date = date_obj.strftime('%a, %d %b %Y')
                            subject_part1 = 'Indeed'
                            subject_part2 = subject

                            def extract_phone_number(data):
                                if isinstance(data, BytesIO):
                                    with pdfplumber.open(data) as pdf:
                                        full_text = ""
                                        for page in pdf.pages:
                                            full_text += page.extract_text()
                                else:  # If data is already a string
                                    full_text = data

                                phone_pattern = r'(?:(?:\+?\d{1,3}\s?)?(?:\(\d{1,4}\)\s?)?|(?:\+?\d{1,3}\s)?\d{1,4}[\s./-]?)?\(?(?:\d{2,3})\)?[\s./-]?\d{1,5}[\s./-]?\d{1,5}(?:[\s./-]?\d{1,5})?(?:[\s./-]?\d{1,5})?'
                                phone_matches = re.findall(phone_pattern, full_text)
                                cleaned_numbers = [re.sub(r'\D', '', num) for num in phone_matches]
                                cleaned_numbers = [num for num in cleaned_numbers if num]

                                if cleaned_numbers:
                                    return cleaned_numbers[0]
                                else:
                                    return None

                            def extract_emails(data):
                                if isinstance(data, BytesIO):
                                    with pdfplumber.open(data) as pdf:
                                        full_text = ""
                                        for page in pdf.pages:
                                            full_text += page.extract_text()
                                else:  # If data is already a string
                                    full_text = data

                                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                                email_matches = re.findall(email_pattern, full_text)
                                return email_matches

                            def extract_phone_number1(pdf_file):
                                with pdfplumber.open(pdf_file) as pdf:
                                    for page in pdf.pages:
                                        page_text = page.extract_text()
                                        phone_pattern = r'(?:(?:\+?\d{1,3}\s?)?(?:\(\d{1,4}\)\s?)?|(?:\+?\d{1,3}\s)?\d{1,4}[\s./-]?)?\(?(?:\d{2,3})\)?[\s./-]?\d{1,5}[\s./-]?\d{1,5}(?:[\s./-]?\d{1,5})?(?:[\s./-]?\d{1,5})?'
                                        phone_matches = re.findall(phone_pattern, page_text)
                                        cleaned_numbers = [re.sub(r'\D', '', num) for num in phone_matches]
                                        cleaned_numbers = [num for num in cleaned_numbers if num]
                                        if cleaned_numbers:
                                            for num in cleaned_numbers:
                                                if len(num) >= 10:
                                                    return num
                                return None

                            def extract_emails1(pdf_file):
                                with pdfplumber.open(pdf_file) as pdf:
                                    for page in pdf.pages:
                                        page_text = page.extract_text()
                                        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                                        email_matches = re.findall(email_pattern, page_text)
                                        if email_matches:
                                            return email_matches

                                return None

                            if subject == "HandsHR website":
                                body = message.get_payload(decode=True).decode('utf-8')
                                name_match = re.search(r'<strong>Name</strong></td></tr><tr bgcolor=\'#FFFFFF\'><td width=\'20\'>&nbsp;</td><td>([^<]+)', body)
                                number_match = re.search(r'<strong>Number</strong></td></tr><tr bgcolor=\'#FFFFFF\'><td width=\'20\'>&nbsp;</td><td>([^<]+)', body)
                                email_match = re.search(r'<strong>Email Address</strong></td></tr><tr bgcolor=\'#FFFFFF\'><td width=\'20\'>&nbsp;</td><td>([^<]+)', body)
                                position_match = re.search(r'<strong>Position</strong></td></tr><tr bgcolor=\'#FFFFFF\'><td width=\'20\'>&nbsp;</td><td>([^<]+)', body)
                                resume_link_match = re.search(r"<td[^>]*><a href='([^']+)'", body)
                                name = name_match.group(1).strip() if name_match else None
                                number = number_match.group(1).strip() if number_match else None
                                email_addr = email_match.group(1).strip() if email_match else None
                                position = position_match.group(1).strip() if position_match else None
                                resume_link = resume_link_match.group(1).strip() if resume_link_match else None
                                pdf_content_blob = None

                                if resume_link:
                                    response = requests.get(resume_link)
                                    resume_filename = os.path.basename(resume_link)
                                    if response.ok:
                                        pdf_content = response.content
                                        pdf_content_blob = io.BytesIO(pdf_content)

                                with app.app_context():
                                    email_entry = Emails_data(
                                        org_id=org_id,
                                        sender_name=name,
                                        email=email_addr,
                                        subject_part1=subject,
                                        subject_part2=position,
                                        formatted_date=formatted_date,
                                        file_name=resume_filename if resume_filename else None,
                                        file_content=pdf_content_blob.getvalue() if pdf_content_blob else None,
                                        pdf_content_json=None,
                                        phone_number=number,
                                        action='',
                                        status=None,
                                        message_id=message_id
                                    )
                                    session.add(email_entry)
                                    session.commit()
                            else:
                                pdf_attachments = []
                                for part in message.walk():
                                    if part.get_content_type() == 'application/pdf':
                                        filename = part.get_filename()
                                        decoded_filename = decode_header(filename)[0][0]
                                        if isinstance(decoded_filename, bytes):
                                            decoded_filename = decoded_filename.decode()
                                        pdf_attachments.append((decoded_filename, part.get_payload(decode=True)))
                                for filename, payload in pdf_attachments:
                                    try:
                                        payload_file = io.BytesIO(payload)
                                        pdf_reader = PdfReader(payload_file)
                                        has_images = any(
                                            '/XObject' in page['/Resources'] and page['/Resources']['/XObject'].get_object()
                                            for page in pdf_reader.pages
                                        )

                                        if has_images:
                                            extracted_text = []
                                            with pdfplumber.open(payload_file) as pdf:
                                                for page in pdf.pages:
                                                    images = page.images
                                                    for img in images:
                                                        image_data = page.to_image(resolution=200)
                                                        text = pytesseract.image_to_string(image_data.original)
                                                        extracted_text.append(text)
                                            full_text = "\n".join(extracted_text)
                                            phone_number = extract_phone_number(full_text)
                                            emails = extract_emails(full_text)
                                            email_str = ", ".join(emails) if emails else ""
                                        else:
                                            with pdfplumber.open(payload_file) as pdf:
                                                full_text = ""
                                                for page in pdf.pages:
                                                    full_text += page.extract_text()
                                            phone_number = extract_phone_number1(payload_file)
                                            emails = extract_emails1(payload_file)
                                            email_str = ", ".join(emails) if emails else ""

                                        with app.app_context():
                                            existing_entry = session.query(Emails_data).filter(
                                                or_(
                                                    Emails_data.sender_name == sender_name,
                                                    Emails_data.sender_name.is_(None)
                                                ),
                                                or_(
                                                    Emails_data.email == email_str,
                                                    Emails_data.email.is_(None)
                                                ),
                                                Emails_data.formatted_date == formatted_date,
                                                Emails_data.file_name == filename,
                                                Emails_data.phone_number == phone_number
                                            ).first()

                                            if existing_entry is None:
                                                duplicate_entry = session.query(Emails_data).filter(
                                                    Emails_data.email == email_str,
                                                    Emails_data.subject_part1 == subject_part1,
                                                    Emails_data.subject_part2 == subject
                                                ).first()
                                                pdf_data = {
                                                    'sender_name': sender_name,
                                                    'email': email_str,
                                                    'subject_part1': subject_part1,
                                                    'subject_part2': subject,
                                                    'formatted_date': formatted_date,
                                                    'file_name': filename,
                                                    'phone_number': phone_number,
                                                    'full_text': full_text
                                                }
                                                pdf_json = json.dumps(pdf_data)
                                                if duplicate_entry is None:
                                                    if phone_number is not None and emails is not None:
                                                        email_entry = Emails_data(
                                                            org_id=org_id,
                                                            sender_name=sender_name,
                                                            email=emails[0] if emails else 'No Email!',
                                                            subject_part1=subject_part1,
                                                            subject_part2=subject,
                                                            formatted_date=formatted_date,
                                                            file_name=filename,
                                                            file_content=payload,
                                                            pdf_content_json=pdf_json,
                                                            phone_number=phone_number,
                                                            action='',
                                                            status=None,
                                                            message_id=message_id
                                                        )

                                                        session.add(email_entry)
                                                        session.commit()
                                                else:
                                                    print(f"Duplicate entry found for email '{email_str}' and subject '{subject_part1} - {subject_part2}'")

                                    except Exception as e:
                                        print(f"Error processing PDF '{filename}': {str(e)}")
                                        with app.app_context():
                                            email_entry = Emails_data(
                                                org_id=org_id,
                                                sender_name=sender_name,
                                                email=None,
                                                subject_part1=subject_part1,
                                                subject_part2=subject,
                                                formatted_date=formatted_date,
                                                file_name=filename,
                                                file_content=payload,
                                                pdf_content_json=None,
                                                phone_number=None,
                                                action='',
                                                status=None,
                                                message_id=message_id
                                            )
                                            session.add(email_entry)
                                            session.commit()

                        except Exception as e:
                            print(f"Error fetching email '{msg_id}': {str(e)}")

                except Exception as e:
                    print(f"Error logging in to email account '{email_address}': {str(e)}")
                    if email_address not in last_email_sent or last_email_sent[email_address] < datetime.now() - timedelta(days=1):
                        email_subject = 'Urgent: Action Required - Email Account Credentials Update'
                        email_body = '''
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <style>
                                body {
                                    font-family: Arial, sans-serif;
                                }
                                .container {
                                    background-color: #f2f2f2;
                                    border-radius: 10px;
                                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                                    overflow: hidden;
                                    margin: 15px 0px;
                                    padding: 20px;
                                    max-width: 800px;
                                    margin:auto;
                                }
                                .cont-img{
                                    width: 34%;
                                    margin: auto;
                                    display: block;
                                    margin-bottom:20px
                                }
                                .details {
                                    margin-top: 10px;
                                }
                                .details p {
                                    margin: 0;
                                }
                                .bold {
                                    font-weight: bold;
                                }
                                .signature {
                                    margin-top: 20px;
                                    font-size:15px
                                }
                                .signature p {
                                    margin: 0px;
                                }
                                .signature2 p {
                                    margin: 0px;
                                    text-align: center;
                                }
                                .hello{
                                    border: 1px solid #19355f;
                                    margin-bottom: 28px;
                                }
                                .signature2 {
                                    padding: 7px;
                                    background: #ffff;
                                    margin-top: 21px;
                                }
                                .geoxhr {
                                    width: 100px;
                                    margin-top: 10px;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <img class="cont-img" src="https://www.click-hr.com/static/img/clickhr.png">
                                <div class="hello"></div>
                                <div class="details">
                                    <p>We encountered an issue accessing your email for ClickHR. Please contact the ClickHR Administrator to update your credentials ASAP to avoid disruption. This includes your Indeed or ZipRecruiter email and password.</p>
                                </div>
                                <div class="signature">
                                    <p>Thank you.</p>
                                </div>
                                <div class="signature2">
                                    <p>If assistance is required, feel free to reach out to us at:</p>
                                    <p>clickhr@click-hr.com.</p>
                                    <p> +1 647-930-0988</p>
                                </div>
                            </div>
                        </body>
                        </html>
                        '''
                        msg = Message(subject=email_subject, recipients=[email_address], html=email_body)
                        mail.send(msg)
                        last_email_sent[email_address] = datetime.now()
                finally:
                    server.logout()
            time.sleep(60)  # Run every 1 minute

    except Exception as e:
        print(f"Error in fetch_data: {e}")
    finally:
        session.close()


def run_app():
    app.run()

def run_scheduled_tasks():
    schedule.every(1).minutes.do(fetch_data)
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_background_task():
    bg_thread = Thread(target=run_scheduled_tasks, daemon=True)
    bg_thread.start()
    print("Background thread started.")

if __name__ == "__main__":
   # run_background_task()
    run_app()
