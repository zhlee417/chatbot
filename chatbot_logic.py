import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from cal_api import (
    list_bookings,
    create_booking,
    cancel_booking as api_cancel_booking, 
    get_slots
)
from datetime import datetime, timedelta
import pytz # Import pytz

# Load .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
CURRENT_USER_EMAIL = os.getenv("CURRENT_USER_EMAIL")
CURRENT_USER_NAME = CURRENT_USER_EMAIL.split('@')[0] if CURRENT_USER_EMAIL else "User" 
USER_TIMEZONE = "America/Los_Angeles" # Define user's timezone

client = OpenAI(api_key=api_key)
la_tz = pytz.timezone(USER_TIMEZONE) # Timezone object

# Function definitions
function_definitions = [
    {
        "name": "list_bookings",
        "description": "List all bookings for the current logged-in user.",
        "parameters": { 
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "create_booking",
        "description": f"Book a new meeting for the current logged-in user. Times should be specified in {USER_TIMEZONE} time. If name and email are not specified in the prompt, they default to the current user's details.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the person attending the meeting. Defaults to the current user's name if not specified."},
                "email": {"type": "string", "description": "Email of the person attending the meeting. Defaults to the current user's email if not specified."},
                "start": {"type": "string", "description": f"Start date and time in YYYY-MM-DDTHH:MM format (e.g., 2025-05-21T17:00) in {USER_TIMEZONE} time."},
                "end": {"type": "string", "description": f"End date and time in YYYY-MM-DDTHH:MM format (e.g., 2025-05-21T17:15) in {USER_TIMEZONE} time."}
            },
            "required": ["start", "end"] 
        }
    },
    {
        "name": "cancel_booking",
        "description": f"Cancel an existing booking for the current user based on its time and date in {USER_TIMEZONE} time.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_time": {"type": "string", "description": f"The start time of the event to cancel, in HH:MM format (e.g., '17:00', '05:00PM') in {USER_TIMEZONE} time."},
                "event_date": {"type": "string", "description": f"The date of the event to cancel (e.g., 'today', 'tomorrow', '2025-05-21') in {USER_TIMEZONE} time. Defaults to 'today' if not specified."}
            },
            "required": ["event_time"]
        }
    },
    {
        "name": "get_slots",
        "description": f"Check available slots for a specific date for the current user's default event type. The date is interpreted in {USER_TIMEZONE} time.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": f"The date to check for slots, in YYYY-MM-DD format (e.g., '2025-05-21') for {USER_TIMEZONE}."}
            },
            "required": ["date"]
        }
    }
]

def parse_datetime_from_cal_api(datetime_str):
    """Parses datetime string from Cal.com API (e.g., '2025-05-21T16:00:00.000Z') to a UTC-aware datetime object."""
    return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))

def find_and_cancel_booking(event_time_str: str, event_date_str: str = "today"):
    """Finds a booking by time and date (in USER_TIMEZONE) for the current user and cancels it."""
    if not CURRENT_USER_EMAIL:
        return "Error: Current user email is not configured."

    try:
        now_in_user_tz = datetime.now(la_tz)
        target_date_obj = None
        if event_date_str.lower() == "today":
            target_date_obj = now_in_user_tz.date()
        elif event_date_str.lower() == "tomorrow":
            target_date_obj = (now_in_user_tz + timedelta(days=1)).date()
        else:
            try:
                target_date_obj = datetime.strptime(event_date_str, "%Y-%m-%d").date()
            except ValueError:
                return f"Error: Invalid date format for event_date: {event_date_str}. Please use YYYY-MM-DD, 'today', or 'tomorrow'."

        parsed_time = None
        fmts = ["%H:%M", "%I:%M%p", "%I:%M %p"]
        for fmt in fmts:
            try:
                parsed_time = datetime.strptime(event_time_str, fmt).time()
                break
            except ValueError:
                continue
        if parsed_time is None:
            raise ValueError(f"Could not parse time: {event_time_str}")
        
        # Create a naive datetime, then localize it to USER_TIMEZONE
        target_datetime_naive = datetime.combine(target_date_obj, parsed_time)
        target_datetime_user_tz = la_tz.localize(target_datetime_naive)
        
        print(f"Attempting to find booking for user {CURRENT_USER_EMAIL} at {target_datetime_user_tz.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")

        user_bookings_data = list_bookings() 
        
        if 'bookings' not in user_bookings_data or not user_bookings_data['bookings']:
            return f"No bookings found for {CURRENT_USER_EMAIL}."

        matching_bookings = []
        for booking in user_bookings_data['bookings']:
            if booking.get('status') == 'CANCELLED': 
                continue
            
            booking_start_utc = parse_datetime_from_cal_api(booking['startTime'])
            booking_start_user_tz = booking_start_utc.astimezone(la_tz)

            if booking_start_user_tz == target_datetime_user_tz:
                matching_bookings.append(booking)
        
        if not matching_bookings:
            return f"No active booking found for {CURRENT_USER_EMAIL} at {target_datetime_user_tz.strftime('%Y-%m-%d %H:%M')} ({USER_TIMEZONE})."
        
        if len(matching_bookings) > 1:
            titles = [b.get('title', 'Untitled Event') for b in matching_bookings]
            return f"Multiple active bookings found for {target_datetime_user_tz.strftime('%Y-%m-%d %H:%M')} ({USER_TIMEZONE}): {'; '.join(titles)}. Please specify by ID."

        found_booking_id = matching_bookings[0]['id']
        
        print(f"Found booking ID: {found_booking_id} to cancel.")
        cancellation_result = api_cancel_booking(str(found_booking_id))
        return f"Booking ID {found_booking_id} cancelled successfully. Details: {cancellation_result}"

    except Exception as e:
        print(f"Exception in find_and_cancel_booking: {e}") 
        return f"Error during cancellation process: {str(e)}"


