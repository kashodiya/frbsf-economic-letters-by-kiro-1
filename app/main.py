"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.db.database import initialize_database
from app.db.repository import DatabaseRepository
from app.services.scraper import ScraperService
from app.services.llm import LLMService
from app.models.schemas import (
    LetterListResponse,
    LetterDetailResponse,
    FetchResponse,
    FetchMoreRequest,
    QuestionCreate,
    QuestionResponse,
    DeleteResponse,
    ErrorResponse,
    Letter,
    Question
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Global service instances
db_repo: DatabaseRepository = None
scraper_service: ScraperService = None
llm_service: LLMService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global db_repo, scraper_service, llm_service
    
    # Startup
    logger.info("Starting application...")
    
    # Initialize database
    initialize_database(settings.database_path)
    
    # Initialize services
    db_repo = DatabaseRepository(settings.database_path)
    scraper_service = ScraperService(
        base_url=settings.frbsf_base_url,
        timeout=settings.scrape_timeout,
        max_retries=settings.max_retries
    )
    llm_service = LLMService(
        region=settings.aws_region,
        model_id=settings.bedrock_model_id,
        profile=settings.aws_default_profile
    )
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="Economic Letter Insights",
    description="AI-powered analysis of FRBSF economic letters",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML file."""
    return FileResponse("static/index.html")


@app.get("/api/letters", response_model=LetterListResponse)
async def get_letters(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get paginated list of letters.
    
    Args:
        limit: Maximum number of letters to return
        offset: Number of letters to skip
        
    Returns:
        LetterListResponse with letters and pagination info
    """
    try:
        letters_data, total = db_repo.get_letters(limit=limit, offset=offset)
        
        letters = [Letter(**letter) for letter in letters_data]
        has_more = (offset + len(letters)) < total
        
        return LetterListResponse(
            letters=letters,
            total=total,
            has_more=has_more
        )
    except Exception as e:
        logger.error(f"Error getting letters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/letters/fetch-new", response_model=FetchResponse)
async def fetch_new_letters():
    """
    Fetch new letters from FRBSF website.
    
    Returns:
        FetchResponse with count of new letters added
    """
    try:
        # Fetch first page
        letters = await scraper_service.fetch_letters_page(page=1)
        
        new_count = 0
        for letter in letters:
            # Check if letter already exists
            if not db_repo.letter_exists(letter.url):
                # Fetch full content
                full_content = await scraper_service.fetch_letter_content(letter.url)
                if full_content:
                    letter.content = full_content
                
                # Insert into database
                db_repo.insert_letter(
                    title=letter.title,
                    url=letter.url,
                    publication_date=letter.publication_date,
                    summary=letter.summary,
                    content=letter.content
                )
                new_count += 1
        
        message = f"Added {new_count} new letter(s)" if new_count > 0 else "No new letters found"
        return FetchResponse(new_count=new_count, message=message)
        
    except Exception as e:
        logger.error(f"Error fetching new letters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/letters/fetch-more", response_model=FetchResponse)
async def fetch_more_letters(request: FetchMoreRequest):
    """
    Fetch older letters from FRBSF website.
    
    Args:
        request: FetchMoreRequest with current page number
        
    Returns:
        FetchResponse with count of letters added
    """
    try:
        total_added = 0
        current_page = request.current_page
        max_attempts = 5  # Try up to 5 pages to find new letters
        
        for attempt in range(max_attempts):
            next_page = current_page + attempt + 1
            logger.info(f"Attempting to fetch page {next_page}")
            
            letters = await scraper_service.fetch_letters_page(page=next_page)
            
            if not letters:
                logger.info(f"No letters found on page {next_page}")
                break
            
            added_count = 0
            for letter in letters:
                # Check if letter already exists
                if not db_repo.letter_exists(letter.url):
                    # Fetch full content
                    full_content = await scraper_service.fetch_letter_content(letter.url)
                    if full_content:
                        letter.content = full_content
                    
                    # Insert into database
                    db_repo.insert_letter(
                        title=letter.title,
                        url=letter.url,
                        publication_date=letter.publication_date,
                        summary=letter.summary,
                        content=letter.content
                    )
                    added_count += 1
            
            total_added += added_count
            
            # If we found new letters, stop searching
            if added_count > 0:
                logger.info(f"Found {added_count} new letters on page {next_page}")
                message = f"Added {total_added} new letter(s) from page {next_page}"
                return FetchResponse(new_count=total_added, message=message)
            else:
                logger.info(f"Page {next_page} had {len(letters)} letters but all already exist")
        
        # If we get here, we tried multiple pages but found no new letters
        if total_added == 0:
            message = f"Checked {max_attempts} pages but all letters already exist. You may have reached the end of available letters."
        else:
            message = f"Added {total_added} new letter(s)"
        
        return FetchResponse(new_count=total_added, message=message)
        
    except Exception as e:
        logger.error(f"Error fetching more letters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/letters/{letter_id}", response_model=LetterDetailResponse)
async def get_letter_detail(letter_id: int):
    """
    Get letter details with questions.
    
    Args:
        letter_id: The letter ID
        
    Returns:
        LetterDetailResponse with letter and questions
    """
    try:
        # Get letter
        letter_data = db_repo.get_letter_by_id(letter_id)
        if not letter_data:
            raise HTTPException(status_code=404, detail="Letter not found")
        
        # Get questions
        questions_data = db_repo.get_questions_for_letter(letter_id)
        
        letter = Letter(**letter_data)
        questions = [Question(**q) for q in questions_data]
        
        return LetterDetailResponse(letter=letter, questions=questions)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting letter detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/letters/{letter_id}/questions", response_model=QuestionResponse)
async def submit_question(letter_id: int, question_data: QuestionCreate):
    """
    Submit a question about a letter and get LLM answer.
    
    Args:
        letter_id: The letter ID
        question_data: QuestionCreate with question text
        
    Returns:
        QuestionResponse with answer and metadata
    """
    try:
        # Get letter
        letter_data = db_repo.get_letter_by_id(letter_id)
        if not letter_data:
            raise HTTPException(status_code=404, detail="Letter not found")
        
        # Generate answer using LLM
        answer = await llm_service.generate_insight(
            letter_content=letter_data['content'],
            question=question_data.question
        )
        
        # Store question and answer
        question_id = db_repo.insert_question(
            letter_id=letter_id,
            question=question_data.question,
            answer=answer
        )
        
        # Get the stored question to get timestamp
        questions = db_repo.get_questions_for_letter(letter_id)
        stored_question = next((q for q in questions if q['id'] == question_id), None)
        
        timestamp = stored_question['created_at'] if stored_question else ""
        
        return QuestionResponse(
            question_id=question_id,
            answer=answer,
            timestamp=timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/questions/{question_id}", response_model=DeleteResponse)
async def delete_question(question_id: int):
    """
    Delete a question-answer pair.
    
    Args:
        question_id: The question ID
        
    Returns:
        DeleteResponse with success status
    """
    try:
        deleted = db_repo.delete_question(question_id)
        
        if deleted:
            return DeleteResponse(success=True, message="Question deleted successfully")
        else:
            raise HTTPException(status_code=404, detail="Question not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
