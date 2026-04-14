---
name: employee-onboarding
description: "Manage employee onboarding workflows — create checklists, send welcome emails, schedule orientation meetings, and answer new employee questions. Use when onboarding a new hire or setting up their first-week experience."
---

# Employee Onboarding

Orchestrate the full onboarding experience for new employees.

## When to Use

- HR is onboarding a new employee
- User asks to "set up onboarding for [name]"
- User needs an onboarding checklist
- A new employee has questions about getting started

## Workflow

### Step 1: Gather New Employee Details

Collect:
- **Name**: Full name
- **Employee ID**: From HRIS (or to be created)
- **Role / Title**: Job title
- **Department**: Which team they're joining
- **Start date**: First day
- **Manager**: Who they report to
- **Email**: Company email address

### Step 2: Generate Onboarding Checklist

Create a structured checklist based on their role:

```markdown
## Onboarding Checklist: {Name} — {Role}
**Start Date**: {date} | **Manager**: {manager}

### Before Day 1 (HR Tasks)
- [ ] Create employee record in HRIS
- [ ] Set up company email and accounts
- [ ] Prepare workstation / laptop
- [ ] Send welcome email with first-day instructions
- [ ] Schedule orientation meetings

### Day 1
- [ ] Welcome meeting with manager
- [ ] Team introduction
- [ ] IT setup walkthrough (email, Slack, VPN, tools)
- [ ] Office tour / workspace setup
- [ ] Review company handbook and policies

### Week 1
- [ ] 1:1 with manager — expectations and goals
- [ ] Meet key stakeholders
- [ ] Complete mandatory training modules
- [ ] Set up development environment (for engineering roles)
- [ ] Access to relevant Jira/Linear projects and repos

### Month 1
- [ ] 30-day check-in with manager
- [ ] Complete probation goals review
- [ ] Feedback session with HR
```

Customize based on department:
- **Engineering**: Add repo access, dev environment, code review onboarding
- **HR**: Add HRIS training, policy review
- **Product**: Add roadmap walkthrough, stakeholder mapping

### Step 3: Send Welcome Email

Draft and send (via Gmail) a welcome email including:
- Welcome message from the team
- First-day logistics (time, location, what to bring)
- Links to key resources (handbook, Slack channels, calendar)
- Manager contact info
- IT setup instructions

### Step 4: Schedule Orientation Meetings

Using Calendar tools, schedule:
- Welcome meeting with manager (Day 1, 30 min)
- Team introduction (Day 1, 15 min)
- HR orientation (Day 1, 1 hour)
- 1:1 with manager (End of Week 1, 30 min)
- 30-day check-in (Month 1, 30 min)

### Step 5: Answer New Employee Questions

For new employees asking questions:
1. First check company docs via `search_company_docs` (policy-qa pattern)
2. If not in docs, provide general guidance
3. For IT/access issues, suggest contacting the IT helpdesk

## Notes

- Onboarding checklists should be saved to the filesystem for tracking
- Email sending requires approval (interrupt_on)
- Calendar event creation is automatic (no approval needed)
- Customize the checklist heavily based on role and department — a generic checklist is not helpful
