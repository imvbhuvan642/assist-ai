---
name: leave-management
description: "Manage employee leave — check balances, apply for leave, view team leave calendar, and handle conflicts. Use when the user asks about leave balance, wants to apply for time off, or needs to check team availability. Requires HRIS integration."
---

# Leave Management

Handle all leave-related workflows using HRIS tools.

## When to Use

- User asks "how many leaves do I have?" or "check my leave balance"
- User wants to apply for leave / time off
- User asks about team leave calendar or availability
- User needs to check for leave conflicts before scheduling

## Workflow

### Check Leave Balance

1. Identify the employee ID (ask if not known, check user profile)
2. Call `get_leave_balance(employee_id)`
3. Present the balance breakdown clearly:
   - Casual leave remaining
   - Sick leave remaining
   - Earned/privilege leave remaining
   - Comp-off available
   - Total available days

### Apply for Leave

1. Gather required information:
   - **Leave type**: casual, sick, earned, comp_off
   - **Start date**: YYYY-MM-DD
   - **End date**: YYYY-MM-DD
   - **Reason**: Brief explanation
2. Check the balance first — warn if insufficient
3. Call `apply_leave(employee_id, leave_type, start_date, end_date, reason)`
4. This requires approval (interrupt_on) — clearly state the leave details before confirmation
5. Confirm submission status

### View Team Leaves

1. Identify the manager's employee ID
2. Identify the month (default to current month if not specified)
3. Call `list_team_leaves(manager_id, month)`
4. Present as a calendar-style view or table

### Check for Conflicts

Before applying leave, proactively:
1. Check the team leave calendar for overlapping dates
2. Check the user's Google Calendar for meetings on those dates
3. Warn about any conflicts: "You have a 1:1 with Arjun on April 18 — should I reschedule it?"

## Notes

- Always verify the employee ID before making HRIS calls
- Leave applications require approval — never skip the confirmation step
- If the HRIS provider returns an error, explain it clearly and suggest next steps
- For the mock provider, use sample employee IDs: EMP001, EMP002, EMP003, EMP004, EMP010
