import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.cal.com/v1"
API_KEY = os.getenv("CAL_API_KEY")
CURRENT_USER_EMAIL = os.getenv("CURRENT_USER_EMAIL")
CURRENT_USER_ID = os.getenv("CURRENT_USER_ID")
DEFAULT_USER_TIMEZONE = "America/Los_Angeles" # Default, can be overridden


def list_bookings(user_email: str = None):
    """List bookings by user email. If no email is provided, uses the current user."""
    if not user_email:
        user_email = CURRENT_USER_EMAIL
        
    url = f"{BASE_URL}/bookings?apiKey={API_KEY}&userEmail={user_email}"
    print(f"GET {url}")
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error listing bookings: {response.status_code} - {response.text}")
    return response.json()


def cancel_booking(booking_id: str):
    """Cancel a booking by ID."""
    url = f"{BASE_URL}/bookings/{booking_id}?apiKey={API_KEY}"
    print(f"DELETE {url}")
    response = requests.delete(url)
    if response.status_code != 200:
        raise Exception(f"Error cancelling booking: {response.status_code} - {response.text}")
    return response.json()


def get_slots(date: str, time_zone: str = DEFAULT_USER_TIMEZONE):
    """Get available slots for the default event type, a specific date, and timezone for the current user."""
    event_type_id = int(os.getenv("DEFAULT_EVENT_TYPE_ID"))
    
    if not CURRENT_USER_ID:
        raise ValueError("CURRENT_USER_ID is not set in .env file.")

    # API expects startTime and endTime to be local to the provided timeZone if timeZone param is used
    # Times should not have 'Z' if timeZone parameter is present.
    url = (
        f"{BASE_URL}/slots"
        f"?apiKey={API_KEY}"
        f"&userId={CURRENT_USER_ID}"
        f"&eventTypeId={event_type_id}"
        f"&startTime={date}T00:00:00" # Local start of day
        f"&endTime={date}T23:59:59"   # Local end of day
        f"&timeZone={time_zone}"       # Specify the timezone
    )

    print(f"GET {url}") 

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error response text: {response.text[:500]}...") 
        raise Exception(f"Error fetching slots: {response.status_code} - {response.text[:200]}")
    
    data = response.json()
    if isinstance(data, dict) and 'slots' in data:
        return data
    elif isinstance(data, list): 
        return {'slots': data}
    else: 
        print(f"Unexpected slots API response structure: {data}")
        return {'slots': []}


def create_booking(name: str, email: str, start_local_str: str, end_local_str: str):
    """
    Create a new booking using the default event type.
    Start and end times are local time strings for the DEFAULT_USER_TIMEZONE.
    e.g., "2025-05-21T09:30"
    """
    event_type_id = int(os.getenv("DEFAULT_EVENT_TYPE_ID"))
    url = f"{BASE_URL}/bookings?apiKey={API_KEY}"

    payload = {
        "eventTypeId": event_type_id,
        "start": start_local_str, # Should be like "2025-05-21T09:30:00" or "2025-05-21T09:30"
        "end": end_local_str,     # Should be like "2025-05-21T09:45:00" or "2025-05-21T09:45"
        "responses": {
            "name": name,
            "email": email,
            "guests": [],
            "location": {
                "value": "integrations:daily",
                "optionValue": "" 
            }
        },
        "timeZone": DEFAULT_USER_TIMEZONE, # This tells Cal.com how to interpret start/end
        "language": "en",
        "userId": int(CURRENT_USER_ID), 
        "metadata": {}
    }

    print(f"POST {url}")
    print("Booking payload:", payload)
    
    response = requests.post(url, json=payload)
    
    print(f"Response status: {response.status_code}")
    try:
        print(f"Response body: {response.json()}")
    except:
        print(f"Raw response: {response.text[:200]}...")
    
    if response.status_code != 200:
        if "no_available_users_found_error" in response.text or "No available users found" in response.text:
            raise Exception("Error: No available users found for this time slot or the event type is not bookable by the specified user. Please choose a different time or check event type settings.")
        raise Exception(f"Error creating booking: {response.status_code} - {response.text[:200]}...")
    
    return response.json()


def get_event_types():
    """Fetch all event types associated with the API key."""
    url = f"{BASE_URL}/event-types?apiKey={API_KEY}"
    if CURRENT_USER_ID: 
        url += f"&userId={CURRENT_USER_ID}"
        
    print(f"GET {url}")
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching event types: {response.status_code} - {response.text}")
    return response.json()