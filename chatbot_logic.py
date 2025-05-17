import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from cal_api import list_bookings

# Load .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Function definitions
function_definitions = [
    {
        "name": "list_bookings",
        "description": "List all bookings for a user by email",
        "parameters": {
            "type": "object",
            "properties": {
                "user_email": {
                    "type": "string",
                    "description": "The user's email address"
                }
            },
            "required": ["user_email"]
        }
    }
]

def handle_user_input(user_message: str):
    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[
            {"role": "user", "content": user_message}
        ],
        functions=function_definitions,
        function_call="auto"
    )

    message = response.choices[0].message

    if message.function_call:
        func_name = message.function_call.name
        arguments = json.loads(message.function_call.arguments)

        if func_name == "list_bookings":
            return list_bookings(arguments["user_email"])

        return f"Function '{func_name}' is not yet implemented."

    return message.content
