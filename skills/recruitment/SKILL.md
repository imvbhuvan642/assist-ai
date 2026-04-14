---
name: recruitment
description: "Manage the recruitment pipeline — search candidate communications, schedule interviews, track pipeline stages, and draft outreach emails. Use when the user is hiring, scheduling interviews, or managing candidates."
---

# Recruitment Pipeline

Support the hiring process from candidate sourcing through offer stage.

## When to Use

- User asks to schedule an interview
- User wants to search for candidate-related emails
- User needs to draft an outreach or rejection email
- User wants to track the hiring pipeline
- User asks to prepare interview questions

## Workflow

### Search Candidate Communications

1. Use `search_gmail` with queries like:
   - `from:{candidate_email}` for specific candidates
   - `subject:application {role}` for role-specific applications
   - `label:recruitment` if the user has a recruitment label
2. Summarize relevant threads: who applied, when, current status

### Schedule Interviews

1. Gather details:
   - **Candidate name** and email
   - **Interview type**: phone screen, technical, culture fit, hiring manager
   - **Interviewers**: Who should be in the meeting
   - **Duration**: 30 min (phone), 60 min (technical), 45 min (culture)
   - **Preferred dates/times**
2. Check interviewer availability via Calendar
3. Create the calendar event with:
   - Google Meet link (for remote interviews)
   - Interview type in the title
   - Candidate details in the description
4. Send calendar invite (automatic, no approval needed)

### Draft Candidate Emails

**Outreach/sourcing email**:
- Professional but warm tone
- Highlight the role and company
- Clear call-to-action (apply / schedule a call)

**Interview invitation**:
- Include: date, time, format (video/in-person), interviewers
- Preparation tips if applicable
- Link to Google Meet or office address

**Rejection email**:
- Empathetic, respectful tone
- Thank them for their time
- Brief, non-specific reason
- Encouragement to apply for future roles

**Offer communication**:
- Enthusiastic tone
- Key details: role, start date, compensation summary
- Next steps (formal offer letter to follow)

All emails require approval before sending.

### Track Pipeline

Maintain a pipeline overview:

```markdown
## Hiring Pipeline: {Role}

| Candidate | Stage | Last Activity | Next Step |
|-----------|-------|---------------|-----------|
| {Name}    | Technical Interview | Apr 10 | Schedule culture fit |
| {Name}    | Phone Screen | Apr 8 | Awaiting feedback |
| {Name}    | Applied | Apr 12 | Schedule phone screen |
| {Name}    | Offer | Apr 5 | Awaiting acceptance |
```

### Prepare Interview Questions

Generate role-specific interview questions based on:
- The job description (if provided)
- The interview type (technical, behavioral, culture)
- Common best practices for the role

Structure as:
- 3-5 core competency questions
- 2-3 behavioral/situational questions
- 1-2 role-specific technical questions
- Evaluation criteria for each question

## Notes

- Candidate data is sensitive — don't share one candidate's information when discussing another
- All email communications with candidates require approval
- When scheduling, respect timezone differences for remote candidates
- If an ATS (Applicant Tracking System) is integrated via MCP, prefer using it over manual email tracking