def handle_user_input(user_message: str):
    system_message = f"""You are a helpful calendar assistant.
All operations are for the current logged-in user: Name: {CURRENT_USER_NAME}, Email: {CURRENT_USER_EMAIL}.
Their timezone is {USER_TIMEZONE}. Interpret all date/time input from the user as being in {USER_TIMEZONE}.
When providing times to functions, ensure they are in the format YYYY-MM-DDTHH:MM as per {USER_TIMEZONE}.
If a name or email for a booking is not explicitly mentioned, assume it is for the current user.
Today's date (in {USER_TIMEZONE}) is {datetime.now(la_tz).strftime('%Y-%m-%d')}."""
    
    response = client.chat.completions.create(
        model="gpt-4-0613", 
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        functions=function_definitions,
        function_call="auto"
    )

    message = response.choices[0].message

    if message.function_call:
        func_name = message.function_call.name
        args = json.loads(message.function_call.arguments)

        if func_name == "list_bookings":
            return list_bookings()

        elif func_name == "create_booking":
            booking_name = args.get("name", CURRENT_USER_NAME)
            booking_email = args.get("email", CURRENT_USER_EMAIL)
            
            if not booking_name or not booking_email:
                return "Error: Could not determine name and email for the booking."

            start_local_from_llm = args["start"] # e.g., "2025-05-21T09:45"
            end_local_from_llm = args["end"]     # e.g., "2025-05-21T10:00"
            
            try:
                # Convert to datetime objects, then localize, then format with offset
                naive_start_dt = datetime.strptime(start_local_from_llm, "%Y-%m-%dT%H:%M")
                local_start_dt_aware = la_tz.localize(naive_start_dt) # Add timezone info
                start_iso_with_offset = local_start_dt_aware.isoformat() # YYYY-MM-DDTHH:MM:SS-07:00

                naive_end_dt = datetime.strptime(end_local_from_llm, "%Y-%m-%dT%H:%M")
                local_end_dt_aware = la_tz.localize(naive_end_dt)
                end_iso_with_offset = local_end_dt_aware.isoformat()

            except ValueError:
                return f"Error: Invalid start or end time format from LLM. Expected YYYY-MM-DDTHH:MM. Received start: '{start_local_from_llm}', end: '{end_local_from_llm}'"

            return create_booking(
                booking_name,
                booking_email,
                start_iso_with_offset, # e.g., "2025-05-21T09:45:00-07:00"
                end_iso_with_offset    # e.g., "2025-05-21T10:00:00-07:00"
            )

        elif func_name == "cancel_booking": 
            event_time = args.get("event_time")
            event_date = args.get("event_date", "today") 
            return find_and_cancel_booking(event_time, event_date)

        elif func_name == "get_slots":
            return get_slots(args["date"], time_zone=USER_TIMEZONE)

        return f"Unknown function: {func_name}"

    return message.content