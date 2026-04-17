---
name: onboarding
description: "First-run setup wizard for new users. Use when a new user starts for the first time and has no profile configured, or when a user explicitly asks to re-run onboarding."
---

# User Onboarding

Guide new users through initial setup to configure their Assist AI experience.

## When to Use

- A new user starts and has no profile directory (detected automatically).
- A user explicitly asks to "set up my profile" or "re-run onboarding".

## Workflow

### Step 1: Welcome & Role Selection

Greet the user and ask about their role:

> Welcome to Assist AI! I'm your digital employee assistant. Let me set up your profile so I can work the way you need me to.
>
> What's your role?
> 1. **Developer** — code review, CI/CD, sprint management, documentation
> 2. **HR** — leave management, policy Q&A, onboarding, recruitment
> 3. **Manager** — team dashboards, standups, 1:1 prep, OKR tracking
> 4. **Product Manager** — feature tracking, roadmap, feedback analysis, release notes

Call `update_user_profile("persona", selected_persona)` with their choice.

### Step 2: Basic Profile

Ask for:
- **Name**: "What should I call you?"
- **Timezone**: "What timezone are you in?" (default to Asia/Kolkata if they're unsure)

Call `update_user_profile("name", name)` and `update_user_profile("timezone", timezone)`.

### Step 3: Communication Preferences

Ask:
> How do you prefer I communicate?
> - **Direct** — brief, no filler, just the answer
> - **Balanced** — concise but with enough context
> - **Detailed** — thorough explanations with examples

Call `update_user_profile("communication_style", choice)`.

### Step 4: Skill Overview

**IMPORTANT**: You MUST call `list_enabled_skills()` first to show the skills that are already enabled for the user's persona. Then call `list_available_skills()` to get the full catalog.

Present the results clearly:
> Based on your **{persona}** role, I've enabled these skills for you:
> {list from list_enabled_skills}
>
> There are also other skills available that you could add:
> {list skills from list_available_skills that are currently disabled}
>
> Would you like to **add** any of those, **remove** any of your current ones, or **keep the current set**?

If the user wants to change skills, use `set_enabled_skills(skill_names)` with the full updated list (this is a single batch call — do NOT call enable_skill/disable_skill multiple times).

### Step 5: Google Services (Gmail, Calendar, Meet)

Ask the user if they want to connect their Google account:

> Would you like to connect your Google services now? This enables:
> - **Gmail** — search, read, draft, and send emails
> - **Calendar** — create and manage calendar events
> - **Meet** — schedule video meetings with Meet links
>
> Reply **yes** to authorize now (a browser window will open), or **later** to skip. You can always connect later by saying "connect my Google account".

If the user says yes:
1. Call `connect_google_services()`. This opens a browser for OAuth authorization.
2. The tool saves the token to the user's private creds directory.
3. Tell the user they must **restart the session** for Gmail/Calendar/Meeting tools to activate.

If the user says later/no:
- Skip without any changes. The Google integration tools simply won't be available until they connect.
- Do NOT remind them again later — they'll discover the limitation when they try to use Gmail/Calendar.

### Step 6: Approval Gates

Explain the current defaults:
> By default, I'll ask for your approval before:
> - Sending emails
> - Deleting calendar events
> - Moving calendar events
>
> Want to add or remove any approval gates?

Handle any changes via `update_approval_gate(tool_name, enabled)`.

### Step 7: Confirmation

Summarize the configuration by calling `get_user_profile()` and `list_enabled_skills()`.

> You're all set! Here's your configuration:
> [profile summary]
>
> You can change any of these anytime by saying "show my config" or "update my preferences".

## Notes

- Keep the flow conversational — don't dump all questions at once.
- If the user seems impatient, offer to use sensible defaults and skip ahead.
- The onboarding skill should only run once per user. After the profile is created, subsequent sessions use the preferences skill instead.
- Always create the profile directory before writing any settings (the tools handle this automatically).

Things to Note:
1. Directly give the summary to the User after Step 6, do not ask if they want to see it. The summary is a nice way to end the onboarding flow and make the user feel good about their new setup.
2. The onboarding flow should be linear and not allow the user to jump around between steps.