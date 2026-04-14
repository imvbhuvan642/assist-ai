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

Call `list_available_skills()` to show what's available.

Explain:
> These are all enabled by default. You can disable any skill you don't need by saying "disable [skill-name]". You can always re-enable them later.

If the user wants to disable some, call `disable_skill(name)` for each.

### Step 5: Approval Gates

Explain the current defaults:
> By default, I'll ask for your approval before:
> - Sending emails
> - Deleting calendar events
> - Moving calendar events
>
> Want to add or remove any approval gates?

Handle any changes via `update_approval_gate(tool_name, enabled)`.

### Step 6: Confirmation

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
