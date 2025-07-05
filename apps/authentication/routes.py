from flask import render_template, redirect, request, url_for, session, jsonify, flash
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required,
    UserMixin
)
from datetime import datetime, timedelta
from apps import login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm
from apps.authentication.util import send_email_async
import logging
import uuid
from sqlalchemy.exc import SQLAlchemyError
import traceback

# Configure logging to capture only errors
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable Werkzeug's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# === Static credentials and keys ===
STATIC_EMAIL = "shemalandry6@gmail.com"
STATIC_PASSWORD = "Darkone"
ADMIN_EMAIL = "knightwatcher20@gmail.com"

STATIC_API_KEYS = {
    "1": {
        "api_key": "5f28839b8c9a9d186d3cc79d117be784a63ca83061635df1ebfec146abb93b6b",
        "is_active": True
    }
}

# === Static User class using UserMixin ===
class StaticUser(UserMixin):
    def __init__(self):
        self.id = 1
        self.username = "Darkone"
        self.email = STATIC_EMAIL
        self.two_factor_auth = False

    def get_id(self):
        return str(self.id)

# === User loader function ===
@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return StaticUser()
    return None

# === Login route ===
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)

    if request.method == 'POST' and 'login' in request.form:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()


        if username.lower() == STATIC_EMAIL.lower() and password == STATIC_PASSWORD:
            user = StaticUser()
            session_token = str(uuid.uuid4())
            session['session_token'] = session_token
            login_user(user, remember=True)

            return redirect(url_for('home_blueprint.show_dashboard'))
        else:
            print("Invalid credentials!")
            flash("Invalid username or password", "error")

    return render_template('accounts/Login.html', form=login_form)

# === Logout route ===
@blueprint.route('/logout')
def logout():
    session.pop('session_token', None)
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))

# === Unauthorized handler ===
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403

# === Error handlers ===
@blueprint.errorhandler(400)
def bad_request(error):
    return render_template('home/page-400.html'), 400

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    logging.error(f"500 Error: {error}")

    # Send email notification to admin
    subject = "🚨 Critical Error in Your Flask App"
    html_body = f"""
    <h3>An Internal Server Error (500) occurred</h3>
    <p><strong>Error Details:</strong></p>
    <pre>{str(error)}</pre>
    <p><strong>Request Path:</strong> {request.path}</p>
    <p><strong>User IP:</strong> {request.remote_addr}</p>
    """
    send_email_async(ADMIN_EMAIL, subject, html_body)

    if request.accept_mimetypes.accept_json:
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('home/page-500.html'), 500
