"""Gmail Tool — read, search, draft, and send emails using the Gmail API."""

import os
import logging

logger = logging.getLogger(__name__)

def get_gmail_tools() -> list:
    """Initialize and return the Gmail API tools from langchain-google-community."""
    try:
        from langchain_google_community.gmail.toolkit import GmailToolkit
        from langchain_google_community.gmail.utils import build_resource_service, get_gmail_credentials
    except ImportError:
        logger.warning(
            "langchain-google-community[gmail] not found. "
            "Please install it to use Gmail tools."
        )
        return []

    credentials_file = os.environ.get("GMAIL_CREDENTIALS", "credentials.json")
    token_file = os.environ.get("GMAIL_TOKEN", "token.json")

    # If the credentials file doesn't exist, we can't initialize the Gmail toolkit
    if not os.path.exists(credentials_file) and not os.path.exists(token_file):
        logger.warning(
            "Gmail credentials not found at %s. "
            "Please download your credentials.json from Google Cloud Console "
            "and place it in the project root.",
            credentials_file
        )
        return []

    try:
        # This will trigger the OAuth flow if token_file doesn't exist or is invalid
        # But we need credentials.json to be there if token isn't there yet.
        credentials = get_gmail_credentials(
            token_file=token_file,
            scopes=["https://mail.google.com/"],
            client_secrets_file=credentials_file,
        )
        api_resource = build_resource_service(credentials=credentials)
        toolkit = GmailToolkit(api_resource=api_resource)
        return toolkit.get_tools()
    except Exception as exc:
        logger.warning("Failed to initialize Gmail tools: %s", exc)
        return []
