import streamlit as st
from typing import List, Union
import requests
from enum import Enum

# Define the base URL for your FastAPI backend
API_BASE_URL = "http://localhost:8000"  # Adjust this to match your FastAPI server


class AgentMode(Enum):
    AUTO_AGENT = "Auto Agent"
    WEB_SEARCH = "Web Search"
    DB_QUERY = "DB Query"
    QA_MODE = "QA Mode"
    FUTURE_ANALYSIS = "Future works/analysis"


def format_arxiv_results(results: List[dict]) -> str:
    """
    Format arxiv results into a nice markdown list with expandable details
    """
    formatted_output = []

    for idx, paper in enumerate(results, 1):
        # Create the main list item with title and summary
        title = paper.get("title", "Untitled")
        authors = ", ".join(
            [author.get("name", "") for author in paper.get("authors", [])]
        )
        summary = paper.get("summary", "").replace("\n", " ")

        # Create details section
        details = f"""
- **Authors:** {authors}
- **Published:** {paper.get('published', 'N/A')}
- **Categories:** {', '.join(paper.get('categories', []))}
- **Paper URL:** [{paper.get('entry_id', 'N/A')}]({paper.get('entry_id', '#')})
- **PDF URL:** [{paper.get('pdf_url', 'N/A')}]({paper.get('pdf_url', '#')})

**Abstract:**
{summary}
"""
        # Combine the main list item with the details
        formatted_item = f"{idx}. **{title}**\n{details}\n"
        formatted_output.append(formatted_item)

    return "\n".join(formatted_output)


def make_agent_api_call(mode: AgentMode, prompt: str) -> Union[List[dict], str]:
    """
    Make API calls to different endpoints based on the selected mode
    """
    # Define endpoints for each mode
    endpoints = {
        AgentMode.AUTO_AGENT: "/api/auto-agent",
        AgentMode.WEB_SEARCH: "/api/web-search",
        AgentMode.DB_QUERY: "/api/db-query",
        AgentMode.QA_MODE: "/api/qa",
        AgentMode.FUTURE_ANALYSIS: "/api/future-analysis",
    }

    endpoint = endpoints[mode]

    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json={"prompt": prompt, "max_results": 5},
            headers={"Content-Type": "application/json"},
            timeout=30,  # Timeout after 30 seconds
        )
        response.raise_for_status()
        # print("hello from response in st", response.json())
        json_response = response.json()

        # switch on mode
        if mode == AgentMode.WEB_SEARCH:
            return format_arxiv_results(json_response)
        else:
            return json_response

    except requests.exceptions.RequestException as e:
        st.session_state.api_error = f"API Error: {str(e)}"
        return f"Error processing request. Please try again later. ({str(e)})"
