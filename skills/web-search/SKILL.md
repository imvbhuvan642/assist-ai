---
name: web-search
description: For searching the internet to find up-to-date information, news, financial data, or factual answers
---

# Web Search Skill

## When to Use This Skill

Use this skill when you need to answer a question that requires external information from the internet, such as:
- Current events and recent news
- Real-time financial or stock data
- Factual information not present in the local database or context
- General knowledge or research

## Workflow

### 1. Formulate the Query
Translate the user's question into a concise and effective search engine query.
- Use keywords instead of full sentences when appropriate.
- Be specific about what you are looking for.

### 2. Execute Web Search
Use the `internet_search` tool to run the web search.
- **`query`**: The formulated search string.
- **`max_results`**: Usually keep the default of 5, but increase if more comprehensive results are needed.
- **`topic`**: Choose "general" for most queries, "news" for recent events, or "finance" for financial information.
- **`include_raw_content`**: Keep as False unless you specifically need the raw HTML content of the pages.

### 3. Analyze Results
Review the returned search results (URLs, titles, snippets).
- Check if the snippets contain the answer to the user's question.
- If the results are insufficient, refine your query and search again.

### 4. Provide the Answer
Synthesize the information from the search results to answer the user's question.
- Cite the sources (URLs) where appropriate to provide context and reliability.

## Example: General Information Search
**User:** "What is the capital of France?"
**Query:** "capital of France"
**Tool Call:** `internet_search(query="capital of France", topic="general")`
**Response:** Summarize the result (Paris).

## Example: News Search
**User:** "What are the latest updates on the Mars rover?"
**Query:** "latest updates Mars rover NASA"
**Tool Call:** `internet_search(query="latest updates Mars rover NASA", topic="news")`
**Response:** Provide a summary of the latest news based on the search snippets.

## Example: Finance Search
**User:** "What is Apple's latest stock price?"
**Query:** "Apple AAPL stock price today"
**Tool Call:** `internet_search(query="Apple AAPL stock price today", topic="finance")`
**Response:** Provide the financial data from the search results.

## Quality Guidelines
- Always ensure the search query matches the intent of the user's request.
- Select the appropriate `topic` parameter for better, more context-aware results.
- Synthesize the information comprehensively rather than just pasting raw snippets.
- Only perform a web search if the information cannot be found locally or if you need the most up-to-date data.
