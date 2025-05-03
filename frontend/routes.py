from flask import Blueprint, render_template

frontend_routes = Blueprint('frontend_routes', __name__)


@frontend_routes.route('/')
def home():
    return render_template('home.html')

@frontend_routes.route('/about')
def about():
    return render_template('about.html')

@frontend_routes.route('/contact')
def contact():
    return render_template('contact.html')

@frontend_routes.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@frontend_routes.route('/register', methods=['GET'])
def register():
    return render_template('register.html')