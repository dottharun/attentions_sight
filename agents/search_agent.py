import arxiv
from typing import List
from fastapi import HTTPException
from util.log import logger
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage


async def query_arxiv(query: str, max_results: int = 5) -> List[arxiv.Result]:
    """
    Query arXiv for papers using the arxiv package.
    From - https://github.com/lukasschwab/arxiv.py?tab=readme-ov-file#fetching-results

    Args:
        query (str): Search query string
        max_results (int, optional): Maximum number of results to return. Defaults to 5.

    Returns:
        List[arxiv.Result]: List of arxiv Result objects
    """
    # Initialize the client
    client = arxiv.Client()

    # Create the search object
    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance
    )

    # Get results and convert generator to list
    try:
        return list(client.results(search))
    except Exception as e:
        raise Exception(f"Error querying arXiv: {str(e)}")


# Load environment variables
load_dotenv()


async def llm_make_arxiv_query(prompt: str) -> str:
    """
    Convert user prompt into an optimized arXiv search query using Groq LLM.

    Args:
        prompt (str): User's natural language query

    Returns:
        str: Optimized arXiv search query

    Raises:
        HTTPException: If LLM query generation fails
    """
    try:
        # Initialize Groq LLM
        llm = ChatGroq(
            temperature=0.3,
            model="llama3-8b-8192",
            stop_sequences=[],
        )

        # Create system prompt to guide query generation
        system_prompt = """You are an expert at converting natural language questions into optimized arXiv search queries.
        Focus on extracting key technical terms and concepts.
        Use AND, OR, and quotation marks for precise queries.
        Include relevant field filters (e.g. ti: for title, abs: for abstract) when appropriate.
        Format the response as a single line containing only the search query."""

        # Combine system prompt with user query
        messages = [
            HumanMessage(
                content=f"{system_prompt}\n\nUser question: {prompt}\n\nArXiv query:"
            ),
        ]

        # Get response from LLM
        response = llm.invoke(messages)

        # Extract and clean the query
        query = str(response.content).strip()

        logger.info(f"Generated arXiv query: {query}")

        return query

    except Exception as e:
        logger.error(f"Error in LLM query generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate search query")
