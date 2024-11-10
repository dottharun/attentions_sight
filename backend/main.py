from fastapi import FastAPI
from contextlib import asynccontextmanager
from agents.search_agent import query_arxiv


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


# Create a FastAPI instance
# app = FastAPI(lifespan=lifespan)
app = FastAPI()


# Route to fetch arXiv results dynamically
@app.get("/arxiv/{query}")
async def get_arxiv_results(query: str, max_results: int = 5):
    result = await query_arxiv(query, max_results)
    return result
