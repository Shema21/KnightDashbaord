from flask import Flask
from flask_login import LoginManager
from importlib import import_module

# Remove SQLAlchemy initialization
login_manager = LoginManager()

# Static user configuration
class StaticUser:
    def __init__(self):
        self.id = 1  # Static user ID
        self.username = "Darkone"
        self.email = "shemalandry6@gmail.com"  # Match your static email
        self.two_factor_auth = False
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    # Always return the static user if ID matches
    if user_id == "1":  # Match your static user ID
        return StaticUser()
    return None

def register_extensions(app):
    # Only initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'authentication_blueprint.login'

def register_blueprints(app):
    for module_name in ('authentication', 'home'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Remove database configuration
    register_extensions(app)
    register_blueprints(app)
    
    # Remove before_first_request and teardown handlers
    
    global application
    application = app  
    
    return app