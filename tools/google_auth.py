"""Google OAuth management — per-user connect/disconnect/status tools.

Each user gets their own token at ``workspace/users/<id>/creds/google-token.json``.
The shared OAuth app credentials (``creds/credentials.json``) are used for all users.

Tools:
  - connect_google_services   → opens browser, authorizes, saves token
  - disconnect_google_services → deletes the user's token
  - google_auth_status         → reports whether the user is connected

After a user connects, they should restart the session so Gmail/Calendar/Meeting
tools can load with the new token.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import yaml
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_USERS_DIR = _PROJECT_ROOT / "workspace" / "users"
_DEFAULT_CREDS_FILE = _PROJECT_ROOT / "creds" / "credentials.json"

# Combined scopes — Gmail + Calendar. One token covers all Google services.
_GOOGLE_SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar",
]

# Module-level active user ID — set by the agent factory at startup.
_active_user_id: str | None = None


def set_active_user(user_id: str | None) -> None:
    """Set the active user so google_auth tools write to the right directory."""
    global _active_user_id
    _active_user_id = user_id


def get_user_token_path(user_id: str | None = None) -> Path:
    """Return the Google token path for a user (user-scoped or global fallback)."""
    uid = user_id or _active_user_id
    if uid:
        creds_dir = _USERS_DIR / uid / "creds"
        creds_dir.mkdir(parents=True, exist_ok=True)
        return creds_dir / "google-token.json"
    # Global fallback — matches the legacy token location
    return _PROJECT_ROOT / "creds" / "token.json"


def get_shared_credentials_file() -> Path:
    """Return the path to the shared OAuth client credentials file."""
    env_override = os.environ.get("GOOGLE_CREDENTIALS")
    if env_override and Path(env_override).exists():
        return Path(env_override)
    return _DEFAULT_CREDS_FILE


def _update_integrations_yaml(user_id: str, service: str, connected: bool) -> None:
    """Record connection status in the user's integrations.yaml."""
    path = _USERS_DIR / user_id / "integrations.yaml"
    if not path.exists():
        return
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            data = {}
        if connected:
            data[service] = {"connected_at": datetime.now().isoformat(timespec="seconds")}
        else:
            data.pop(service, None)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    except Exception as exc:
        logger.warning("Failed to update integrations.yaml: %s", exc)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def connect_google_services() -> str:
    """Start the Google OAuth flow to connect Gmail, Calendar, and Meet for the current user.

    Opens a browser window for the user to authorize. On success, saves the
    token to the user's private creds directory. The user must restart the
    session for Gmail/Calendar/Meeting tools to activate with the new token.

    Use this when:
      - A user asks to connect their Google services
      - A Gmail/Calendar tool failed because no token is available
      - During onboarding if the user opts in to Google integration
    """
    creds_file = get_shared_credentials_file()
    if not creds_file.exists():
        return (
            f"Cannot start OAuth flow — shared credentials file not found at {creds_file}. "
            "The admin needs to place credentials.json in the creds/ directory."
        )

    token_path = get_user_token_path()
    if _active_user_id is None:
        logger.warning("connect_google_services called without an active user — using global token path")

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError:
        return (
            "Google auth libraries not installed. "
            "Run: pip install google-auth google-auth-oauthlib"
        )

    # If a token exists and is valid / refreshable, don't re-prompt
    creds = None
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), _GOOGLE_SCOPES)
            if creds and creds.valid:
                return f"Google services are already connected for this user.\nToken: {token_path}"
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                token_path.write_text(creds.to_json(), encoding="utf-8")
                if _active_user_id:
                    _update_integrations_yaml(_active_user_id, "google", True)
                return (
                    f"Google token refreshed successfully.\n"
                    f"Saved to: {token_path}\n"
                    "Restart the session for tools to pick up the refreshed token."
                )
        except Exception as exc:
            logger.info("Existing token at %s is invalid, re-authorizing: %s", token_path, exc)

    # Run full OAuth flow
    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), _GOOGLE_SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
        token_path.write_text(creds.to_json(), encoding="utf-8")
        if _active_user_id:
            _update_integrations_yaml(_active_user_id, "google", True)
        return (
            f"Google services connected successfully.\n"
            f"Token saved to: {token_path}\n"
            "**Please restart the session** so Gmail, Calendar, and Meeting tools load with your token."
        )
    except Exception as exc:
        logger.exception("Google OAuth flow failed")
        return f"OAuth flow failed: {exc}"


@tool
def disconnect_google_services() -> str:
    """Remove the current user's Google OAuth token, disconnecting Gmail/Calendar/Meet.

    Deletes the user's stored token. Their Google services will stop working
    until they reconnect. The user must restart the session after disconnecting.
    """
    token_path = get_user_token_path()
    if not token_path.exists():
        return "No Google token found — you're already disconnected."
    try:
        token_path.unlink()
        if _active_user_id:
            _update_integrations_yaml(_active_user_id, "google", False)
        return (
            f"Google services disconnected. Token removed from {token_path}.\n"
            "Restart the session for the change to take effect."
        )
    except Exception as exc:
        return f"Failed to remove token: {exc}"


@tool
def google_auth_status() -> str:
    """Report whether the current user is connected to Google services.

    Returns whether a valid token exists, its expiration status, and the
    token file location.
    """
    token_path = get_user_token_path()
    if not token_path.exists():
        return (
            "Google services are NOT connected for this user.\n"
            "Call `connect_google_services` to authorize and enable Gmail, Calendar, and Meet."
        )
    try:
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(str(token_path), _GOOGLE_SCOPES)
        if creds.valid:
            return f"Connected. Token is valid. Path: {token_path}"
        if creds.expired and creds.refresh_token:
            return (
                f"Connected, but access token expired. It will auto-refresh on next use. "
                f"Path: {token_path}"
            )
        return (
            f"Connected, but token appears invalid/revoked. "
            f"Call `connect_google_services` to re-authorize. Path: {token_path}"
        )
    except Exception as exc:
        return f"Token file exists but couldn't be parsed ({exc}). Run `connect_google_services` to re-authorize."


def get_google_auth_tools() -> list:
    """Return the Google auth management tools."""
    return [connect_google_services, disconnect_google_services, google_auth_status]
