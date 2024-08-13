from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
import imaplib
import email
import re
import io
from email.header import decode_header
import pdfplumber
from datetime import datetime
from dateutil import parser
from PyPDF2 import PdfReader
import json
from datetime import datetime
import schedule
import time
# from twilio.rest import Client
# import fitz
import threading
import fitz  # PyMuPDF
import re
from flask import Flask
import pymysql
import numpy as np
# import cv2
import pytesseract
from PIL import Image
from io import BytesIO
thread_creation_allowed = True


app = Flask(__name__)

# client = Client(account_sid, auth_token)
#

DB_HOST = '35.183.134.169'
DB_USER = 'hayat'
DB_PASSWORD = 'Hayat_admin123'
DB_DATABASE = 'Clickhrin'
#
# DB_HOST = 'localhost'
# DB_USER = 'root'
# DB_PASSWORD = ''
# DB_DATABASE = 'clickhr'

IMAP_SERVER = 'imap.gmail.com'
EMAIL_CREDENTIALS = [
    {'address': 'jobs@i8is.com', 'password': 'nisa2024'},  # Add more email addresses and passwords here
]
Base = declarative_base()


# Define the SQLAlchemy model
class Emails_data(Base):
    __tablename__ = 'emails_data'
    id = Column(Integer, primary_key=True)
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
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.sender_name, self.subject_part2)


# Create the database engine and session
# engine = create_engine('mysql+pymysql://hayat:Hayat_admin123@35.183.134.169/clickhr')
engine = create_engine(
    'mysql+pymysql://hayat:Hayat_admin123@35.183.134.169/Clickhrin')

Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)


# Function to create threads (only if allowed)
def create_thread(target_function):
    global thread_creation_allowed
    if thread_creation_allowed:
        print("Creating thread...")
        # Create a new thread targeting the specified function
        new_thread = threading.Thread(target=target_function)
        new_thread.start()
    else:
        print("Thread creation not allowed.")
def delete_duplicate_records():
    while True:
        try:
            connection = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE
            )
            if connection.open:
                print("Connected to MySQL database")
                cursor = connection.cursor()

                # SQL query to delete duplicate rows based on specified columns
                delete_query = """
                DELETE e1
                FROM emails_data e1
                INNER JOIN emails_data e2
                WHERE e1.sender_name = e2.sender_name
                AND e1.email = e2.email
                AND e1.subject_part1 = e2.subject_part1
                AND e1.subject_part2 = e2.subject_part2
                AND e1.formatted_date = e2.formatted_date
                AND e1.id > e2.id
                """

                cursor.execute(delete_query)
                connection.commit()

                print(cursor.rowcount, "duplicate records deleted.")
            else:
                print("Failed to connect to MySQL database")
        except pymysql.Error as error:
            print("Error:", error)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.open:
                connection.close()
                print("MySQL connection closed")
        time.sleep(180)

