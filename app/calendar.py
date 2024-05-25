import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'config/credentials.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('calendar', 'v3', credentials=credentials)

logging.basicConfig(level=logging.INFO)

def create_event(summary, start_time, end_time):
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Seoul'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Seoul'},
    }
    try:
        event = service.events().insert(calendarId='jinhyuk.a.yoon@gmail.com', body=event).execute()
        logging.info(f"Event created: {event.get('htmlLink')}")
        return event
    except Exception as e:
        logging.error(f"Error creating event: {e}")
        return None
