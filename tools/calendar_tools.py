"""Google Calendar Tool — create, search, update, delete, and move calendar events."""

import os
import logging

logger = logging.getLogger(__name__)


def get_calendar_tools(user_id: str | None = None) -> list:
    """Initialize and return the Google Calendar API tools from langchain-google-community.

    When ``user_id`` is provided, uses the user's per-user token.  Returns an
    empty list if the user hasn't connected Google services yet.
    """
    try:
        from langchain_google_community.calendar.toolkit import CalendarToolkit
        from langchain_google_community._utils import get_google_credentials
    except ImportError:
        logger.warning(
            "langchain-google-community[calendar] not found. "
            "Please install it to use Calendar tools."
        )
        return []

    from tools.google_auth import get_user_token_path, get_shared_credentials_file

    token_file = str(get_user_token_path(user_id))
    credentials_file = str(get_shared_credentials_file())

    if not os.path.exists(token_file):
        logger.info(
            "Calendar tools: no token at %s — user must run connect_google_services first.",
            token_file,
        )
        return []
    if not os.path.exists(credentials_file):
        logger.warning(
            "Calendar credentials file not found at %s.", credentials_file
        )
        return []

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
