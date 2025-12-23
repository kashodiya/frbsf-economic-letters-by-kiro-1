# Design Document

## Overview

The Economic Letter Insights application is a full-stack web application that combines web scraping, AI-powered analysis, and a modern single-page application interface. The system consists of:

1. **Backend**: FastAPI server handling HTTP requests, web scraping, database operations, and AWS Bedrock LLM integration
2. **Frontend**: Single-file VueJS application with Vuetify UI components and VueRouter for navigation
3. **Storage**: SQLite database for persisting letters and question history
4. **AI Integration**: AWS Bedrock Claude Sonnet model for generating insights

The application follows a client-server architecture where the frontend communicates with the backend via REST API endpoints, and the backend manages all external integrations (web scraping and LLM).

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  VueJS SPA (index.html)                               │  │
│  │  - Vuetify UI Components                              │  │
│  │  - VueRouter for Navigation                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   API        │  │   Scraper    │  │   LLM        │      │
│  │   Routes     │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                  │               │
│         └─────────────────┴──────────────────┘               │
│                           │                                  │
│                  ┌────────▼────────┐                         │
│                  │   Database      │                         │
│                  │   Repository    │                         │
│                  └────────┬────────┘                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  SQLite DB      │
                  │  (letters.db)   │
                  └─────────────────┘
                           
External Services:
  - FRBSF Website (scraping)
  - AWS Bedrock (LLM)
```

### Technology Stack

- **Backend Framework**: FastAPI (Python)
- **Frontend Framework**: VueJS 3 with Composition API
- **UI Library**: Vuetify 3
- **Routing**: VueRouter 4
- **Database**: SQLite 3
- **Web Scraping**: BeautifulSoup4 + httpx
- **LLM**: AWS Bedrock (boto3)
- **Environment Management**: UV
- **Configuration**: python-dotenv

## Components and Interfaces

### Backend Components

#### 1. API Routes (`main.py`)

FastAPI application with the following endpoints:

- `GET /` - Serves the index.html file
- `GET /api/letters` - Returns list of letters with pagination
  - Query params: `limit` (default 20), `offset` (default 0)
  - Response: `{ letters: Letter[], total: int, has_more: bool }`
- `POST /api/letters/fetch-new` - Fetches new letters from FRBSF
  - Response: `{ new_count: int, message: str }`
- `POST /api/letters/fetch-more` - Fetches older letters
  - Body: `{ current_page: int }`
  - Response: `{ added_count: int, has_more: bool }`
- `GET /api/letters/{letter_id}` - Returns letter details with questions
  - Response: `{ letter: Letter, questions: Question[] }`
- `POST /api/letters/{letter_id}/questions` - Submits a question
  - Body: `{ question: str }`
  - Response: `{ question_id: int, answer: str, timestamp: str }`
- `DELETE /api/questions/{question_id}` - Deletes a question-answer pair
  - Response: `{ success: bool }`

#### 2. Scraper Service (`services/scraper.py`)

Handles web scraping from FRBSF website:

```python
class ScraperService:
    def __init__(self, base_url: str)
    async def fetch_letters_page(self, page: int = 1) -> List[LetterData]
    async def fetch_letter_content(self, url: str) -> str
    def parse_letter_list(self, html: str) -> List[LetterData]
    def parse_letter_content(self, html: str) -> str
```

#### 3. LLM Service (`services/llm.py`)

Manages AWS Bedrock interactions:

```python
class LLMService:
    def __init__(self, region: str, profile: str)
    async def generate_insight(self, letter_content: str, question: str) -> str
    def _build_prompt(self, letter_content: str, question: str) -> str
```

#### 4. Database Repository (`db/repository.py`)

Handles all database operations:

```python
class DatabaseRepository:
    def __init__(self, db_path: str)
    def initialize_schema(self)
    
    # Letter operations
    def get_letters(self, limit: int, offset: int) -> Tuple[List[Letter], int]
    def get_letter_by_id(self, letter_id: int) -> Optional[Letter]
    def get_letter_by_url(self, url: str) -> Optional[Letter]
    def insert_letter(self, letter: LetterData) -> int
    def letter_exists(self, url: str) -> bool
    
    # Question operations
    def get_questions_for_letter(self, letter_id: int) -> List[Question]
    def insert_question(self, letter_id: int, question: str, answer: str) -> int
    def delete_question(self, question_id: int) -> bool
```

### Frontend Components

#### 1. Main App Structure (`index.html`)

Single HTML file containing:
- Vue app initialization
- VueRouter configuration
- Vuetify setup
- Component definitions using `<template>` tags with IDs

#### 2. Vue Components

**LetterList Component** (`#letter-list-template`)
- Displays paginated list of letters
- Fetch new/more buttons
- Navigation to letter details

**LetterDetail Component** (`#letter-detail-template`)
- Shows letter content and metadata
- Link to original FRBSF page
- Question input form
- List of previous questions/answers with delete buttons

**LoadingSpinner Component** (`#loading-spinner-template`)
- Reusable loading indicator

