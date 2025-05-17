from cal_api import get_event_types

event_types_data = get_event_types()
event_types = event_types_data["event_types"]

print("✅ Event types:")
for et in event_types:
    print(f"- ID: {et['id']}, Title: {et['title']}, Link: {et['link']}")