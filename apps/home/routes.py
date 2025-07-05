from apps.home import blueprint
from flask import Flask, request, Response, redirect, url_for, render_template, flash, jsonify, session, current_app
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound, Undefined
import os
from datetime import datetime, timedelta
import json
import logging
from ..authentication.util import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Static API key configuration
STATIC_API_KEYS = {
    "1": {
        "api_key": "5f28839b8c9a9d186d3cc79d117be784a63ca83061635df1ebfec146abb93b6b",
        "is_active": True
    }
}

# Cache setup
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

def sanitize_data(data):
    """Recursively sanitize data by converting Undefined/unsafe objects"""
    if isinstance(data, Undefined):
        return None
    elif isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [sanitize_data(item) for item in data]
    elif isinstance(data, (str, int, float, bool)) or data is None:
        return data
    else:
        try:
            json.dumps(data)
            return data
        except TypeError:
            return str(data)

def validate_api_key(api_key):
    """Validate the API key format"""
    return api_key == STATIC_API_KEYS["1"]["api_key"]

@blueprint.route('/<path:endpoint>', methods=['POST'])
def handle_data(endpoint):
    try:
        data = request.get_json()
        if not data:
            logger.warning("No JSON data received")
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400

        api_key = data.get('api_key')
        if not api_key or not validate_api_key(api_key):
            logger.warning(f"Invalid API key attempt: {api_key}")
            return jsonify({"status": "error", "message": "Invalid API key"}), 403

        filename = os.path.join(CACHE_DIR, f"mt5_data_{api_key}.json")
        cached_data = {"data": {}, "last_updated": datetime.utcnow().isoformat()}

        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    cached_data = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Corrupted cache file: {filename}")

        cached_data['data'][endpoint] = sanitize_data(data)
        cached_data['last_updated'] = datetime.utcnow().isoformat()

        with open(filename, 'w') as f:
            json.dump(cached_data, f, indent=2)

        logger.info(f"Data received for {endpoint}")
        return jsonify({"status": "success", "message": "Data received"}), 200

    except Exception as e:
        logger.error(f"Error in handle_data: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": "Internal server error"}), 500

@blueprint.route('/Client/Dashboard', methods=['GET'])
@login_required
def show_dashboard():
    try:
        if not current_user.is_authenticated:
            flash("Session expired. Please log in.", "danger")
            return redirect(url_for('authentication_blueprint.login'))

        if getattr(current_user, 'two_factor_auth', False) and not session.get('log_two', False):
            return redirect(url_for('authentication_blueprint.verify_otp_page'))

        user_id = str(getattr(current_user, 'id', ''))
        if user_id != "1":
            logger.warning(f"Unauthorized access attempt by user {user_id}")
            flash("Access denied", "danger")
            return redirect(url_for('authentication_blueprint.login'))

        api_key = STATIC_API_KEYS["1"]["api_key"]
        filename = os.path.join(CACHE_DIR, f"mt5_data_{api_key}.json")
        dashboard_data = {}
        last_updated = "Never"

        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    cached_data = json.load(f)
                    raw_data = cached_data.get('data', {})
                    last_updated = cached_data.get('last_updated', 'Never')

                    for section_name, section_content in raw_data.items():
                        if isinstance(section_content, dict) and section_content.get('api_key') == api_key:
                            dashboard_data[section_name] = sanitize_data(section_content.get('data', {}))
            except json.JSONDecodeError:
                logger.error(f"Corrupted dashboard data file: {filename}")
                flash("Data loading issue - please refresh", "warning")

        return render_template(
            'home/Client/Dashboard.html',
            segment='Dashboard',
            active_page='Dashboard.html',
            mt5_data=dashboard_data,
            last_updated=last_updated,
            user_id=user_id,
            api_key=api_key
        )

    except Exception as e:
        logger.critical(f"Dashboard error: {str(e)}", exc_info=True)
        flash("System error - please try again", "danger")
        return redirect(url_for('authentication_blueprint.login'))

@blueprint.route('/api/mt5-data', methods=['GET'])
@login_required
def get_mt5_data():
    try:
        user_id = str(current_user.id)
        if user_id != "1":
            return jsonify({"error": "Unauthorized"}), 403

        api_key = STATIC_API_KEYS["1"]["api_key"]
        filename = os.path.join(CACHE_DIR, f"mt5_data_{api_key}.json")

        if not os.path.exists(filename):
            return jsonify({"error": "No data available"}), 404

        with open(filename, 'r') as f:
            cached_data = json.load(f)
            response_data = {
                section: content.get('data', {})
                for section, content in cached_data.get('data', {}).items()
                if isinstance(content, dict) and content.get('api_key') == api_key
            }

        return jsonify({
            "data": sanitize_data(response_data),
            "last_updated": cached_data.get('last_updated', 'Unknown')
        })

    except Exception as e:
        logger.error(f"API error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

# Additional routes remain unchanged but with added error handling
@blueprint.route('/')
def index():
    return render_template('home/Home.html', segment='Home')

def template_exists(template_path):
    try:
        current_app.jinja_loader.get_source(current_app.jinja_env, template_path)
        return True
    except TemplateNotFound:
        return False

@blueprint.route('/Client/<template>')
@login_required
def route_client_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'
            
        if current_user.two_factor_auth and not session.get('log_two', False):
            return redirect(url_for('authentication_blueprint.verify_otp_page'))
            
        client_template_path = f"home/Client/{template}"
        if template_exists(client_template_path):
            return render_template(client_template_path,
                                segment=get_segment(request),
                                current_user=current_user,
                                active_page=template)
        raise TemplateNotFound(template)
    except Exception as e:
        logger.error(f"Template error: {str(e)}", exc_info=True)
        return render_template('home/page-500.html'), 500

@blueprint.route('/<template>')
def route_general_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'
            
        general_template_path = f"home/{template}"
        if template_exists(general_template_path):
            return render_template(general_template_path,
                                 segment=get_segment(request))
        raise TemplateNotFound(template)
    except Exception as e:
        logger.error(f"General template error: {str(e)}", exc_info=True)
        return render_template('home/page-500.html'), 500

def get_segment(request):
    try:
        return request.path.split('/')[-1] or 'index'
    except Exception:
        return 'index'