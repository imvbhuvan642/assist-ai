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

    credentials_file = os.environ.get("GOOGLE_CREDENTIALS", "credentials.json")
    token_file = os.environ.get("GOOGLE_TOKEN", "token.json")

    # If the credentials file doesn't exist, we can't initialize the Gmail toolkit
    if not os.path.exists(credentials_file) and not os.path.exists(token_file):
        raise FileNotFoundError(
            f"Gmail credentials not found at {credentials_file}. "
            "Please download your credentials.json from Google Cloud Console "
            "and place it in the project root."
        )

    try:
        # This will trigger the OAuth flow if token_file doesn't exist or is invalid
        # But we need credentials.json to be there if token isn't there yet.
        credentials = get_gmail_credentials(
            token_file=token_file,
            scopes=[
                "https://mail.google.com/",
                "https://www.googleapis.com/auth/calendar",
            ],
            client_sercret_file=credentials_file,  # NOTE: upstream typo in langchain_google_community
        )
        api_resource = build_resource_service(credentials=credentials)
        toolkit = GmailToolkit(api_resource=api_resource)
        base_tools = toolkit.get_tools()

        # Filter out the default draft and send tools so we can replace them with custom ones
        tools_to_keep = [t for t in base_tools if t.name not in ["create_gmail_draft", "send_gmail_message"]]

        import markdown
        import base64
        from email.mime.text import MIMEText
        from langchain_core.tools import tool

        def _build_html_message(message_body: str) -> str:
            """Convert markdown to a styled HTML email body."""
            html_content = markdown.markdown(message_body)
            styled_html = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333333;
                        max-width: 600px;
                    }}
                    blockquote {{
                        border-left: 4px solid #cccccc;
                        padding-left: 15px;
                        margin-left: 0;
                        color: #666666;
                    }}
                    ul, ol {{
                        padding-left: 20px;
                    }}
                    li {{
                        margin-bottom: 8px;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            return styled_html

        @tool
        def create_gmail_draft(message: str, to: str, subject: str) -> str:
            """Create an email draft with proper HTML formatting.
            The message can include Markdown (bullets, bolding, etc.)."""
            try:
                html_body = _build_html_message(message)
                mime_msg = MIMEText(html_body, 'html')
                mime_msg['to'] = to
                mime_msg['subject'] = subject
                
                raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()
                create_draft_body = {'message': {'raw': raw}}
                
                api_resource.users().drafts().create(userId='me', body=create_draft_body).execute()
                return f"Successfully created a formatted Gmail draft for {to}."
            except Exception as e:
                return f"Failed to create Gmail draft: {e}"

        @tool
        def send_gmail_message(message: str, to: str, subject: str) -> str:
            """Send a formatted HTML email immediately.
            The message can include Markdown (bullets, bolding, etc.)."""
            try:
                html_body = _build_html_message(message)
                mime_msg = MIMEText(html_body, 'html')
                mime_msg['to'] = to
                mime_msg['subject'] = subject
                
                raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()
                send_message_body = {'raw': raw}
                
                api_resource.users().messages().send(userId='me', body=send_message_body).execute()
                return f"Successfully sent a formatted email to {to}."
            except Exception as e:
                return f"Failed to send email: {e}"

        tools_to_keep.extend([create_gmail_draft, send_gmail_message])
        return tools_to_keep
    except Exception as exc:
        logger.warning("Failed to initialize Gmail tools: %s", exc)
        return []
