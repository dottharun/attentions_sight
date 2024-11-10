from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from agents.search_agent import query_arxiv
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def startup_event():
    # Query arXiv for a specific topic (e.g., "machine learning")
    query = "electron learning"
    result = await query_arxiv(query, max_results=2)
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


# Create a FastAPI instance with testing arxiv event
# app = FastAPI(lifespan=lifespan)

# Create a FastAPI instance
app = FastAPI()


# Route to fetch arXiv results dynamically
@app.get("/api/arxiv/{query}")
async def get_arxiv_results(query: str, max_results: int = 5):
    result = await query_arxiv(query, max_results)
    return result


# Request and Response Models
class SearchRequest(BaseModel):
    prompt: str
    max_results: int = 2


async def llm_make_arxiv_query(prompt: str) -> str:
    """
    Convert user prompt into an optimized arXiv search query using LLM.
    Add your LLM integration here.
    """
    try:
        # This is a placeholder - replace with actual LLM call
        # You would typically:
        # 1. Call your LLM with a prompt like:
        # "Convert this user question into a focused arXiv search query: {}"
        # 2. Process the response to extract key search terms

        # For now, we'll just use basic keyword extraction
        keywords = prompt.lower().split()
        cleaned_keywords = [word for word in keywords if len(word) > 3]
        query = " AND ".join(cleaned_keywords[:3])  # Use top 3 keywords

        return query
    except Exception as e:
        logger.error(f"Error in LLM query generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate search query")


@app.post("/api/web-search")
async def web_search(request: SearchRequest):
    """
    Process web search requests using arXiv
    """
    try:
        # Generate optimized search query using LLM
        search_query = await llm_make_arxiv_query(request.prompt)
        logger.info(f"Generated search query: {search_query}")

        # Perform arXiv search
        results = await query_arxiv(search_query, max_results=request.max_results)

        return results

    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Error processing web search: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing web search: {str(e)}"
        )
