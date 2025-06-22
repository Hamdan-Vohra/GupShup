from flask import Blueprint, render_template,session,flash,redirect,url_for


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
def login():
    return render_template('login.html')

@frontend_routes.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@frontend_routes.route('/chat-app', methods=['GET'])
def ChatApp():
    if 'username' not in session:
        flash("Login required", "warning")
        return redirect(url_for('login'))
    print("Session Username:", session.get('username'))
    return render_template("chat-app.html", username=session['username'])