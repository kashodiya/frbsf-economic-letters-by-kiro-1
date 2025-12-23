# Implementation Plan

- [x] 1. Initialize project structure with UV


  - Use UV to create new Python project with pyproject.toml
  - Set up directory structure: app/, app/services/, app/db/, app/models/, static/
  - Create .env.example file with all required environment variables
  - Create .env file for local development
  - _Requirements: 10.4, 11.2_





- [ ] 2. Set up database models and repository
  - [ ] 2.1 Create SQLite database schema
    - Write SQL schema for letters and questions tables with indexes


    - Implement database initialization function
    - _Requirements: 12.1, 12.4_
  
  - [ ] 2.2 Implement database repository class
    - Create DatabaseRepository with connection management
    - Implement letter CRUD operations (insert, get_by_id, get_by_url, get_letters with pagination)
    - Implement question CRUD operations (insert, get_for_letter, delete)
    - Implement duplicate checking logic
    - _Requirements: 12.2, 12.3, 13.1, 13.2, 13.3_
  
  - [ ]* 2.3 Write property test for letter storage round-trip
    - **Property 4: Letter storage and retrieval round-trip**
    - **Validates: Requirements 12.2**
  
  - [ ]* 2.4 Write property test for question storage round-trip
    - **Property 5: Question storage and retrieval round-trip**
    - **Validates: Requirements 6.1, 6.2**
  
  - [ ]* 2.5 Write property test for duplicate prevention
    - **Property 9: Duplicate letter prevention**
    - **Validates: Requirements 13.3, 14.3**
  
  - [ ]* 2.6 Write property test for foreign key integrity
    - **Property 12: Foreign key integrity**




    - **Validates: Requirements 12.3**
  
  - [ ]* 2.7 Write property test for question chronological ordering
    - **Property 6: Question chronological ordering**
    - **Validates: Requirements 6.3**

- [ ] 3. Implement web scraper service
  - [ ] 3.1 Create scraper service class
    - Implement HTTP client with httpx for async requests
    - Create methods to fetch FRBSF letter list pages
    - Implement HTML parsing with BeautifulSoup4 to extract letter metadata
    - Implement letter content extraction from individual letter pages
    - Add pagination support for fetching older letters
    - _Requirements: 1.4, 2.1, 3.1, 14.2_
  
  - [ ]* 3.2 Write property test for scraper field extraction
    - **Property 2: Scraper field extraction completeness**
    - **Validates: Requirements 1.4**




  
  - [ ]* 3.3 Write property test for scraper error resilience
    - **Property 3: Scraper error resilience**
    - **Validates: Requirements 1.5**
  
  - [ ]* 3.4 Write unit tests for scraper with sample HTML
    - Test parsing of known FRBSF HTML structures
    - Test pagination logic
    - _Requirements: 1.4, 3.1_

- [ ] 4. Implement LLM service with AWS Bedrock
  - [ ] 4.1 Create LLM service class
    - Initialize boto3 Bedrock client with profile and region from environment


    - Implement prompt construction for letter insights
    - Implement async method to invoke Claude Sonnet model
    - Add error handling for API failures, timeouts, and rate limits
    - _Requirements: 5.2, 8.1, 8.3, 8.4_




  
  - [ ]* 4.2 Write property test for LLM configuration
    - **Property 14: LLM configuration correctness**
    - **Validates: Requirements 5.2, 8.4**
  

  - [ ]* 4.3 Write unit tests for LLM service
    - Test prompt construction
    - Test error handling with mocked Bedrock client
    - _Requirements: 5.2, 5.4_

- [x] 5. Create Pydantic models for API

  - Define LetterData, Letter, Question, QuestionCreate models
  - Define response models: LetterListResponse, FetchResponse
  - Add validation rules for all models
  - _Requirements: 1.2, 6.1_