def fetch_data():
    while True:
        for email_credentials in EMAIL_CREDENTIALS:
            email_address = email_credentials['address']
            password = email_credentials['password']
            server = imaplib.IMAP4_SSL(IMAP_SERVER, port=993)

            try:
                server.login(email_address, password)
                server.select('INBOX')

                current_datetime = datetime.now()
                current_date = current_datetime.strftime('%d-%b-%Y')
                year = '2024'

                # Update the search criteria to fetch emails from June 1st to the current date
                # search_criteria = f'(SINCE 07-Mar-{year} BEFORE {current_date})'
                search_criteria = f'(SINCE {current_date})'
                _, msg_ids = server.search   (None, search_criteria)
                recent_msg_ids = msg_ids[0].split()

                def extract_phone_number(data):
                    if isinstance(data, BytesIO):  # If data is a PDF file
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
                        return cleaned_numbers[0]  # Return only the first phone number
                    else:
                        return None

                def extract_emails(data):
                    if isinstance(data, BytesIO):  # If data is a PDF file
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



                for msg_id in recent_msg_ids:
                    try:
                        _, msg_data = server.fetch(msg_id, '(RFC822)')
                        raw_message = msg_data[0][1]
                        message = email.message_from_bytes(raw_message)
                        if '=?' in message.get('Subject'):
                            continue
                        sender_name = email.utils.parseaddr(message.get('From'))[0]
                        image_email = email.utils.parseaddr(message.get('From'))[1]
                        print(sender_name,image_email)
                        subject = message.get('Subject')
                        date_raw = message.get('Date')
                        date_obj = parser.parse(date_raw).date()
                        formatted_date = date_obj.strftime('%a, %d %b %Y')
                        subject_part1 = 'Indeed'
                        subject_part2 = subject

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
                                    '/XObject' in page['/Resources'] and page['/Resources']['/XObject'].get_object() for
                                    page in pdf_reader.pages)

                                if has_images:
                                    print(f"Processing {filename} as it contains images")

                                    extracted_text = []

                                    # Add image processing code here
                                    with pdfplumber.open(payload_file) as pdf:
                                        for page in pdf.pages:
                                            # Extract images from the page
                                            images = page.images

                                            # Extract text from each image using pytesseract
                                            for img in images:
                                                image_data = page.to_image(resolution=200)
                                                text = pytesseract.image_to_string(image_data.original)
                                                extracted_text.append(text)

                                    # Combine extracted text from images
                                    full_text = "\n".join(extracted_text)

                                    # Continue processing the text as before
                                    phone_number = extract_phone_number(full_text)
                                    emails = extract_emails(full_text)
                                    email_str = ", ".join(emails) if emails else ""
                                    # print(full_text)
                                else:
                                 # Extract the entire text content from the PDF
                                 with pdfplumber.open(payload_file) as pdf:
                                     full_text = ""
                                     for page in pdf.pages:
                                         full_text += page.extract_text()

                                 phone_number = extract_phone_number1(payload_file)
                                 emails = extract_emails1(payload_file)
                                 email_str = ", ".join(emails) if emails else ""
                                 print(subject, "subject_part1", subject_part1, "subject_part2", subject_part2)

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
                                        # Check for duplicate based on email and subject
                                        duplicate_entry = session.query(Emails_data).filter(
                                            Emails_data.email == email_str,
                                            Emails_data.subject_part1 == subject_part1,
                                            Emails_data.subject_part2 == subject
                                        ).first()

                                        # Create a dictionary to represent the PDF data including the full text content
                                        pdf_data = {
                                            'sender_name': sender_name,
                                            'email': email_str,
                                            'subject_part1': subject_part1,
                                            'subject_part2': subject,
                                            'formatted_date': formatted_date,
                                            'file_name': filename,
                                            'phone_number': phone_number,
                                            'full_text': full_text  # Include the full text content
                                        }

                                        # Serialize the dictionary to JSON format
                                        pdf_json = json.dumps(pdf_data)
                                        if duplicate_entry is None:
                                            if phone_number is not None and emails is not None:
                                                email_entry = Emails_data(
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
                                                    status=None
                                                )

                                                session.add(email_entry)
                                                session.commit()
                                        else:
                                            print(
                                                f"Duplicate entry found for email '{email_str}' and subject '{subject_part1} - {subject_part2}'")

                            except Exception as e:
                                print(f"Error processing PDF '{filename}': {str(e)}")
                                # print(f"Error processing PDF '{filename}': {str(e)}")
                                # If an error occurs while processing the PDF, save the PDF as a blob file and set other fields to None
                                with app.app_context():
                                    email_entry = Emails_data(
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
                                        status=None
                                    )
                                    session.add(email_entry)
                                    session.commit()

                    except Exception as e:
                        print(f"Error fetching email '{msg_id}': {str(e)}")

            except Exception as e:
                print(f"Error logging in to email account '{email_address}': {str(e)}")

            finally:
                server.logout()
        time.sleep(30)  # Run every 1 minute

        # Create and start threads for the two functions


if thread_creation_allowed:
    delete_thread = threading.Thread(target=delete_duplicate_records)
    fetch_thread = threading.Thread(target=fetch_data)

    delete_thread.start()
    fetch_thread.start()
session.commit()
session.close()

while True:
    schedule.run_pending()
    time.sleep(1)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=2000)
