import os
import json
from typing import List, Dict, Any
from langchain.tools import tool


# Mock Brave Search class to replace the real one
class MockBraveSearch:
    """Mock implementation of BraveSearch to avoid API key requirements"""

    def __init__(self, api_key: str = None, search_kwargs: Dict = None):
        self.api_key = api_key or "mock_key"
        self.search_kwargs = search_kwargs or {}

    @classmethod
    def from_api_key(cls, api_key: str, search_kwargs: Dict = None):
        return cls(api_key, search_kwargs)

    def run(self, query: str) -> str:
        """Returns mock search results in the expected format"""
        mock_results = [
            {
                "title": f"Mock Result 1 for: {query}",
                "link": "https://example.com/result1",
                "snippet": f"This is a mock search result for the query '{query}'. This tool is currently running in demo mode without real search capabilities.",
            },
            {
                "title": f"Mock Result 2 for: {query}",
                "link": "https://example.com/result2",
                "snippet": f"Another mock result related to '{query}'. To enable real search, configure the BRAVE_API_KEY environment variable.",
            },
            {
                "title": f"Mock Result 3 for: {query}",
                "link": "https://example.com/result3",
                "snippet": f"Third mock search result for '{query}'. This demonstrates the expected output format.",
            },
        ]
        return json.dumps(mock_results)


def remove_html(text: str) -> str:
    """Remove HTML tags from text"""
    import re

    if not text:
        return ""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


# Check if we have a real API key, otherwise use mock
if os.getenv("BRAVE_API_KEY"):
    try:
        from langchain_community.tools import BraveSearch

        brave_tool = BraveSearch.from_api_key(
            api_key=os.getenv("BRAVE_API_KEY"), search_kwargs={"count": 10}
        )
        print("✅ Using real Brave Search API")
    except ImportError:
        print("⚠️ BraveSearch not available, using mock implementation")
        brave_tool = MockBraveSearch.from_api_key("mock", {"count": 10})
else:
    print("ℹ️ No BRAVE_API_KEY found, using mock search implementation")
    brave_tool = MockBraveSearch.from_api_key("mock", {"count": 10})


@tool("SearchEngine")
def search_engine(query: str) -> str:
    """
    Search-Engine tool for browsing the web and getting urls, titles, and website snippets

    Parameters:
    - query (str): Query that will be sent to the search engine

    Returns:
    - str: The search result from the query containing the "Title", "Link", and "Snippet" for each search result
    """
    try:
        response = json.loads(brave_tool.run(query))
        output = ""

        for entry in response:
            output += f"TITLE: {entry.get('title', 'No title')}\n"
            output += f"LINK: {entry.get('link', 'No link')}\n"
            output += f"SNIPPET: {remove_html(entry.get('snippet', 'No snippet'))}\n"
            output += "\n\n"

        return output[:-4] if output else "No search results found"

    except Exception as e:
        # Fallback in case anything goes wrong
        return f"""TITLE: Search Error - Demo Mode Active
LINK: https://example.com/demo
SNIPPET: Search functionality is running in demo mode. Error: {str(e)}

TITLE: Enable Real Search
LINK: https://brave.com/search/api/
SNIPPET: To enable real search capabilities, sign up for Brave Search API and set the BRAVE_API_KEY environment variable.

TITLE: Current Query: {query}
LINK: https://example.com/query
SNIPPET: Your search query was '{query}' but no real search was performed due to missing API configuration."""


# Alternative implementation if you want to completely disable search
@tool("SearchEngineDisabled")
def search_engine_disabled(query: str) -> str:
    """
    Disabled search engine - returns helpful message instead
    """
    return f"""🔍 Search functionality is currently disabled.

Query attempted: "{query}"

To enable search:
1. Get a Brave Search API key from https://brave.com/search/api/
2. Set environment variable: BRAVE_API_KEY=your_key_here
3. Uncomment the real search implementation

For now, this tool will continue without web search capabilities."""


# You can also create a completely offline version that uses local data
@tool("LocalSearch")
def local_search(query: str) -> str:
    """
    Local search that works with predefined cybersecurity knowledge
    """
    # This is a simple example - you could expand this with a local database
    cybersec_knowledge = {
        "nmap": {
            "title": "Nmap Network Scanner",
            "link": "https://nmap.org/",
            "snippet": "Nmap is a network discovery and security auditing tool. It can discover hosts and services on a network.",
        },
        "sqlmap": {
            "title": "SQLMap SQL Injection Tool",
            "link": "https://sqlmap.org/",
            "snippet": "SQLMap is an automatic SQL injection and database takeover tool written in Python.",
        },
        "metasploit": {
            "title": "Metasploit Framework",
            "link": "https://www.metasploit.com/",
            "snippet": "The Metasploit Framework is a penetration testing platform for finding, exploiting, and validating vulnerabilities.",
        },
    }

    query_lower = query.lower()
    results = []

    for key, data in cybersec_knowledge.items():
        if key in query_lower or any(
            word in data["snippet"].lower() for word in query_lower.split()
        ):
            results.append(data)

    if not results:
        return f"No local knowledge found for query: '{query}'. This is a limited offline search."

    output = ""
    for result in results:
        output += f"TITLE: {result['title']}\n"
        output += f"LINK: {result['link']}\n"
        output += f"SNIPPET: {result['snippet']}\n\n"

    return output.strip()
