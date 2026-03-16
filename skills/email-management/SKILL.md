---
name: email-management
description: Manage emails using Gmail, including searching, reading, creating drafts, and sending emails.
---

# Email Management Skill

## When to Use This Skill

Use this skill when the user asks you to interact with their email inbox, such as:
- Searching for specific emails or catching up on unread messages.
- Summarizing recent emails or email threads.
- Drafting responses or new emails to specific contacts.
- Sending emails on behalf of the user.

## Available Tools

The `GmailToolkit` provides several tools:
- **`search_gmail`**: Search for emails using standard Gmail search operators (e.g., `is:unread`, `from:boss@example.com`, `subject:"project zero"`).
- **`get_gmail_message`**: Retrieve the full content of a specific email message using its ID.
- **`get_gmail_thread`**: Retrieve the full content of an email thread using its ID.
- **`create_gmail_draft`**: Create an email draft (but do not send it).
- **`send_gmail_message`**: Send an email directly to a recipient.

## Workflow

### 1. Searching for Emails
- Translate the user's request into a precise Gmail search query.
- Use the `search_gmail` tool with the query to find relevant message IDs.
- For example, if looking for new emails, use the query `is:unread`.

### 2. Reading Emails
- After finding message or thread IDs using `search_gmail`, use `get_gmail_message` or `get_gmail_thread` to read the actual content.
- Be mindful of avoiding excessively large threads if not needed; parse them accurately to find the answer.

### 3. Drafting or Sending Emails
- **Drafting**: If the user wants to review the email before it goes out, use `create_gmail_draft` with the appropriate `to`, `subject`, and `message` parameters.
- **Sending**: If the user explicitly asks you to send the email immediately or gives you approval, use `send_gmail_message`.
- Ensure a professional and polite tone unless requested otherwise. Be concise and format the message cleanly.

## Example: Summarizing Unread Emails
**User:** "Do I have any new emails?"
1. Use `search_gmail` with `query="is:unread"`.
2. Extract the IDs from the results.
3. Use `get_gmail_message` iteratively on the top few IDs to read the contents.
4. Provide a neat summary to the user.

## Example: Drafting a Reply
**User:** "Draft a reply to Alice thanking her for the report."
1. Use `search_gmail` with `query="from:alice"`.
2. Find the relevant message/thread ID to get context.
3. Use `create_gmail_draft` pointing to Alice, with an appropriate subject and a drafted reply body.
4. Let the user know the draft implies it is in their Gmail draft folder.

## Quality Guidelines
- Always confirm with the user before actually using `send_gmail_message` unless they explicitly said "send an email to...". When in doubt, lean towards creating a draft.
- Ensure email addresses match the recipient exactly.
