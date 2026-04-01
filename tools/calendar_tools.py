"""Google Calendar Tool — create, search, update, delete, and move calendar events."""

import os
import logging

logger = logging.getLogger(__name__)


def get_calendar_tools() -> list:
    """Initialize and return the Google Calendar API tools from langchain-google-community."""
    try:
        from langchain_google_community.calendar.toolkit import CalendarToolkit
        from langchain_google_community._utils import get_google_credentials
    except ImportError:
        logger.warning(
            "langchain-google-community[calendar] not found. "
            "Please install it to use Calendar tools."
        )
        return []

    token_file = os.environ.get("GOOGLE_TOKEN", "token.json")
    credentials_file = os.environ.get("GOOGLE_CREDENTIALS", "credentials.json")

    # If the credentials file doesn't exist and there's no cached token, we can't proceed
    if not os.path.exists(credentials_file) and not os.path.exists(token_file):
        raise FileNotFoundError(
            f"Google Calendar credentials not found at {credentials_file}. "
            "Please download your credentials.json from Google Cloud Console "
            "and place it in the project root."
        )

    try:
        # Build credentials with calendar scope — reuses the same OAuth flow as Gmail.
        # On first run, this will open a browser window for consent.
        credentials = get_google_credentials(
            token_file=token_file,
            scopes=[
                "https://mail.google.com/",
                "https://www.googleapis.com/auth/calendar",
            ],
            client_secrets_file=credentials_file,
        )

        # Build the calendar API service and toolkit
        from langchain_google_community.calendar.utils import build_calendar_service

        api_resource = build_calendar_service(credentials=credentials)
        toolkit = CalendarToolkit(api_resource=api_resource)
        calendar_tools_list = toolkit.get_tools()

        import uuid
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

        calendar_tools_list.append(create_google_meet)
        return calendar_tools_list
    except Exception as exc:
        logger.warning("Failed to initialize Calendar tools: %s", exc)
        return []
