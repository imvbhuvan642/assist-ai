---
name: calendar-management
description: Manage Google Calendar events, including searching, creating, updating, and deleting calendar events.
---

# Calendar Management Skill

## When to Use This Skill

Use this skill when the user asks you to interact with their calendar, such as:
- Checking what events are scheduled for today or this week.
- Summarizing upcoming meetings or schedule conflicts.
- Creating new events or meetings on the calendar.
- Updating or deleting existing calendar events.

## Available Tools

The `CalendarToolkit` provides tools (usually from `langchain-google-community`) to manage Google Calendar events, typically including functions to search, create, update, and delete events. Let the LangChain toolkit natively handle the API calls.

## Workflow

### 1. Searching for Events
- When asked what is on the schedule, use the calendar search tool to fetch upcoming events for a specified date range.
- Provide a clear, natural language summary of the returned events.

### 2. Creating Events
- When asked to add a meeting or appointment, gather the event title, start time, end time, and optionally location/description from the user.
- Use the calendar event creation tool to schedule the meeting.

### 3. Managing Events
- Use search tools to find the exact event ID before attempting to update or delete any event.
- Use the calendar update/delete tools using the found event ID.

## Example: Summarizing Upcoming Events
**User:** "What's on my schedule for tomorrow?"
1. Search the calendar for events occurring tomorrow.
2. Read the results from the calendar search tool.
3. Provide a chronological summary of the day to the user.

## Example: Creating an Event
**User:** "Schedule a meeting with Bob for tomorrow at 2 PM to discuss the project."
1. Extract the event details: title = "Meeting with Bob to discuss the project", time = "Tomorrow 2:00 PM". (Translate to ISO 8601 if needed).
2. Use the calendar creation tool to create the event.
3. Inform the user that the event has been successfully placed on their calendar.

## Quality Guidelines
- Ensure dates and times are correctly formatted (e.g., handling time zones implicitly based on user preference or local context).
- For overlapping meetings, inform the user about the conflict when summarizing or scheduling new meetings.
