# Requirements Document

## Introduction

This document specifies the requirements for an Economic Letter Insights application that scrapes economic letters from the Federal Reserve Bank of San Francisco (FRBSF) website and provides AI-powered insights using AWS Bedrock. The application consists of a FastAPI backend serving a VueJS single-page application with Vuetify components, enabling users to browse letters, ask questions about their content, and maintain a history of their inquiries.

## Glossary

- **Application**: The Economic Letter Insights web application system
- **Backend**: The FastAPI server component that handles HTTP requests, web scraping, and LLM interactions
- **Frontend**: The VueJS single-page application with Vuetify UI components
- **Economic Letter**: A publication from the Federal Reserve Bank of San Francisco containing economic analysis and insights
- **FRBSF**: Federal Reserve Bank of San Francisco
- **LLM**: Large Language Model (AWS Bedrock Claude Sonnet)
- **User**: A person interacting with the application through a web browser
- **Question History**: Stored questions and answers associated with specific economic letters
- **AWS Bedrock**: Amazon Web Services managed service for accessing foundation models
- **UV**: Python package and environment management tool
- **SQLite Database**: Local database file used to persist letters, questions, and answers

## Requirements

### Requirement 1

**User Story:** As a user, I want to view a list of economic letters from FRBSF, so that I can browse available publications and select ones to read and analyze.

#### Acceptance Criteria

1. WHEN the user opens the application THEN the Frontend SHALL display a list of economic letters scraped from https://www.frbsf.org/research-and-insights/publications/economic-letter/
2. WHEN displaying each letter THEN the Frontend SHALL show the letter title, publication date, and a brief summary
3. WHEN the user clicks on a letter THEN the Frontend SHALL navigate to a detail view for that specific letter
4. WHEN the Backend scrapes the FRBSF website THEN the Backend SHALL extract letter metadata including title, date, URL, and content
5. WHEN the scraping process encounters an error THEN the Backend SHALL log the error and return available data without crashing

### Requirement 2

**User Story:** As a user, I want to fetch new economic letters, so that I can access the most recently published content.

#### Acceptance Criteria

1. WHEN the user clicks a refresh button THEN the Backend SHALL scrape the FRBSF website for new letters published since the last fetch
2. WHEN new letters are found THEN the Backend SHALL add them to the available letters list
3. WHEN the fetch completes THEN the Frontend SHALL update the display to show newly available letters
4. WHEN no new letters are found THEN the Application SHALL notify the user that the list is up to date

### Requirement 3

**User Story:** As a user, I want to fetch older economic letters, so that I can access historical publications for research and analysis.

#### Acceptance Criteria

1. WHEN the user clicks a "load more" button THEN the Backend SHALL scrape additional pages from the FRBSF website to retrieve older letters
2. WHEN older letters are retrieved THEN the Frontend SHALL append them to the existing list
3. WHEN the Backend reaches the last available page THEN the Application SHALL disable the "load more" button and notify the user
4. WHEN pagination fails THEN the Backend SHALL return an error message without affecting already loaded letters

### Requirement 4

**User Story:** As a user, I want to navigate to the original FRBSF page of a letter, so that I can read the full publication in its original format.

#### Acceptance Criteria

1. WHEN viewing a letter detail page THEN the Frontend SHALL display a link to the original FRBSF publication
2. WHEN the user clicks the original publication link THEN the Frontend SHALL open the FRBSF page in a new browser tab
3. WHEN the link is displayed THEN the Frontend SHALL clearly indicate it leads to an external website

### Requirement 5

**User Story:** As a user, I want to ask questions about an economic letter using AI, so that I can gain insights and understanding of the content.

#### Acceptance Criteria

1. WHEN viewing a letter detail page THEN the Frontend SHALL display an input field for entering questions
2. WHEN the user submits a question THEN the Backend SHALL send the question and letter content to AWS Bedrock model us.anthropic.claude-sonnet-4-20250514-v1:0 in us-east-1 region
3. WHEN the LLM generates a response THEN the Frontend SHALL display the answer below the question
4. WHEN the LLM request fails THEN the Backend SHALL return an error message and the Frontend SHALL display it to the user
5. WHEN processing a question THEN the Frontend SHALL show a loading indicator until the response is received

### Requirement 6

**User Story:** As a user, I want my questions and answers to be saved, so that I can review previous insights when I revisit a letter.

#### Acceptance Criteria

1. WHEN the user submits a question about a letter THEN the Backend SHALL store the question, answer, and timestamp in the SQLite Database associated with that letter
2. WHEN the user opens a letter they previously asked questions about THEN the Frontend SHALL display all stored questions and answers for that letter retrieved from the SQLite Database
3. WHEN displaying question history THEN the Frontend SHALL show questions in chronological order with timestamps
4. WHEN the storage operation fails THEN the Backend SHALL log the error and return the answer without persisting it

