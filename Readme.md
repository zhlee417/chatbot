# Demo Video

[![OpenAI cal.com Chatbot](https://img.youtube.com/vi/w5EQb1lRyOo/0.jpg)](https://www.youtube.com/watch?v=w5EQb1lRyOo)

## Overview

Your task is to create an interactive chatbot using OpenAI's function calling capabilities. 
This chatbot will allow a user to interact with your cal.com account directly through the chat interface. 
The chatbot should be able to help the user to book a new event, list the user's active events and cancel events using the cal.com API.

## Requirements

Build a simple chatbot that can interact with the REST API. The chatbot may be a web server, and the user may interact 
with it through REST API. It will be a bonus if you can make the chatbot interactive through a web interface. 

Use OpenAI's function calling feature to integrate external APIs with your chatbot. 
This will involve crafting requests to the cal.com API and processing responses within the chatbot's logic.
Specifically, you'll need to implement the following functionality:

 - When the user says something like "help me to book a meeting", the chatbot will ask for the meeting details such as 
   the date, time and reason, and then create a new event if the time is available.
 - Once the user says something like "show me the scheduled events", retrieve a list of the user's scheduled events based on the user's email.

Bonus points for the following features:
 - When the user says something like "cancel my event at 3pm today", find the event (based on the user's email) and cancel the right event.
 - Implement the feature to reschedule an event booked by the user.
 - Build an interactive web UI. You may use LLM UI framework such as chainlit or streamlit.
