import requests
import os
from dotenv import load_dotenv

# Load from .env
load_dotenv()

api_key = os.getenv("CAL_API_KEY")

# Construct URL with query param
url = f"https://api.cal.com/v1/bookings?apiKey={api_key}"

response = requests.get(url)

print(f"Status Code: {response.status_code}")
print("Response Body:")
print(response.text)