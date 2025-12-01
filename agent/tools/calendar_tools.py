import os
import datetime
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List, Optional

# Scopes for Google Calendar access
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

TOKEN_FILE = 'token.json'
CLIENT_SECRETS_FILE = 'client_secret.json'


def get_calendar_credentials():
    """Get or refresh Google Calendar credentials"""
    creds = None
    
    # Load existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials, initiate OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("No valid credentials found. Starting OAuth flow...")
            print("A browser window will open for authentication.")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=8080)
        
        # Save the credentials for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print(f"✅ Credentials saved to {TOKEN_FILE}")
    
    return creds


def get_calendar_service():
    """Build and return Google Calendar service"""
    creds = get_calendar_credentials()
    return build('calendar', 'v3', credentials=creds)


def list_upcoming_events(max_results: int = 10) -> str:
    """
    List upcoming events from user's Google Calendar.
    
    Args:
        max_results: Maximum number of events to return (default: 10)
    
    Returns:
        Formatted string of upcoming events
    """
    try:
        service = get_calendar_service()
        
        # Get current time in UTC
        now = datetime.datetime.now(datetime.UTC).isoformat()
        
        print(f"Fetching {max_results} upcoming events...")
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "No upcoming events found."
        
        output = f"📅 Upcoming {len(events)} events:\n\n"
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No title')
            location = event.get('location', '')
            
            output += f"{i}. {summary}\n"
            output += f"   Time: {start}\n"
            if location:
                output += f"   Location: {location}\n"
            output += "\n"
        
        return output
    
    except Exception as e:
        return f"❌ Error fetching events: {str(e)}"

def get_upcoming_events_raw(max_results: int=100):
    """
    Get raw event data (for internal use by conflict checking).
    
    Args:
        max_results: Maximum number of events to return
    
    Returns:
        List of event dictionaries
    """
    try:
        service = get_calendar_service()
        now = datetime.datetime.now(datetime.UTC).isoformat()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return events_result.get('items', [])
    
    except Exception as e:
        print(f"❌ Error fetching events: {str(e)}")
        return []

def conflict_calendar(event_new):
    """
    Find conflict events with a new event.

    Args:
        event_new: New event dict with 'start' and 'end' keys containing 'dataTime'

    Return:
        List of conflicting events
    """
 
    overlap = []
    events= get_upcoming_events_raw()

    new_start = event_new['start']['dateTime']
    new_end = event_new['end']['dateTime']

    for ev in events:
        # Get existing event times
        ev_start = ev['start'].get('dateTime', ev['start'].get('date'))
        ev_end = ev['end'].get('dateTime', ev['end'].get('date'))

        if new_start < ev_end and new_end > ev_start:  
            overlap.append({
                'summary': ev.get('summary', 'No title'),
                'start': ev_start,
                'end': ev_end
            })
    
    print(f"Found {len(overlap)} conflicting events")
    return overlap
    

    
def create_calendar_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
    force_create: bool = False
) -> str:
    """
    Create a new event in user's Google Calendar.
    
    Args:
        summary: Event title/summary
        start_time: Start time in ISO format (e.g., '2025-11-24T10:00:00+01:00')
        end_time: End time in ISO format (e.g., '2025-11-24T11:00:00+01:00')
        description: Event description (optional)
        location: Event location (optional)
        force_create: If True, create event even if conflicts exist
    
    Returns:
        Confirmation message with event details or conflict warning
    """
    try:
        service = get_calendar_service()
        
        event = {
            'summary': summary,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time},
        }
        
        if not force_create:
            has_conflict = conflict_calendar(event)

            if len(has_conflict) > 0:
                conflict_msg = "⚠️ **Time Conflict Detected!**\n\n"
                conflict_msg += f"Your new event '{summary}' conflicts with:\n\n"
                
                for i, conf in enumerate(has_conflict, 1):
                    conflict_msg += f"{i}. {conf['summary']}\n"
                    conflict_msg += f"   Time: {conf['start']} to {conf['end']}\n\n"
                
                conflict_msg += "Would you still like to add this event? (Reply 'yes' to confirm)"
                return conflict_msg

        if len(has_conflict)>0:
            return "Confliction"
        else:
            if description:
                event['description'] = description
            if location:
                event['location'] = location
            
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return (
                f"✅ Event created successfully!\n\n"
                f"Title: {summary}\n"
                f"Start: {start_time}\n"
                f"End: {end_time}\n"
                f"Event Link: {created_event.get('htmlLink', 'N/A')}"
            )
        
    except Exception as e:
        return f"❌ Error creating event: {str(e)}"


