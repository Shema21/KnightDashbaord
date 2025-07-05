
import os
import hashlib
import binascii
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from flask import session
import pandas as pd
import re
import json
from datetime import datetime
from collections import defaultdict
from datetime import datetime
import secrets

from functools import wraps
from flask import session, flash, redirect, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)


import json

import shutil


# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/

# SMTP server configuration (for Gmail in this case)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'shemalandry6@gmail.com'
SENDER_PASSWORD = 'klrx zqbv pkrg ydmi'

# Allowed file extensions
ALLOWED_PICTURE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
# Define upload folders
PROFILE_UPLOAD_FOLDER = os.path.join('apps', 'static', 'assets', 'uploads', 'avatars')


# Ensure directories exist
os.makedirs(PROFILE_UPLOAD_FOLDER, exist_ok=True)


def allowed_picture_file(filename):
    """
    Check if the file has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PICTURE_EXTENSIONS

def send_email_async(receiver_email, subject, html_body):
    """Send an HTML email asynchronously in a separate thread."""
    
    def send():
        try:
            # Your email credentials
            sender_email = "shemalandry6@gmail.com"
            sender_password = "klrx zqbv pkrg ydmi"
            
            # Set up the SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()  # Start TLS for security
            server.login(sender_email, sender_password)
            
            # Set up the MIME structure for the email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            
            # Attach the HTML message body
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send the email
            server.sendmail(sender_email, receiver_email, msg.as_string())
            
            # Close the SMTP session
            server.quit()
            print(f"Email sent successfully to {receiver_email}")

        except Exception as e:
            print(f"Error sending email: {str(e)}")

    # Start the email sending thread
    threading.Thread(target=send).start()


import os, json, time
from datetime import datetime

CACHE_DIR = os.path.join("apps", "cache", "mt5_data")

def get_cache_path(api_key):
    return os.path.join(CACHE_DIR, f"{api_key}.json")

def load_cached_data(api_key):
    path = get_cache_path(api_key)
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            return data
    return None

def save_cached_data(api_key, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = get_cache_path(api_key)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
