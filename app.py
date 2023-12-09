import streamlit as st
import smtplib
from ftplib import FTP
from email.mime.text import MIMEText
from tempfile import NamedTemporaryFile
import re
import os


def get_filepath(uploaded_file):
    """
        Gets the filepath of the uploaded file 
        as st.file_uploader() gives only the filename.
    """

    last_dot_index = uploaded_file.name.rfind('.')
    if last_dot_index != -1:
        file_extension = uploaded_file.name[last_dot_index:]
    else:
        file_extension = None
    
    with NamedTemporaryFile(delete=False, suffix=file_extension, dir="temp") as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name


def send_email(recipient_email, subject, body, file_name, filepath):
    """
        Uploads a given file to the FTP server, attaches the URL of the file 
        to the body of the mail and sends the email with SMTP.
    """

    # Add sender email.
    sender_email = ''
    sender_password = ''
    smtp_server = ''

    # Add the ftp data.
    ftp_host = ''
    ftp_username = ''
    ftp_password = ''
    ftp_upload_path = ''

    # Append the URL of the file in the email body
    email_body = f'{body}\n\nFile URL: ftp://{ftp_username}:{ftp_password}@{ftp_host}/{file_name}'

    # Create the schema for the email.
    message = MIMEText(email_body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email

    # Upload file to FTP server
    try:
        # Establish FTP connection
        with FTP(ftp_host) as ftp:
            # Authorize
            ftp.login(user=ftp_username, passwd=ftp_password)

            # Open the file to upload, move to the right directory
            # and stor it there.
            with open(filepath, 'rb') as file:
                ftp.cwd(ftp_upload_path)
                ftp.storbinary(f"STOR {file_name}", file)
                st.info('File uploaded to FTP server.')

            # Delete the temporary file after use
            os.remove(filepath)
    except Exception as e:
        st.error(f'Error: {e}')

    # Transfer the email with SMTP
    try:
        # Create a SMTP object.
        server = smtplib.SMTP(smtp_server, 587)

        # Initiate an SMTP conversation with the server.
        server.ehlo()

        # Establish a secure channel with TLS (Transport Layer Security)
        server.starttls()

        # Login to the SMTP server and send the email.
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        st.success("Email sent successfully!")

        server.quit()
    except Exception as e:
        st.error(f'Error: {e}')


def check_email(email):
    """Checks if the inputed email has a valid format."""

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, email):
        return True
    return False


# Input address
recipient_email = st.text_input('Recipient email:')

# Input subject
subject = st.text_input('Subject:')

# Input body
body = st.text_area('Body:')

# Upload file
file = st.file_uploader('Upload file:')

if st.button('Send email'):
    if check_email(recipient_email):
        if subject and body and file:
            send_email(recipient_email, subject, body, file.name, get_filepath(file))
        else:
            st.warning('Fill the fields and upload a file.')
    else:
        st.error('Invalid email!')