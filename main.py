from openai import OpenAI
import json
import os, datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

base_url = "https://api.aimlapi.com/v1"

# Insert your AIML API key in the quotation marks instead of <YOUR_AIMLAPI_KEY>:
api_key = "c98f13f1277241e08e6ca0f50e2fcbf8" 

system_prompt = "Always reply with the word no"
user_prompt = "Tell me about San Francisco"

api = OpenAI(api_key=api_key, base_url=base_url)

def createToken():
    creds = None

    if os.path.exists("token.json"):
       creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
           creds.refresh(Request())
        else:
           flow = InstalledAppFlow.from_client_secrets_file("Calendar-API-Utility\credentials.json", SCOPES) # you may have to change the credentials.json to the relative path of the file.
           creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        global service
        service = build("calendar", "v3", credentials=creds)

    except HttpError as error:
        print(f"An error occurred: {error}")


def createEvent(title, color, date, startTime, endTime, allDay=False, allowDuplicates = True):

    event = {
        "summary": title,
        "colorId": color,
        "start": {
            "date": date if allDay else None,
            "dateTime": None if allDay else date + 'T' + startTime + ':00',
            "timeZone": 'America/New_York'
            },
        "end": {
            "date": date if allDay else None,
            "dateTime": None if allDay else date + 'T' + endTime + ':00',
            "timeZone": 'America/New_York'
            }
    }
    if allowDuplicates == False:
        existing_events = getEvents(date)
        event_exists = any(existing_event['summary'] == title for existing_event in existing_events)

        if not event_exists:
            event = service.events().insert(calendarId="primary",body=event).execute()
        else:
            print(f'Event "{title}" on {date} already exists')
    else: 
        event = service.events().insert(calendarId="primary",body=event).execute()


def getEvents(date):
    events_result = (service.events().list(calendarId="primary", timeMin=date + 'T00:00:00Z', timeMax=date + 'T23:59:59Z').execute())
    events = events_result.get('items', [])
    return events

def deleteEvent(event):
    print(event['id'])
    service.events().delete(calendarId='primary', eventId=event['id']).execute()

def main():
    createToken()
    completion = api.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=256,
    )

    response = completion.choices[0].message.content

    print("User:", user_prompt)
    print("AI:", response)


if __name__ == "__main__":
    main()