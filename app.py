from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api

app = Flask(__name__)

# Configuration for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)

# Import models after initializing db
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for form submission
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        # Save data to the database
        new_entry = User(name=name, email=email)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('index'))

# Route for displaying analysis results
@app.route('/analysis')
def analysis():
    users = User.query.all()
    total_users = len(users)
    email_domains = [user.email.split('@')[1] for user in users]
    domain_counts = {domain: email_domains.count(domain) for domain in set(email_domains)}

    return render_template('analysis.html', total_users=total_users, domain_counts=domain_counts)

# API resource definition
class UserListResource(Resource):
    def get(self):
        users = User.query.all()
        user_list = [{'id': user.id, 'name': user.name, 'email': user.email} for user in users]
        return {'users': user_list}

api.add_resource(UserListResource, '/api/users')

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True)
