---
name: resource-allocation
description: "Analyze team capacity and recommend resource allocation — pull leave calendars, sprint load, and workload distribution. Use when a manager needs to plan staffing, check capacity, or balance workload."
---

# Resource Allocation

Help managers understand team capacity and optimize workload distribution.

## When to Use

- Manager asks "who has bandwidth?" or "team capacity this sprint"
- Planning for an upcoming project or sprint
- Checking if the team can take on additional work
- Identifying overloaded or underutilized team members

## Workflow

### Step 1: Gather Capacity Data

1. **HRIS leaves** (if connected): Call `list_team_leaves(manager_id, month)` for upcoming time off
2. **Sprint load** (if Jira/Linear connected): Get assigned tickets per person, story points
3. **Calendar density**: Check how much meeting time each person has this week

### Step 2: Calculate Capacity

For each team member:
- **Available days** = working days - leaves - holidays
- **Sprint load** = assigned story points / typical velocity
- **Meeting overhead** = hours in meetings / total hours
- **Capacity score** = High / Medium / Low

### Step 3: Present Allocation View

```markdown
## Team Capacity — {Period}

| Member | Available Days | Sprint Load | Meetings/Week | Capacity |
|--------|---------------|-------------|---------------|----------|
| {Name} | 9/10          | 8/13 pts    | 6 hrs         | 🟢 High  |
| {Name} | 7/10          | 12/13 pts   | 10 hrs        | 🔴 Low   |
| {Name} | 10/10         | 5/13 pts    | 4 hrs         | 🟢 High  |
| {Name} | 5/10 (leave)  | 8/13 pts    | 3 hrs         | 🟡 Med   |

### Recommendations
- **{Name}** has capacity — consider assigning {specific unowned tickets}
- **{Name}** is overloaded — consider moving {ticket} to someone with more bandwidth
- **{Name}** is on leave {dates} — ensure their in-progress work has coverage

### Risks
- Team is at 85% capacity this sprint — limited buffer for emergencies
- {Name}'s leave overlaps with {Name}'s leave — {area} will have no coverage on {dates}
```

## Notes

- Capacity analysis is a planning aid, not a performance metric — present it as such
- If data sources are limited, work with what's available and note assumptions
- Always account for "slack time" — 100% utilization is unsustainable
- For cross-team resource requests, focus on impact and priority, not just availability
