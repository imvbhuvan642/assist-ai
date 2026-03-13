---
name: calendar-management
description: Manage Google Calendar events including creating, searching, updating, deleting, and moving events and reminders.
---

# Calendar Management Skill

## When to Use This Skill

Use this skill when the user asks you to interact with their Google Calendar, such as:
- Creating new events, meetings, or reminders.
- Searching for upcoming events or checking their schedule.
- Updating or rescheduling existing events.
- Deleting or cancelling events.
- Moving events between calendars.
- Checking what calendars are available.

## Available Tools

The `CalendarToolkit` provides the following tools:
- **`create_calendar_event`**: Create a new event on Google Calendar. Supports setting title, start/end times, description, location, attendees, and reminders.
- **`search_calendar_events`**: Search for events within a date/time range or by keyword query.
- **`update_calendar_event`**: Update an existing event's details (title, time, description, attendees, etc.) using the event ID.
- **`delete_calendar_event`**: Delete an event from the calendar using the event ID.
- **`move_calendar_event`**: Move an event from one calendar to another.
- **`get_calendars_info`**: List all calendars available to the user (primary, shared, subscribed).
- **`get_current_datetime`**: Get the current date and time — useful for scheduling relative events (e.g., "in 2 hours").

## Workflow

### 1. Checking Schedule / Searching Events
- Use `get_current_datetime` first to know what "today" or "now" means.
- Use `search_calendar_events` with the appropriate time range to find events.
- Example: For "What's on my schedule tomorrow?", search from tomorrow 00:00 to tomorrow 23:59.

### 2. Creating Events
- Gather the required details: title (summary), start time, end time.
- Optional: description, location, attendees, reminders.
- Use ISO 8601 format for datetime fields (e.g., `2026-03-15T10:00:00`).
- For all-day events, use date format `2026-03-15`.
- Use `create_calendar_event` with the gathered details.

### 3. Updating Events
- First, use `search_calendar_events` to find the event and get its event ID.
- Then use `update_calendar_event` with the event ID and the fields to update.
- Only include the fields that need to change.

### 4. Deleting Events
- First, search for the event to confirm the correct one and get its event ID.
- Confirm with the user before deleting unless they explicitly said "delete" or "cancel".
- Use `delete_calendar_event` with the event ID.

### 5. Moving Events Between Calendars
- Use `get_calendars_info` to list available calendars if the user doesn't specify a destination.
- Use `move_calendar_event` with the event ID, source calendar ID, and destination calendar ID.

## Example: Creating a Meeting

**User:** "Schedule a team standup tomorrow at 9 AM for 30 minutes"
1. Use `get_current_datetime` to determine tomorrow's date.
2. Use `create_calendar_event` with:
   - summary: "Team Standup"
   - start: "2026-03-14T09:00:00"
   - end: "2026-03-14T09:30:00"
3. Confirm the event was created and share the details.

## Example: Checking Today's Schedule

**User:** "What meetings do I have today?"
1. Use `get_current_datetime` to know today's date.
2. Use `search_calendar_events` with today's date range.
3. Summarize the events in a clear, chronological format.

## Example: Rescheduling an Event

**User:** "Move my 3 PM meeting to 4 PM"
1. Use `search_calendar_events` to find events around 3 PM today.
2. Identify the correct event and get its event ID.
3. Use `update_calendar_event` to change the start and end times.
4. Confirm the change with the user.

## Quality Guidelines
- Always use `get_current_datetime` before scheduling or searching to ensure accurate date/time references.
- When creating events, always confirm the timezone context with the user if ambiguous.
- Always confirm with the user before deleting events unless they explicitly said to delete.
- Present schedules in a clean, chronological, easy-to-read format.
- For recurring events, mention the recurrence pattern clearly.
