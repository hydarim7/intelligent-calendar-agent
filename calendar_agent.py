import os
import datetime
import flask
import google.auth.transport.requests
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from flask import session, redirect, url_for, request
from google.oauth2.credentials import Credentials

app = flask.Flask(__name__)
app.secret_key = "a3f9c1d27b4e3a9e1c847d2a90c9f5ef"

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
          'openid'
         ]

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def get_credentials():
    """Helper function to get credentials from session"""
    if 'credentials' not in session:
        return None
    
    creds_dict = session['credentials']
    
    # Check if all required fields are present
    required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret']
    if not all(field in creds_dict and creds_dict[field] for field in required_fields):
        print("Missing credentials fields:", {k: v for k, v in creds_dict.items()})
        return None
    
    return Credentials(**creds_dict)

@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect('/authorize')
    return redirect('/events')


@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['state'] = state
    return redirect(auth_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    
    # Fetch the token
    flow.fetch_token(authorization_response=request.url)
    
    credentials = flow.credentials
    
    # Store credentials properly
    session['credentials'] = credentials_to_dict(credentials)
    
    print("✅ Credentials saved:", session['credentials'].keys())
    print("Refresh token present:", bool(credentials.refresh_token))
    
    return redirect('/events')


@app.route('/logout')
def logout():
    session.clear()
    return 'Logged out! <a href="/authorize">Login again</a>'


@app.route('/events')
def events():
    creds = get_credentials()
    if not creds:
        return redirect('/authorize')
    
    service = build('calendar', 'v3', credentials=creds)

    # Fix deprecation warning
    now = datetime.datetime.now(datetime.UTC).isoformat()
    events_result = service.events().list(
        calendarId='primary', 
        timeMin=now,
        maxResults=5, 
        singleEvents=True, 
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        return "No upcoming events found."

    output = "<h2>Upcoming events:</h2><ul>"
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        output += f"<li>{start} — {event['summary']}</li>"
    output += "</ul>"
    output += '<br><a href="/add-event">Add Test Event</a> | <a href="/logout">Logout</a>'
    return output


@app.route('/add-event')
def add_event():
    creds = get_credentials()
    if not creds:
        return redirect('/authorize')
    
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': 'Test event from Flask',
        'start': {'dateTime': '2025-11-24T10:00:00+01:00'},
        'end': {'dateTime': '2025-11-24T11:00:00+01:00'},
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return f"✅ Event created on your calendar!<br><a href='/events'>View Events</a>"


if __name__ == '__main__':
    app.run(debug=True)