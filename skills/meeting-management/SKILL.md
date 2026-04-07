---
name: meeting-management
description: Manage virtual meetings, specifically scheduling Google Meet conferences.
---

# Meeting Management Skill

## When to Use This Skill

Use this skill whenever the user explicitly asks to schedule a video conference, meeting, team sync, or uses keywords like "Meet", "Google Meet", "sync", or "video call".
This takes precedence over standard calendar scheduling when a video link is strictly necessary.

## Available Tools

- `create_google_meet`: Creates a new Google Calendar event and automatically attaches a Google Meet video conference link.

## Workflow

### 1. Scheduling a Google Meet

- When asked to schedule a meeting, extract the event title (summary), start time, end time, and optionally the attendees' email addresses.
- Both `start_time` and `end_time` MUST be ISO format strings with NO timezone offsets (e.g. `2023-10-25T10:00:00`).
- If no timezone is provided by the user, allow the tool to use its default (`Asia/Kolkata` IST).
- Call `create_google_meet` with the extracted parameters.

### 2. Communicating the Result

- After the tool successfully creates the event, it will return the Event ID, Meet Link, Calendar Link, and the formatted summary.
- **CRITICAL**: The tool defaults to IST (`Asia/Kolkata`). You MUST explicitly inform the user that the meeting was scheduled using IST as the timezone context.
- Gently ask the user if they would like to adjust the timezone or if IST is correct.
- Present the returning checklist directly to the user so they have easy access to the links.

## Example: Scheduling a Sync

**User:** "Schedule a 30-minute sync with John (john@example.com) for tomorrow at 10 AM."

1. Extract details: Summary: "Sync", Attendees: ["john@example.com"], Start Date/Time: Tomorrow 10:00:00, End Time: Tomorrow 10:30:00.
2. Call `create_google_meet(summary="Sync", start_time="...", end_time="...", attendees=["john@example.com"])`.
3. Report success to the user:
   "✅ Google Meet Event Scheduled Successfully! ... I have scheduled this in IST (Asia/Kolkata) based on defaults. Would you like me to adjust the timezone for this meeting?"
