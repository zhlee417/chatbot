from cal_api import list_bookings

# Replace with your Cal.com email address
user_email = "your_email@domain.com"

try:
    bookings = list_bookings(user_email)
    print("Bookings retrieved successfully:")
    print(bookings)
except Exception as e:
    print("Failed to retrieve bookings:")
    print(e)