### Requirement 7

**User Story:** As a user, I want to delete previous questions and answers, so that I can remove outdated or irrelevant inquiries from my history.

#### Acceptance Criteria

1. WHEN viewing stored questions THEN the Frontend SHALL display a delete button next to each question-answer pair
2. WHEN the user clicks the delete button THEN the Backend SHALL remove that specific question-answer pair from storage
3. WHEN deletion completes successfully THEN the Frontend SHALL remove the question-answer pair from the display
4. WHEN deletion fails THEN the Backend SHALL return an error and the Frontend SHALL notify the user

### Requirement 8

**User Story:** As a developer, I want the application to use AWS Bedrock without explicit credentials, so that deployment on EC2 with IAM roles is simplified.

#### Acceptance Criteria

1. WHEN the Backend initializes the AWS Bedrock client THEN the Backend SHALL use the AWS_DEFAULT_PROFILE environment variable set to aws-admin-profile
2. WHEN making Bedrock API calls THEN the Backend SHALL rely on IAM role credentials from the EC2 instance
3. WHEN AWS authentication fails THEN the Backend SHALL log the error with sufficient detail for troubleshooting
4. WHEN the Backend connects to Bedrock THEN the Backend SHALL use the us-east-1 region

### Requirement 9

**User Story:** As a developer, I want the frontend to be a single HTML file with VueJS and Vuetify, so that the application is simple to deploy and maintain.

#### Acceptance Criteria

1. WHEN the Backend serves the frontend THEN the Backend SHALL serve a single index.html file containing the complete VueJS application
2. WHEN defining Vue components THEN the Frontend SHALL use HTML elements with id references rather than inline string templates
3. WHEN the Frontend initializes THEN the Frontend SHALL load Vuetify components and VueRouter for navigation
4. WHEN the user navigates between views THEN VueRouter SHALL handle routing without full page reloads

### Requirement 10

**User Story:** As a developer, I want to use UV for all Python operations, so that package and environment management is consistent and modern.

#### Acceptance Criteria

1. WHEN initializing the project THEN the developer SHALL use UV to create the project structure
2. WHEN installing dependencies THEN the developer SHALL use UV to manage all Python packages
3. WHEN running the application THEN the developer SHALL use UV to execute the FastAPI server
4. WHEN the project includes dependency specifications THEN the project SHALL use UV-compatible configuration files (pyproject.toml)

### Requirement 11

**User Story:** As a developer, I want environment configuration through .env files, so that sensitive settings can be managed separately from code.

#### Acceptance Criteria

1. WHEN the application starts THEN the Backend SHALL load configuration from a .env file
2. WHEN the project is shared THEN the project SHALL include an .env.example file documenting required environment variables
3. WHEN environment variables are missing THEN the Backend SHALL use sensible defaults or fail with clear error messages
4. WHEN the .env file contains AWS_DEFAULT_PROFILE THEN the Backend SHALL use that profile for AWS service authentication

### Requirement 12

**User Story:** As a developer, I want all application data stored in SQLite, so that the application has a simple, file-based persistence layer without requiring external database services.

#### Acceptance Criteria

1. WHEN the Backend initializes THEN the Backend SHALL create or connect to a SQLite Database file
2. WHEN storing economic letters THEN the Backend SHALL persist letter metadata and content in the SQLite Database
3. WHEN storing questions and answers THEN the Backend SHALL persist them in the SQLite Database with foreign key relationships to their associated letters
4. WHEN the database schema is missing THEN the Backend SHALL create all required tables automatically on startup
5. WHEN database operations fail THEN the Backend SHALL log detailed error messages and handle failures gracefully

### Requirement 13

**User Story:** As a user, I want the application to automatically fetch and store new letters, so that I always have access to the latest publications without manual intervention.

#### Acceptance Criteria

1. WHEN new letters are scraped from FRBSF THEN the Backend SHALL check if each letter already exists in the SQLite Database
2. WHEN a letter does not exist in the database THEN the Backend SHALL insert it as a new record
3. WHEN a letter already exists in the database THEN the Backend SHALL skip it to avoid duplicates
4. WHEN the fetch operation completes THEN the Backend SHALL return a count of newly added letters

### Requirement 14

**User Story:** As a user, I want to load more historical letters from the archive, so that I can access older publications beyond the initial page.

#### Acceptance Criteria

1. WHEN the user requests more past letters THEN the Backend SHALL track the current pagination offset
2. WHEN fetching past letters THEN the Backend SHALL scrape the next page of results from the FRBSF website
3. WHEN past letters are retrieved THEN the Backend SHALL store them in the SQLite Database if they do not already exist
4. WHEN all available letters have been fetched THEN the Backend SHALL indicate that no more letters are available
