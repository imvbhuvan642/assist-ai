---
name: preferences
description: "Manage user preferences, skill toggles, approval gates, and profile settings. Use when the user wants to customize their experience: enable/disable skills, change persona, update profile, or modify approval gates."
---

# Preferences Management

Conversational interface for users to customize their Assist AI experience.

## When to Use

- User asks to enable or disable a skill
- User wants to change their persona / role
- User asks to see their current configuration
- User wants to add or remove an approval gate
- User asks to update their profile (name, timezone, communication style)
- User says "show my config" or "what skills do I have?"

## Workflow

### Show Current Configuration

1. Call `get_user_profile()` to get profile settings.
2. Call `list_enabled_skills()` to get skill status.
3. Present a clean summary combining both.

### Enable / Disable Skills

1. If the user names a specific skill, call `enable_skill(skill_name)` or `disable_skill(skill_name)`.
2. If the user is unsure what's available, call `list_available_skills()` first to show all options with descriptions.
3. Confirm the change back to the user.

### Change Persona

1. Call `update_user_profile("persona", new_persona)`.
2. Inform the user that the persona change will take full effect on the next session (the system prompt overlay loads at startup).
3. Valid personas: `developer`, `hr`, `manager`, `product_manager`.

### Update Profile Fields

1. Call `update_user_profile(key, value)` for the requested field.
2. Valid fields: `name`, `persona`, `timezone`, `communication_style`, `output_format`.
3. Confirm the change.

### Modify Approval Gates

1. Call `update_approval_gate(tool_name, true)` to add a gate.
2. Call `update_approval_gate(tool_name, false)` to remove a gate.
3. Explain what the gate does: the agent will pause and ask for confirmation before executing that tool.

## Notes

- Profile changes to `name`, `timezone`, `communication_style`, and `output_format` take effect immediately via dynamic prompt injection.
- Persona changes affect the system prompt overlay, which loads at startup — tell the user to restart for full effect.
- Skill toggling takes effect on the next message (skills are filtered dynamically).
- Never disable the `preferences` or `onboarding` skills — they are always available.
