from chatbot_logic import handle_user_input
import os 
from dotenv import load_dotenv 

load_dotenv() 

print("\n Test 1: List bookings")
response = handle_user_input("Show me all my scheduled meetings") 
print(response)
print("-" * 80)

print("\n Test 2: Get available slots on 2025-05-21")
response = handle_user_input("What are my available slots on 2025-05-21?")
print(response)
print("-" * 80)

print("\n Test 3: Create a new booking")
response = handle_user_input(
    "Help me book a meeting from 11:45 to 12:00 today"
)
print(response)
print("-" * 80)

# print("\n Test 4: Cancel a booking")
# response = handle_user_input("cancel my event at 11:45 today")  
# print(response)
# print("-" * 80)