def force_create_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = ""
) -> str:
    """
    Force create an event even if there are conflicts.
    Use this ONLY when the user explicitly confirms they want to create 
    an event despite time conflicts.
    
    Args:
        summary: Event title/summary
        start_time: Start time in ISO format
        end_time: End time in ISO format
        description: Event description (optional)
        location: Event location (optional)
    
    Returns:
        Confirmation message with event details
    """
    try:
        service = get_calendar_service()
        
        event = {
            'summary': summary,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time},
        }
        
        if description:
            event['description'] = description
        if location:
            event['location'] = location
        
        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        return (
            f"✅ Event created successfully (despite conflicts)!\n\n"
            f"Title: {summary}\n"
            f"Start: {start_time}\n"
            f"End: {end_time}\n"
            f"Event Link: {created_event.get('htmlLink', 'N/A')}"
        )
        
    except Exception as e:
        return f"❌ Error creating event: {str(e)}"
    
def create_meeting_with_attendees(
    summary: str,
    start_time: str,
    end_time: str,
    attendee_emails: List[str],
    description: str = "",
    location: str = "",
    send_notifications: bool = True,
    conference_solution: bool = False
) -> str:
    """
    Create a meeting and send invitations to attendees.
    
    Args:
        summary: Meeting title/summary
        start_time: Start time in ISO format (e.g., '2025-11-24T10:00:00+01:00')
        end_time: End time in ISO format (e.g., '2025-11-24T11:00:00+01:00')
        attendee_emails: List of attendee email addresses (e.g., ['user@example.com'])
        description: Meeting description (optional)
        location: Meeting location (optional)
        send_notifications: Whether to send email invitations (default: True)
        conference_solution: Whether to add Google Meet link (default: False)
    
    Returns:
        Confirmation message with meeting details and attendee list
    """
    try:
        service = get_calendar_service()
        
        # Build attendees list
        attendees = [{'email': email} for email in attendee_emails]
        
        event = {
            'summary': summary,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time},
            'attendees': attendees,
        }
        
        if description:
            event['description'] = description
        if location:
            event['location'] = location
        
        # Add Google Meet conference if requested
        if conference_solution:
            event['conferenceData'] = {
                'createRequest': {
                    'requestId': f"meet-{datetime.datetime.now().timestamp()}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        
        # Create the event
        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='all' if send_notifications else 'none',
            conferenceDataVersion=1 if conference_solution else 0
        ).execute()
        
        # Format response
        output = f"✅ Meeting created successfully!\n\n"
        output += f"Title: {summary}\n"
        output += f"Start: {start_time}\n"
        output += f"End: {end_time}\n"
        output += f"\n👥 Attendees invited ({len(attendee_emails)}):\n"
        for email in attendee_emails:
            output += f"   • {email}\n"
        
        if conference_solution and 'hangoutLink' in created_event:
            output += f"\n🎥 Google Meet: {created_event['hangoutLink']}\n"
        
        output += f"\n📧 Email invitations: {'Sent' if send_notifications else 'Not sent'}\n"
        output += f"Event Link: {created_event.get('htmlLink', 'N/A')}"
        
        return output
    
    except Exception as e:
        return f"❌ Error creating meeting: {str(e)}"


def check_free_busy(
    attendee_emails: List[str],
    time_min: str,
    time_max: str
) -> str:
    """
    Check free/busy status for attendees in a given time range.
    
    Args:
        attendee_emails: List of email addresses to check
        time_min: Start of time range in ISO format
        time_max: End of time range in ISO format
    
    Returns:
        Formatted string showing busy times for each attendee
    """
    try:
        service = get_calendar_service()
        
        body = {
            "timeMin": time_min,
            "timeMax": time_max,
            "items": [{"id": email} for email in attendee_emails]
        }
        
        freebusy_result = service.freebusy().query(body=body).execute()
        calendars = freebusy_result.get('calendars', {})
        
        output = f"📊 Free/Busy Status ({time_min} to {time_max}):\n\n"
        
        for email in attendee_emails:
            calendar_data = calendars.get(email, {})
            busy_times = calendar_data.get('busy', [])
            
            output += f"👤 {email}:\n"
            if not busy_times:
                output += "   ✅ Free during this time\n"
            else:
                output += f"   🔴 Busy periods ({len(busy_times)}):\n"
                for busy in busy_times:
                    output += f"      • {busy['start']} to {busy['end']}\n"
            output += "\n"
        
        return output
    
    except Exception as e:
        return f"❌ Error checking availability: {str(e)}"


def find_meeting_slots(
    attendee_emails: List[str],
    duration_minutes: int,
    time_min: str,
    time_max: str,
    max_suggestions: int = 3
) -> str:
    """
    Find available meeting slots that work for all attendees.
    
    Args:
        attendee_emails: List of email addresses
        duration_minutes: Meeting duration in minutes
        time_min: Start of search range in ISO format
        time_max: End of search range in ISO format
        max_suggestions: Maximum number of time slots to suggest (default: 3)
    
    Returns:
        Suggested meeting times that work for all attendees
    """
    try:
        service = get_calendar_service()
        
        # Add your own calendar to the list
        all_attendees = attendee_emails.copy()
        
        body = {
            "timeMin": time_min,
            "timeMax": time_max,
            "items": [{"id": email} for email in all_attendees]
        }
        
        freebusy_result = service.freebusy().query(body=body).execute()
        calendars = freebusy_result.get('calendars', {})
        
        # Collect all busy times
        all_busy_times = []
        for email in all_attendees:
            calendar_data = calendars.get(email, {})
            busy_times = calendar_data.get('busy', [])
            all_busy_times.extend(busy_times)
        
        # Find free slots (simplified algorithm)
        start_dt = datetime.datetime.fromisoformat(time_min.replace('Z', '+00:00'))
        end_dt = datetime.datetime.fromisoformat(time_max.replace('Z', '+00:00'))
        duration = datetime.timedelta(minutes=duration_minutes)
        
        suggestions = []
        current_time = start_dt
        
        while current_time + duration <= end_dt and len(suggestions) < max_suggestions:
            slot_start = current_time
            slot_end = current_time + duration
            
            # Check if this slot conflicts with any busy time
            is_free = True
            for busy in all_busy_times:
                busy_start = datetime.datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                
                # Check for overlap
                if not (slot_end <= busy_start or slot_start >= busy_end):
                    is_free = False
                    break
            
            if is_free:
                suggestions.append({
                    'start': slot_start.isoformat(),
                    'end': slot_end.isoformat()
                })
            
            # Move to next 30-minute slot
            current_time += datetime.timedelta(minutes=30)
        
        # Format output
        if not suggestions:
            return f"❌ No available time slots found for all attendees in the given range."
        
        output = f"💡 Found {len(suggestions)} available time slot(s) for a {duration_minutes}-minute meeting:\n\n"
        for i, slot in enumerate(suggestions, 1):
            output += f"{i}. {slot['start']} to {slot['end']}\n"
        
        output += f"\n👥 All {len(attendee_emails)} attendee(s) are available during these times."
        
        return output
    
    except Exception as e:
        return f"❌ Error finding meeting slots: {str(e)}"


def search_events(query: str, max_results: int = 10) -> str:
    """
    Search for events in user's calendar by keyword.
    
    Args:
        query: Search keyword
        max_results: Maximum number of results (default: 10)
    
    Returns:
        Formatted string of matching events
    """
    try:
        service = get_calendar_service()
        
        # Get current time in UTC
        now = datetime.datetime.now(datetime.UTC).isoformat()
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            q=query,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return f"No events found matching '{query}'."
        
        output = f"🔍 Found {len(events)} event(s) matching '{query}':\n\n"
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No title')
            
            output += f"{i}. {summary}\n"
            output += f"   Time: {start}\n\n"
        
        return output
    
    except Exception as e:
        return f"❌ Error searching events: {str(e)}"