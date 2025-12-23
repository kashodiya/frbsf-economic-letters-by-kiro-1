"""Pydantic models for API request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LetterData(BaseModel):
    """Base letter data model."""
    title: str
    url: str
    publication_date: str
    summary: Optional[str] = None
    content: str


class Letter(LetterData):
    """Letter model with database fields."""
    id: int
    created_at: str


class QuestionCreate(BaseModel):
    """Model for creating a new question."""
    question: str = Field(..., min_length=1, max_length=5000)


class Question(BaseModel):
    """Question model with database fields."""
    id: int
    letter_id: int
    question: str
    answer: str
    created_at: str


class LetterListResponse(BaseModel):
    """Response model for letter list endpoint."""
    letters: List[Letter]
    total: int
    has_more: bool


class LetterDetailResponse(BaseModel):
    """Response model for letter detail endpoint."""
    letter: Letter
    questions: List[Question]


class FetchResponse(BaseModel):
    """Response model for fetch operations."""
    new_count: int
    message: str


class FetchMoreRequest(BaseModel):
    """Request model for fetching more letters."""
    current_page: int = Field(default=1, ge=1)


class QuestionResponse(BaseModel):
    """Response model for question submission."""
    question_id: int
    answer: str
    timestamp: str


class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    success: bool
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
