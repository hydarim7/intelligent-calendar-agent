import json
from typing import Dict, List, Any
import logging
import os

logger = logging.getLogger(__name__)

def parse_user_input_to_task(user_input: str) -> str:
    """
    Convert natural language requests into structured JSON data for calendar events.
    
    Args:
        user_input: Natural language description of a task or event
    
    Returns:
        Structured JSON string with task details
    """
    
    # For now, we'll do rule-based parsing until AI integration is stable
    # This gives you immediate functionality while we fix the AI imports
    
    task_data = {
        "task_name": user_input,
        "priority": "CORE",  # Default
        "flexibility": "FLOATING",  # Default
        "duration_minutes": 60,  # Default
        "preferred_time": "ANY"
    }
    
    # Simple rule-based analysis
    user_lower = user_input.lower()
    
    # Detect priority
    if any(word in user_lower for word in ['deadline', 'appointment', 'meeting', 'urgent', 'must']):
        task_data["priority"] = "CRITICAL"
    elif any(word in user_lower for word in ['gym', 'exercise', 'work', 'study', 'important']):
        task_data["priority"] = "CORE"
    else:
        task_data["priority"] = "FILLER"
    
    # Detect flexibility
    if any(word in user_lower for word in ['at', 'exactly', 'sharp', 'appointment']):
        task_data["flexibility"] = "FIXED"
    elif any(word in user_lower for word in ['today', 'this morning', 'this afternoon']):
        task_data["flexibility"] = "FLOATING"
    else:
        task_data["flexibility"] = "LIQUID"
    
    # Detect duration
    if any(word in user_lower for word in ['quick', 'brief', 'short']):
        task_data["duration_minutes"] = 15
    elif any(word in user_lower for word in ['gym', 'workout', 'exercise']):
        task_data["duration_minutes"] = 90
    elif any(word in user_lower for word in ['meeting', 'call']):
        task_data["duration_minutes"] = 30
    
    # Extract time if mentioned
    import re
    time_match = re.search(r'(\d{1,2})(:\d{2})?\s*(am|pm|AM|PM)', user_input)
    if time_match:
        hour = int(time_match.group(1))
        minute = time_match.group(2) or ":00"
        ampm = time_match.group(3).lower()
        
        if ampm == 'pm' and hour != 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0
            
        task_data["hard_start_time"] = f"{hour:02d}{minute}"
        task_data["flexibility"] = "FIXED"
    
    print("------------")
    print(f"time: {task_data}")
    print("------------")
    return json.dumps(task_data, indent=2)


def analyze_calendar_events(events_list: List[str]) -> str:
    """
    Analyze calendar events to determine if they are LOCKED or MOVABLE.
    
    Args:
        events_list: List of event titles from Google Calendar
    
    Returns:
        JSON analysis of which events can be moved
    """
    
    analysis_results = []
    
    for event_title in events_list:
        title_lower = event_title.lower()
        
        # Rule-based classification
        is_locked = False
        
        # Keywords that indicate LOCKED events
        locked_keywords = [
            'meeting', 'sync', 'standup', 'call', 'interview', 'appointment',
            'lunch', 'dinner', 'client', 'team', 'with', 'dentist', 'doctor',
            'conference', 'presentation', 'demo', 'review'
        ]
        
        # Keywords that indicate MOVABLE events
        movable_keywords = [
            'gym', 'workout', 'exercise', 'study', 'read', 'write', 'work',
            'deep work', 'focus', 'personal', 'break', 'rest'
        ]
        
        if any(keyword in title_lower for keyword in locked_keywords):
            status = "LOCKED"
        elif any(keyword in title_lower for keyword in movable_keywords):
            status = "MOVABLE"
        else:
            # Default: if it contains names or multiple words, probably locked
            if len(event_title.split()) > 2 or any(c.isupper() for c in event_title[1:]):
                status = "LOCKED"
            else:
                status = "MOVABLE"
        
        analysis_results.append({
            "title": event_title,
            "status": status
        })
    
    return json.dumps(analysis_results, indent=2)


def smart_create_event_from_text(user_input: str) -> str:
    """
    Create a calendar event using intelligent parsing of natural language.
    
    Args:
        user_input: Natural language description of what to schedule
    
    Returns:
        Confirmation message with parsed task details
    """
    try:
        # Parse the user input
        parsed_json = parse_user_input_to_task(user_input)
        
        # Parse as JSON
        try:
            task_data = json.loads(parsed_json)
        except json.JSONDecodeError:
            return f"⚠️ Could not parse task properly. Raw output:\n{parsed_json}"
        
        # Format the response
        output = "🧠 Intelligent Task Analysis:\n\n"
        output += f"📝 Task: {task_data.get('task_name', 'Unknown')}\n"
        output += f"⭐ Priority: {task_data.get('priority', 'Unknown')}\n"
        output += f"🔄 Flexibility: {task_data.get('flexibility', 'Unknown')}\n"
        output += f"⏱️ Duration: {task_data.get('duration_minutes', 'Unknown')} minutes\n"
        
        if 'hard_start_time' in task_data:
            output += f"⏰ Fixed Start: {task_data['hard_start_time']}\n"
        elif 'hard_end_time' in task_data:
            output += f"⏰ Must End By: {task_data['hard_end_time']}\n"
        elif 'preferred_time' in task_data:
            output += f"🎯 Preferred Time: {task_data['preferred_time']}\n"
        
        output += "\n💡 To actually create this event, please provide specific date/time details!"
        output += f"\n\n📋 Parsed Data:\n```json\n{json.dumps(task_data, indent=2)}\n```"
        
        return output
    
    except Exception as e:
        return f"❌ Error in smart parsing: {str(e)}"


def get_movable_events_from_calendar() -> str:
    """
    Get current calendar events and analyze which ones are movable.
    
    Returns:
        Analysis of which events can be rescheduled
    """
    try:
        # Import here to avoid circular imports
        from .calendar_tools import get_calendar_service
        import datetime
        
        service = get_calendar_service()
        
        # Get events for the next 7 days
        now = datetime.datetime.now(datetime.UTC).isoformat()
        week_later = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)).isoformat()
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=week_later,
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "📅 No events found in the next 7 days to analyze."
        
        # Extract event titles
        event_titles = []
        for event in events:
            title = event.get('summary', 'Untitled Event')
            event_titles.append(title)
        
        # Analyze the events
        analysis_result = analyze_calendar_events(event_titles)
        
        # Parse and format the result
        try:
            analysis_data = json.loads(analysis_result)
            
            output = "📊 Calendar Flexibility Analysis:\n\n"
            locked_count = 0
            movable_count = 0
            
            for item in analysis_data:
                status = item.get('status', 'UNKNOWN')
                title = item.get('title', 'Unknown')
                
                if status == 'LOCKED':
                    output += f"🔒 {title}\n"
                    locked_count += 1
                else:
                    output += f"🔄 {title}\n"
                    movable_count += 1
            
            output += f"\n📈 Summary: {locked_count} locked, {movable_count} movable events"
            return output
            
        except json.JSONDecodeError:
            return f"⚠️ Analysis completed but couldn't parse results:\n{analysis_result}"
        
    except Exception as e:
        return f"❌ Error analyzing calendar: {str(e)}"