#### 3. Vue Router Configuration

```javascript
const routes = [
  { path: '/', component: LetterList },
  { path: '/letter/:id', component: LetterDetail }
]
```

## Data Models

### Database Schema

```sql
CREATE TABLE letters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    publication_date TEXT NOT NULL,
    summary TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    letter_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (letter_id) REFERENCES letters(id) ON DELETE CASCADE
);

CREATE INDEX idx_letters_date ON letters(publication_date DESC);
CREATE INDEX idx_questions_letter ON questions(letter_id);
```

### Python Data Models

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LetterData(BaseModel):
    title: str
    url: str
    publication_date: str
    summary: Optional[str]
    content: str

class Letter(LetterData):
    id: int
    created_at: datetime

class QuestionCreate(BaseModel):
    question: str

class Question(BaseModel):
    id: int
    letter_id: int
    question: str
    answer: str
    created_at: datetime

class LetterListResponse(BaseModel):
    letters: list[Letter]
    total: int
    has_more: bool

class FetchResponse(BaseModel):
    new_count: int
    message: str
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Letter display completeness
*For any* letter object, when rendered in the UI, the output should contain the letter title, publication date, and summary.
**Validates: Requirements 1.2**

### Property 2: Scraper field extraction completeness
*For any* valid FRBSF letter page HTML, the scraper should extract all required fields (title, date, URL, and content) without missing data.
**Validates: Requirements 1.4**

### Property 3: Scraper error resilience
*For any* invalid or malformed HTML input, the scraper should handle errors gracefully without crashing the application.
**Validates: Requirements 1.5**

### Property 4: Letter storage and retrieval round-trip
*For any* letter object, storing it in the database and then retrieving it should produce an equivalent letter with all fields preserved.
**Validates: Requirements 12.2**

### Property 5: Question storage and retrieval round-trip
*For any* question-answer pair associated with a letter, storing it in the database and then retrieving all questions for that letter should include the original question-answer pair with all fields preserved.
**Validates: Requirements 6.1, 6.2**

### Property 6: Question chronological ordering
*For any* set of questions associated with a letter, retrieving them from the database should return them ordered by creation timestamp in ascending order.
**Validates: Requirements 6.3**

### Property 7: Question deletion removes from storage
*For any* question-answer pair in the database, deleting it should result in that question no longer being retrievable from the database.
**Validates: Requirements 7.2**

### Property 8: Delete button presence
*For any* question-answer pair displayed in the UI, a delete button should be rendered alongside it.
**Validates: Requirements 7.1**

### Property 9: Duplicate letter prevention
*For any* letter that already exists in the database (matched by URL), attempting to insert it again should not create a duplicate record.
**Validates: Requirements 13.3, 14.3**

### Property 10: New letter count accuracy
*For any* fetch operation, the count of newly added letters returned should equal the number of letters actually inserted into the database.
**Validates: Requirements 13.4**

### Property 11: Pagination offset tracking
*For any* sequence of "load more" operations, the pagination offset should increment correctly to fetch non-overlapping pages of results.
**Validates: Requirements 14.1**

### Property 12: Foreign key integrity
*For any* question stored in the database, it should have a valid foreign key reference to an existing letter, and deleting the letter should cascade delete all associated questions.
**Validates: Requirements 12.3**

### Property 13: Error handling preserves data
*For any* database operation failure, the error should be logged and handled without corrupting existing data or crashing the application.
**Validates: Requirements 3.4, 5.4, 6.4, 12.5**

### Property 14: LLM configuration correctness
*For any* LLM request, the system should use the model "us.anthropic.claude-sonnet-4-20250514-v1:0" in region "us-east-1".
**Validates: Requirements 5.2, 8.4**

### Property 15: Missing configuration handling
*For any* missing required environment variable, the system should either use a documented default value or fail with a clear error message indicating which variable is missing.
**Validates: Requirements 11.3**

### Property 16: Original link display
*For any* letter detail page, the rendered output should include a link element pointing to the original FRBSF URL.
**Validates: Requirements 4.1**

## Error Handling

### Backend Error Handling

1. **Web Scraping Errors**
   - Network timeouts: Retry with exponential backoff (max 3 attempts)
   - Invalid HTML: Log warning and skip malformed entries
   - HTTP errors: Return appropriate status codes to frontend

2. **Database Errors**
   - Connection failures: Retry connection on startup
   - Constraint violations: Log and return user-friendly error messages
   - Transaction failures: Rollback and preserve data integrity

3. **LLM Service Errors**
   - API rate limits: Implement retry logic with backoff
   - Authentication failures: Log detailed error and return 500 status
   - Timeout: Set reasonable timeout (30s) and return error to user
   - Invalid responses: Validate response format and handle gracefully

4. **General Error Handling**
   - All exceptions logged with stack traces
   - User-facing errors return JSON with `{ error: str, detail: str }`
   - Internal errors return 500 status with generic message

### Frontend Error Handling

