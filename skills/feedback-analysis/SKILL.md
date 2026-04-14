---
name: feedback-analysis
description: "Analyze user and customer feedback — search Slack, email, and databases for feedback signals, perform sentiment analysis, and cluster themes. Use when the PM wants to understand user sentiment, identify common complaints, or gather insights from feedback."
---

# Feedback Analysis

Synthesize user feedback from multiple channels into actionable product insights.

## When to Use

- PM asks "what are users saying about X?" or "feedback summary"
- User wants sentiment analysis on a feature or product area
- Preparing for a product review with user feedback evidence
- Identifying recurring complaints or feature requests from users

## Workflow

### Step 1: Gather Feedback

Search across available channels:
1. **Gmail** — support emails, customer replies, NPS responses
2. **Slack** (if connected) — #feedback, #support, #product-ideas channels
3. **SQL Database** (if configured) — feedback tables, survey responses, support tickets
4. **Web** — app store reviews, social media mentions (via internet_search)

### Step 2: Categorize & Tag

For each feedback item, identify:
- **Topic**: Which feature/area it relates to
- **Sentiment**: Positive / Neutral / Negative
- **Type**: Bug report, feature request, praise, complaint, question
- **Urgency**: How many users are affected, how severe

### Step 3: Cluster Themes

Group feedback into themes and rank by volume:

```markdown
## Feedback Analysis — {Period}

### Top Themes (by mention count)

| Theme | Mentions | Sentiment | Sample Quote |
|-------|----------|-----------|-------------|
| Onboarding flow | 23 | 🔴 Negative | "Took me 20 min to figure out setup" |
| API speed | 15 | 🟡 Mixed | "Fast usually, but timeouts on large queries" |
| New dashboard | 12 | 🟢 Positive | "Love the new layout, much cleaner" |

### Sentiment Distribution
- 🟢 Positive: 35%
- 🟡 Neutral: 25%
- 🔴 Negative: 40%

### Key Insights
1. Onboarding friction is the top complaint — 23 mentions across email and Slack
2. API reliability concerns are growing — up from 8 mentions last month
3. Dashboard redesign is well-received — net positive sentiment

### Recommended Actions
1. Prioritize onboarding UX improvements (high volume, strong negative sentiment)
2. Investigate API timeout root cause (growing trend)
3. Consider extending dashboard patterns to other pages (positive signal)
```

## Notes

- Be objective — present what users said, not what the PM wants to hear
- Always include direct quotes — they carry more weight than summaries
- Sentiment analysis is approximate — flag edge cases where tone is ambiguous
- For quantitative analysis, prefer database/survey data over anecdotal channel messages
- If the sample size is small (<10 mentions), note the limitation explicitly
