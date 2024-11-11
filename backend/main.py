from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from agents.future_agent import llm_future_analysis
from agents.search_agent import query_arxiv, llm_make_arxiv_query
from util.log import logger


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


@app.post("/api/future-analysis")
async def future_analysis(request: SearchRequest):
    """
    Process the given research paper and given suggestions for future improvements, critic
    """
    try:
        analysis = await llm_future_analysis(request.prompt)
        logger.info(f"Generated analysis: {analysis}")

        return analysis

    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Error processing web search: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing web search: {str(e)}"
        )
