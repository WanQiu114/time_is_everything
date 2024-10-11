import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_google_calendar_service():
    """Authenticate and get the Google Calendar service."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return build("calendar", "v3", credentials=creds)

def add_event_to_calendar(service, app_name, start_time, end_time):
    """Create an event in Google Calendar for the app usage."""
    event = {
        'summary': f'Worked On {app_name}',
        'description': f'Time spent on {app_name}',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC-4',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC-4',
        },
    }

    try:
        service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created for {app_name}: {start_time} to {end_time}")
    except HttpError as error:
        print(f"An error occurred: {error}")