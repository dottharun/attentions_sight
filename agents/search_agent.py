import arxiv
from typing import List


async def query_arxiv(query: str, max_results: int = 5) -> List[arxiv.Result]:
    """
    Query arXiv for papers using the arxiv package.

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
