from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_required, login_user, UserMixin
from apiclient import discovery
from flask_sqlalchemy import SQLAlchemy
from oauth2client import client
import httplib2





app = Flask(__name__)
app.debug=True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SECRET_KEY'] = 'this_is_secret'


db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "sign_in"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)


def check_credentials(user_email):
    user = User.query.filter_by(email=user_email).first()
    if user:
        print('found user: %s' % user.email)
        
    if not user:
        print('Did not find user %s. Adding to DB' % user_email)
        u = User(email=user_email)
        db.session.add(u)
        db.session.commit()

@app.route('/test')
@login_required
def login_required():
    return 'logged in'
 
@app.route('/')
def sign_in():
    print('running ')
    return render_template('google_sign_in.html')

@app.route('/storeauthcode', methods=['GET', 'POST'])
def get_auth_code():
    if not request.headers.get('X-Requested-With'):
        return 'Aborted'

    auth_code = request.data

    # Set path to the Web application client_secret_*.json file you downloaded from the
    # Google API Console: https://console.developers.google.com/apis/credentials
    CLIENT_SECRET_FILE = 'client_secret.json'


    # Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_clientsecrets_and_code(
        CLIENT_SECRET_FILE,
        ['https://www.googleapis.com/auth/drive.appdata', 'profile', 'email'],
        auth_code)

    

    # Call Google API
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http_auth)
    
    results = service.users().labels().list(userId='me').execute()
    
    # Get profile info from ID token
    user_id = credentials.id_token['sub']
    user_email = credentials.id_token['email']

    check_credentials(user_email)
    return 'finished auth'



 
if __name__ == "__main__":
    app.run()