import logging
import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api

from prometheus_client import start_http_server, Summary

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = os.urandom(24)

# Configuration for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)

# Create Prometheus metrics
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Log an info message when the app starts
logging.info('Application startup')

# Import models after initializing db
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

# Decorator to measure request processing time
@REQUEST_TIME.time()
def process_request():
    pass

# Route for the home page
@app.route('/')
def index():
    process_request()
    return render_template('index.html')

# Route for form submission
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        try:
            process_request()
            # Get form data
            name = request.form['name']
            email = request.form['email']
            # Save data to the database
            new_entry = User(name=name, email=email)
            db.session.add(new_entry)
            db.session.commit()
            logging.info(f'New user added: {name}, {email}')
            flash('User successfully added!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            logging.error('Error during form submission', exc_info=True)
            flash('An error occurred while adding the user.', 'danger')
            return 'An error occurred', 500

# Route for displaying analysis results
@app.route('/analysis')
def analysis():
    try:
        process_request()
        users = User.query.all()
        total_users = len(users)
        email_domains = [user.email.split('@')[1] for user in users]
        domain_counts = {domain: email_domains.count(domain) for domain in set(email_domains)}

        return render_template('analysis.html', total_users=total_users, domain_counts=domain_counts)
    except Exception as e:
        logging.error('Error during form submission', exc_info=True)
        return 'An error occurred', 500

# API resource definition
class UserListResource(Resource):
    def get(self):
        process_request()
        users = User.query.all()
        user_list = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]
        return {'users': user_list}

api.add_resource(UserListResource, '/api/users')

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True)
