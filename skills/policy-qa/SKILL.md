---
name: policy-qa
description: "Answer questions about company policies, handbooks, and standard operating procedures using semantic search over company documents. Use when the user asks about leave policies, code of conduct, expense rules, or any internal company guidelines. Requires RAG to be enabled."
---

# Policy Q&A

Answer employee questions about company policies using RAG-powered document search.

## When to Use

- User asks about leave policy, work-from-home policy, expense policy, etc.
- User asks "what's the rule on..." or "what does the handbook say about..."
- User needs to know compliance requirements or procedures
- User asks about benefits, holidays, or company guidelines

## When NOT to Use

- User asks about leave balance (use leave-management skill)
- User wants general knowledge not in company docs (use web-search)

## Workflow

### Step 1: Understand the Question

Parse the user's question to identify:
- The policy domain (leave, expenses, conduct, WFH, etc.)
- The specific aspect they're asking about
- Whether they need the exact policy text or a summary

### Step 2: Search Documents

1. Call `search_company_docs(query)` with a well-formed search query
2. If the first search doesn't yield clear results, try:
   - A broader query (e.g., "leave policy" instead of "sick leave encashment")
   - A more specific query (e.g., "maternity leave duration" instead of "leave policy")
3. Review the returned excerpts for relevance

### Step 3: Synthesize Answer

1. Provide a clear, direct answer to the question
2. **Always cite the source**: "According to [document name], section X..."
3. If the policy has specific numbers (days, amounts, percentages), quote them exactly
4. If multiple documents address the topic, reconcile them (newer policies supersede older ones)

### Step 4: Handle Edge Cases

**Policy not found**:
> I searched the company documents but couldn't find a specific policy on {topic}. This might be covered in a document that hasn't been added to the system yet. I'd suggest checking with HR directly or asking if the policy document can be added to data/policies/.

**Ambiguous/conflicting policies**:
> I found two documents that address this differently:
> - [Doc A] says: ...
> - [Doc B] says: ...
> The more recent document likely takes precedence, but I'd recommend confirming with HR.

**Question outside policy scope**:
> This isn't covered by company policy documents. Would you like me to search the web for general guidelines on {topic}?

## Output Format

```
**Q: {User's question}**

{Direct answer — 1-3 sentences}

**Source**: {document name}, {section/page if available}

**Relevant excerpt**:
> {Quoted text from the document}

**Additional context**: {Any caveats, exceptions, or related policies}
```

## Notes

- Never fabricate policy details — only state what's in the documents
- If the RAG system returns no results, say so explicitly rather than guessing
- Policies may be outdated — add a caveat if the document date is old
- For sensitive topics (termination, harassment, legal), always recommend the user also consult HR directly
- Documents must be placed in `data/policies/` to be searchable (supports .txt, .md, .pdf, .docx)
