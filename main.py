from fastapi import FastAPI
from contextlib import asynccontextmanager
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


async def startup_event():
    # Query arXiv for a specific topic (e.g., "machine learning")
    query = "electron learning"
    result = await query_arxiv(query, max_results=1)
    print("arXiv Query Result:", result)  # You can process or log the result as needed


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        # Load
        await startup_event()
    except Exception as e:
        print(f"Error during startup: {e}")

    yield

    # Clean up
    pass


# Create a FastAPI instance
app = FastAPI(lifespan=lifespan)


# Route to fetch arXiv results dynamically
@app.get("/arxiv/{query}")
async def get_arxiv_results(query: str, max_results: int = 5):
    result = await query_arxiv(query, max_results)
    return result
