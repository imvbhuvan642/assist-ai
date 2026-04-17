"""Meeting Management Tool — Create and manage virtual meetings (Google Meet, etc.)."""

import os
import uuid
import logging

logger = logging.getLogger(__name__)

def get_meeting_tools(user_id: str | None = None) -> list:
    """Initialize and return meeting management tools (Google Meet via Calendar API).

    Uses the user's per-user Google token when ``user_id`` is set.  Returns
    an empty list if the user hasn't connected Google services yet.
    """
    try:
        from langchain_google_community._utils import get_google_credentials
        from langchain_google_community.calendar.utils import build_calendar_service
    except ImportError:
        logger.warning(
            "langchain-google-community not found. "
            "Please install it to use meeting tools."
        )
        return []

    from tools.google_auth import get_user_token_path, get_shared_credentials_file

    token_file = str(get_user_token_path(user_id))
    credentials_file = str(get_shared_credentials_file())

    if not os.path.exists(token_file):
        logger.info(
            "Meeting tools: no token at %s — user must run connect_google_services first.",
            token_file,
        )
        return []
    if not os.path.exists(credentials_file):
        logger.warning(f"Google credentials not found for meeting tools at {credentials_file}.")
        return []

    try:
        credentials = get_google_credentials(
            token_file=token_file,
            scopes=[
                "https://mail.google.com/",
                "https://www.googleapis.com/auth/calendar",
            ],
            client_secrets_file=credentials_file,
        )
        api_resource = build_calendar_service(credentials=credentials)
        
        from langchain_core.tools import tool
        
        @tool
        def create_google_meet(
            summary: str,
            start_time: str,
            end_time: str,
            description: str = "Scheduled via Assist AI.",
            attendees: list[str] = None,
            timezone: str = "Asia/Kolkata"
        ) -> str:
            """Create a new Google Calendar event with a Google Meet video conference link attached.
            start_time and end_time must be ISO format strings WITHOUT timezone offsets (e.g. '2023-10-25T10:00:00'). 
            attendees is an optional list of email addresses.
            timezone defaults to 'Asia/Kolkata' (IST).
            
            IMPORTANT: After scheduling the meeting, in your response to the user, you MUST tell them:
            1. The meeting was scheduled in IST (Asia/Kolkata).
            2. Ask them if they need it adjusted to a different timezone.
            """
            if not summary:
                summary = "Google Meet Meeting"
            if not description:
                description = "Scheduled via Assist AI."
                
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': timezone,
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': uuid.uuid4().hex,
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            }
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            try:
                created_event = api_resource.events().insert(
                    calendarId='primary',
                    sendUpdates='all',
                    conferenceDataVersion=1,
                    body=event
                ).execute()
                
                meet_link = created_event.get('hangoutLink', 'No link generated')
                event_id = created_event.get('id')
                html_link = created_event.get('htmlLink', '')
                
                return (
                    f"✅ **Google Meet Event Scheduled Successfully!**\n\n"
                    f"- **Title**: {summary}\n"
                    f"- **Meet Link**: {meet_link}\n"
                    f"- **Calendar Link**: {html_link}\n"
                    f"- **Timezone**: {timezone}\n\n"
                    f"*(Agent Note: Please inform the user that it was scheduled in IST and ask if they'd like to change the timezone)*"
                )
            except Exception as e:
                return f"Failed to create Google Meet event: {e}"

        return [create_google_meet]

    except Exception as exc:
        logger.warning("Failed to initialize Meeting tools: %s", exc)
        return []