- [ ] 6. Implement FastAPI backend endpoints
  - [ ] 6.1 Create main FastAPI application
    - Initialize FastAPI app with CORS middleware
    - Set up dependency injection for database and services
    - Implement startup event to initialize database schema
    - Add static file serving for index.html
    - _Requirements: 9.1, 11.1, 12.4_
  
  - [ ] 6.2 Implement letter endpoints
    - GET /api/letters with pagination (limit, offset)
    - POST /api/letters/fetch-new to scrape new letters
    - POST /api/letters/fetch-more to scrape older letters
    - GET /api/letters/{letter_id} to get letter details with questions
    - _Requirements: 1.1, 2.1, 2.2, 3.1, 3.2, 13.4, 14.1_
  
  - [ ] 6.3 Implement question endpoints
    - POST /api/letters/{letter_id}/questions to submit question and get LLM answer
    - DELETE /api/questions/{question_id} to delete question-answer pair
    - _Requirements: 5.2, 6.1, 7.2_
  

  - [ ]* 6.4 Write property test for new letter count accuracy
    - **Property 10: New letter count accuracy**
    - **Validates: Requirements 13.4**




  
  - [ ]* 6.5 Write property test for pagination offset tracking
    - **Property 11: Pagination offset tracking**
    - **Validates: Requirements 14.1**
  

  - [ ]* 6.6 Write property test for question deletion
    - **Property 7: Question deletion removes from storage**
    - **Validates: Requirements 7.2**
  
  - [ ]* 6.7 Write property test for error handling data preservation
    - **Property 13: Error handling preserves data**
    - **Validates: Requirements 3.4, 5.4, 6.4, 12.5**

  
  - [ ]* 6.8 Write unit tests for API endpoints
    - Test request/response formats
    - Test error status codes
    - Test pagination logic
    - _Requirements: 1.1, 2.1, 5.2, 7.2_

- [ ] 7. Checkpoint - Ensure all backend tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [ ] 8. Create VueJS frontend in single HTML file
  - [ ] 8.1 Create index.html with Vue, Vuetify, and VueRouter setup
    - Add CDN links for Vue 3, Vuetify 3, VueRouter 4
    - Initialize Vue app with Vuetify plugin
    - Configure VueRouter with routes
    - Set up global error handling
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [ ] 8.2 Create LetterList component template
    - Define HTML template with id reference
    - Display paginated list of letters with title, date, summary
    - Add "Fetch New" and "Load More" buttons
    - Implement navigation to letter detail on click
    - Add loading states and error messages
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.3, 2.4, 3.1, 3.2, 3.3_
  



  - [ ] 8.3 Create LetterDetail component template
    - Define HTML template with id reference
    - Display letter title, date, content
    - Add link to original FRBSF page (opens in new tab)
    - Create question input form with submit button
    - Display list of previous questions and answers with timestamps
    - Add delete button for each question-answer pair
    - Add loading indicator for LLM requests




    - _Requirements: 4.1, 4.2, 5.1, 5.3, 5.5, 6.2, 6.3, 7.1, 7.3_
  
  - [ ] 8.4 Implement Vue component logic
    - Create reactive state for letters, questions, loading states
    - Implement API calls using fetch
    - Handle errors and display user-friendly messages
    - Implement question submission and deletion

    - _Requirements: 1.1, 2.1, 3.1, 5.2, 7.2_

  

  - [ ]* 8.5 Write property test for letter display completeness
    - **Property 1: Letter display completeness**
    - **Validates: Requirements 1.2**
  
  - [ ]* 8.6 Write property test for delete button presence
    - **Property 8: Delete button presence**
    - **Validates: Requirements 7.1**
  
  - [ ]* 8.7 Write property test for original link display
    - **Property 16: Original link display**
    - **Validates: Requirements 4.1**

- [ ] 9. Add configuration and environment handling
  - [ ] 9.1 Implement configuration loading
    - Use python-dotenv to load .env file
    - Create config module with typed settings
    - Add validation for required environment variables
    - _Requirements: 11.1, 11.3, 11.4_
  
  - [ ]* 9.2 Write property test for missing configuration handling
    - **Property 15: Missing configuration handling**
    - **Validates: Requirements 11.3**

- [ ] 10. Final integration and testing
  - [ ] 10.1 Test end-to-end flows manually
    - Start application and verify frontend loads
    - Test fetching new letters
    - Test loading more letters
    - Test asking questions and viewing answers
    - Test deleting questions
    - Test navigation to original FRBSF pages
    - _Requirements: All_
  
  - [ ] 10.2 Add error handling and logging
    - Ensure all exceptions are caught and logged
    - Verify user-friendly error messages in UI
    - Test error scenarios (network failures, invalid data, etc.)
    - _Requirements: 1.5, 3.4, 5.4, 6.4, 8.3, 12.5_

- [x] 11. Final Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.
