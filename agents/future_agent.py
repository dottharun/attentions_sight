from fastapi import HTTPException
from util.log import logger
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

# Load environment variables
load_dotenv()


async def llm_future_analysis(prompt: str) -> str:
    """
    Analyze research paper content and generate comprehensive insights using Groq LLM.

    Args:
        prompt (str): Combined string containing both the research paper text and user's specific
                     analysis requirements or questions

    Returns:
        str: Markdown formatted text containing paper analysis, future work suggestions,
             and critical evaluation

    Raises:
        HTTPException: If LLM analysis generation fails
    """
    try:
        # Initialize Groq LLM with settings optimized for detailed analysis
        llm = ChatGroq(
            temperature=0.7,  # Slightly higher temperature for more creative analysis
            model="llama3-8b-8192",
            stop_sequences=[],
        )

        # Create system prompt to guide comprehensive analysis
        system_prompt = """You are an expert research analyst specializing in academic paper review and analysis.
        Provide a comprehensive analysis in the following structured format:

        1. Key Findings and Contributions:
           - Main research contributions
           - Novel methodologies or approaches
           - Significant results and their implications

        2. Critical Analysis:
           - Strengths of the research
           - Limitations and potential weaknesses
           - Methodology assessment
           - Validity of conclusions

        3. Future Research Directions:
           - Potential extensions of the work
           - Unexplored areas and opportunities
           - Technical improvements
           - Practical applications

        4. Research Impact:
           - Potential influence on the field
           - Industrial applications
           - Societal implications

        Format the response in clean markdown with appropriate headers and bullet points.
        Be specific, technical, and provide justification for each point."""

        # Combine system prompt with paper content and user requirements
        messages = [
            HumanMessage(
                content=f"{system_prompt}\n\nPaper and analysis requirements:\n{prompt}\n\nAnalysis:"
            ),
        ]

        # Get response from LLM
        response = llm.invoke(messages)

        # Extract and clean the analysis
        analysis = str(response.content).strip()

        logger.info("Generated research analysis successfully")
        return analysis

    except Exception as e:
        logger.error(f"Error in LLM research analysis generation: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to generate research analysis"
        )
