import os
import logging
from dotenv import load_dotenv

load_dotenv()

from google.genai import types
from google.adk.tools import FunctionTool

# Import Agent base and InvocationContext
try:
    from google.adk.agents import Agent
    from google.adk.agents.invocation_context import InvocationContext
    from google.adk.events import Event
except ImportError:
    from google.adk import Agent, InvocationContext, Event

from agent.prompt import get_system_prompt
# Import your calendar tools - FIXED IMPORTS
from agent.tools.calendar_tools import (
    list_upcoming_events,
    create_calendar_event,
    search_events,
    create_meeting_with_attendees,
    check_free_busy,
    find_meeting_slots
)

# Import your new intelligent prompt tools
from agent.tools.prompt_tools import (
    parse_user_input_to_task,
    analyze_calendar_events,
    smart_create_event_from_text,
    get_movable_events_from_calendar
)

from agent.tools.weather_tools import (
    get_location,
    get_current_weather,
    start_weather_reminder, 
    stop_weather_reminder,
    scheduler, 
    start_weather_reminder, 
    stop_weather_reminder,
    get_reminder_status
)

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Register calendar tools with ADK FunctionTool wrapper
tools = [
    FunctionTool(list_upcoming_events),
    FunctionTool(create_calendar_event),
    FunctionTool(search_events),
    FunctionTool(create_meeting_with_attendees),
    FunctionTool(check_free_busy),
    FunctionTool(find_meeting_slots),
    # Add the new intelligent tools
    FunctionTool(smart_create_event_from_text),
    FunctionTool(parse_user_input_to_task),
    FunctionTool(analyze_calendar_events),
    FunctionTool(get_movable_events_from_calendar),
    FunctionTool(get_location),
    FunctionTool(get_current_weather),
    FunctionTool(start_weather_reminder),
    FunctionTool(stop_weather_reminder),
    FunctionTool(get_reminder_status),
    
]

# Rest of your agent code stays exactly the same...
class CalendarAgent(Agent):
    """Calendar agent that can read and create Google Calendar events."""

    async def _run_async_impl(self, ctx: InvocationContext):
        # Extract user info for logging
        user_email = None
        try:
            if getattr(ctx, "user", None):
                user_email = getattr(ctx.user, "email", None)
            if not user_email and getattr(ctx, "session", None):
                user_email = getattr(ctx.session, "user_id", None)
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract user email: {e}")
            user_email = "UNKNOWN"

        logger.info(f"📅 Calendar Agent - User: {user_email}")
        logger.debug(f"🧾 Full session context: {ctx.session.__dict__}")

        # Proceed with normal agent run
        async for event in super()._run_async_impl(ctx):
            yield event




def build_agent() -> Agent:
    """Construct and return the Calendar agent."""
    model = os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-001")
    system_prompt = get_system_prompt()

    calendar_agent = CalendarAgent(
        name=os.getenv("AGENT_NAME", "calendar_agent"),
        model=model,
        tools=tools,
        instruction=system_prompt,
        generate_content_config=types.GenerateContentConfig(temperature=0.7),
    )

    scheduler.start()

    return calendar_agent


# Build the root agent
root_agent = build_agent()

# Expose agent for ADK deployment
agent = root_agent


if __name__ == "__main__":
    print("🗓️ Advanced Calendar Agent loaded successfully with ADK!")
    print("=" * 60)
    print("Agent capabilities:")
    print("  ✓ List upcoming events")
    print("  ✓ Create personal calendar events")
    print("  ✓ Schedule meetings with attendees (sends invitations)")
    print("  ✓ Check attendee availability (free/busy)")
    print("  ✓ Find available meeting slots")
    print("  ✓ Add Google Meet links to meetings")
    print("  ✓ Search events by keyword")
    print("  🧠 Smart natural language parsing")
    print("  📊 Calendar flexibility analysis")
    print("=" * 60)