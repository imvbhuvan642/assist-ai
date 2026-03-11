import os
from typing import Literal
from tavily import TavilyClient
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

@tool
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
) -> dict:
    """
    Run a web search using Tavily to find up-to-date information, news, or factual answers.
    
    Args:
        query: The search query to execute. Formulate this clearly to get the best results.
        max_results: The maximum number of search results to return (default: 5).
        topic: The category of search. Use "general" for most queries, "news" for recent events, or "finance" for financial data (default: "general").
        include_raw_content: Set to True to include the raw HTML content of the search results (default: False).
        
    Returns:
        A dictionary containing the search results, including URLs, titles, and snippets.
    """
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
