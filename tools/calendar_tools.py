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
        return toolkit.get_tools()
    except Exception as exc:
        logger.warning("Failed to initialize Calendar tools: %s", exc)
        return []
