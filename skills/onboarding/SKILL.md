---
name: onboarding
description: "First-run setup for new users, resumed after the CLI form collects name/designation/persona/timezone. Use when a new user starts for the first time, or when a user explicitly asks to re-run onboarding."
---

# User Onboarding

For brand-new users, the CLI has already collected **name, designation, persona, and timezone** via an interactive form and written them to `profile.yaml` before you were invoked. Do **not** ask for those again.

Your job is to pick up from the agent-name step and walk the user through the remaining setup.

## When to Use

- A new user starts and their basic profile fields are populated but `agent_name` is empty.
- A user explicitly asks to "set up my profile" or "re-run onboarding" — in that case, start from Step 1 and ask for every field.

## Workflow (new user, resuming from form)

### Step 1: Agent Name

Ask the user what they'd like to call you:

> What would you like to call me? I'll go by whatever name you pick.

Save the chosen name:

```
update_user_profile("agent_name", <chosen_name>)
```

From this point forward, refer to yourself by that name in responses.

### Step 2: Communication Preferences

Ask:

> How do you prefer I communicate?
> - **Direct** — brief, no filler, just the answer
> - **Balanced** — concise but with enough context
> - **Detailed** — thorough explanations with examples

Call `update_user_profile("communication_style", choice)`.

### Step 3: Skill Overview

**IMPORTANT**: Call `list_enabled_skills()` first to show the skills already enabled for the user's persona. Then call `list_available_skills()` for the full catalog.

Present the results clearly:

> Based on your **{persona}** role, I've enabled these skills for you:
> {list from list_enabled_skills}
>
> There are also other skills available that you could add:
> {list skills from list_available_skills that are currently disabled}
>
> Would you like to **add** any, **remove** any of your current ones, or **keep the current set**?

If the user wants changes, use `set_enabled_skills(skill_names)` with the full updated list (single batch call — do NOT call enable_skill/disable_skill repeatedly).

### Step 4: Google Services (Gmail, Calendar, Meet)

> Would you like to connect your Google account now? This enables:
> - **Gmail** — search, read, draft, and send emails
> - **Calendar** — create and manage calendar events
> - **Meet** — schedule video meetings with Meet links
>
> Reply **yes** to authorize now (a browser window will open), or **later** to skip.

If yes: call `connect_google_services()`. Tell the user they'll need to **restart the session** for the Google tools to activate.
If later/no: skip quietly. Do not remind them later.

### Step 5: Approval Gates

> By default, I'll ask for your approval before:
> - Sending emails
> - Deleting calendar events
> - Moving calendar events
>
> Want to add or remove any approval gates?

Handle changes via `update_approval_gate(tool_name, enabled)`.

### Step 6: Confirmation

Call `get_user_profile()` and `list_enabled_skills()`, then summarize:

> You're all set! Here's your configuration:
> [profile summary]
>
> You can change any of these anytime by saying "show my config" or "update my preferences".

## Workflow (re-onboarding / manual trigger)

If the user explicitly asks to re-run onboarding, ask every field in order: name → designation → persona → timezone → agent_name → communication_style → skills → Google → approval gates. Use the corresponding `update_user_profile(...)` calls.

## Notes

- Keep the flow conversational — don't dump all questions at once.
- If the user seems impatient, offer sensible defaults and skip ahead.
- The onboarding skill should only auto-run once per user. After the profile is created, subsequent sessions use the preferences skill instead.
- Give the final summary directly at Step 6 — do not ask permission to show it.
- The flow is linear; do not jump between steps.