1. **API Request Errors**
   - Network errors: Display "Connection failed" message with retry button
   - 4xx errors: Display specific error message from backend
   - 5xx errors: Display generic "Server error" message

2. **User Input Validation**
   - Empty questions: Disable submit button
   - Invalid data: Show inline validation messages

3. **Loading States**
   - Show loading spinner during async operations
   - Disable action buttons while processing
   - Timeout after 60 seconds with error message

## Testing Strategy

### Unit Testing

The application will use **pytest** for Python unit tests with the following focus areas:

1. **Database Repository Tests**
   - Test CRUD operations for letters and questions
   - Test pagination logic
   - Test duplicate detection
   - Example: Test that inserting a letter with a duplicate URL raises an error

2. **Scraper Service Tests**
   - Test HTML parsing with sample FRBSF pages
   - Test error handling with malformed HTML
   - Example: Test that scraper extracts correct title from a known HTML structure

3. **LLM Service Tests**
   - Test prompt construction
   - Test error handling for API failures
   - Mock Bedrock client for testing
   - Example: Test that authentication errors are properly caught and logged

4. **API Endpoint Tests**
   - Test request/response formats
   - Test error status codes
   - Test authentication and authorization
   - Example: Test that GET /api/letters returns correct JSON structure

### Property-Based Testing

The application will use **Hypothesis** for property-based testing in Python. Each property-based test will:

- Run a minimum of 100 iterations with randomly generated inputs
- Be tagged with a comment explicitly referencing the correctness property from this design document
- Use the format: `# Feature: economic-letter-insights, Property {number}: {property_text}`
- Implement exactly ONE correctness property per test

**Property-Based Test Coverage:**

1. **Property 1 Test**: Generate random letter objects and verify all required fields appear in rendered output
2. **Property 2 Test**: Generate various HTML structures and verify scraper extracts all fields
3. **Property 3 Test**: Generate malformed HTML inputs and verify no crashes occur
4. **Property 4 Test**: Generate random letters, store and retrieve, verify equality
5. **Property 5 Test**: Generate random question-answer pairs, store and retrieve, verify equality
6. **Property 6 Test**: Generate random sets of questions with timestamps, verify chronological ordering
7. **Property 7 Test**: Generate random questions, delete them, verify they're gone
8. **Property 8 Test**: Generate random questions, render UI, verify delete button exists
9. **Property 9 Test**: Generate random letters, insert twice, verify only one exists
10. **Property 10 Test**: Generate random letter sets, fetch and count, verify accuracy
11. **Property 11 Test**: Generate random pagination sequences, verify offset increments correctly
12. **Property 12 Test**: Generate random letters and questions, verify foreign key constraints
13. **Property 13 Test**: Generate random database failures, verify data integrity preserved
14. **Property 14 Test**: Generate random LLM requests, verify correct model and region used
15. **Property 15 Test**: Generate random missing config scenarios, verify proper error handling
16. **Property 16 Test**: Generate random letters, render detail page, verify link exists

### Integration Testing

While not the primary focus, basic integration tests will verify:
- End-to-end API flows (fetch letters → display → ask question → view answer)
- Database initialization and migration
- Frontend-backend communication

### Testing Requirements

- Unit tests and property tests are complementary: unit tests catch specific bugs, property tests verify general correctness
- All property-based tests must be tagged with their corresponding correctness property number
- Each correctness property must be implemented by a SINGLE property-based test
- Tests should avoid mocking when possible to validate real functionality
- All tests must pass before considering a feature complete

## Configuration

### Environment Variables

The application uses a `.env` file for configuration:

```
# AWS Configuration
AWS_DEFAULT_PROFILE=aws-admin-profile
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# Database
DATABASE_PATH=./data/letters.db

# Application
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Scraping
FRBSF_BASE_URL=https://www.frbsf.org/research-and-insights/publications/economic-letter/
SCRAPE_TIMEOUT=30
MAX_RETRIES=3
```

### .env.example

The project includes an `.env.example` file documenting all required variables with descriptions and example values.

## Deployment Considerations

1. **EC2 Deployment**
   - Application runs on EC2 with IAM role for AWS service access
   - No explicit AWS credentials needed
   - SQLite database stored in persistent volume

2. **Dependencies**
   - All Python dependencies managed via UV
   - Frontend dependencies loaded from CDN (Vue, Vuetify)

3. **Database**
   - SQLite file created automatically on first run
   - Regular backups recommended for production

4. **Monitoring**
   - Application logs to stdout/stderr
   - Consider CloudWatch integration for production

## Security Considerations

1. **Input Validation**
   - Sanitize all user inputs before database storage
   - Validate URLs before scraping
   - Limit question length to prevent abuse

2. **Rate Limiting**
   - Implement rate limiting on LLM endpoints to control costs
   - Limit scraping frequency to respect FRBSF servers

3. **Data Privacy**
   - Questions and answers stored locally
   - No PII collected from users
   - Consider encryption for sensitive data in production

4. **AWS Security**
   - Use IAM roles with least privilege
   - Rotate credentials regularly
   - Monitor Bedrock usage and costs
