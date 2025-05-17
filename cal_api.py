import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.cal.com/v1"
API_KEY = os.getenv("CAL_API_KEY")


def list_bookings(user_email: str):
    """List bookings by user email."""
    url = f"{BASE_URL}/bookings?apiKey={API_KEY}&userEmail={user_email}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error listing bookings: {response.status_code} - {response.text}")
    return response.json()


def cancel_booking(booking_id: str):
    """Cancel a booking by ID."""
    url = f"{BASE_URL}/bookings/{booking_id}?apiKey={API_KEY}"
    response = requests.delete(url)
    if response.status_code != 200:
        raise Exception(f"Error cancelling booking: {response.status_code} - {response.text}")
    return response.json()


def create_booking(event_type_id: str, name: str, email: str, start: str, end: str):
    """Create a new booking (requires you to know available slot)."""
    url = f"{BASE_URL}/bookings?apiKey={API_KEY}"
    payload = {
        "eventTypeId": event_type_id,
        "title": f"Meeting with {name}",
        "start": start,    # ISO 8601 string (e.g. 2025-05-16T15:00:00.000Z)
        "end": end,        # ISO 8601 string
        "email": email,
        "name": name,
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error creating booking: {response.status_code} - {response.text}")
    return response.json()
