from flask import Flask, render_template, request
from apiclient import discovery
from oauth2client import client
import httplib2


app = Flask(__name__)
app.debug=True
 
@app.route('/')
def sign_in():
    return render_template('google_sign_in.html')

@app.route('/storeauthcode', methods=['GET', 'POST'])
def get_auth_code():
    if not request.headers.get('X-Requested-With'):
        abort(403)

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

    labels = results.get('labels', [])
    if not labels:
        print('No labels found.')
    else:
      print('Labels:')
      for label in labels:
        print(label['name'])

    # appfolder = service.files().get(fileId='appfolder').execute()

    # Get profile info from ID token
    userid = credentials.id_token['sub']
    email = credentials.id_token['email']
    
    


 
if __name__ == "__main__":
    app.run()