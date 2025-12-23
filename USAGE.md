# Usage Guide

## Quick Start

1. **Start the application**:
   ```bash
   uv run python run.py
   ```
   Or on Windows, double-click `start.bat`

2. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

## Step-by-Step Guide

### 1. Fetch Economic Letters

When you first open the application, the database will be empty. Click the **"Fetch New Letters"** button to scrape the latest economic letters from the FRBSF website.

- The application will fetch letters from the first page
- New letters will be added to the database
- You'll see a message indicating how many letters were added

### 2. Browse Letters

The main page displays all letters in a card layout with:
- Letter title
- Publication date
- Brief summary (if available)

Click on any letter card to view its full content.

### 3. Load More Historical Letters

To access older letters:
1. Click the **"Load More"** button
2. The application will fetch the next page of letters from FRBSF
3. New letters will be added to your database

### 4. View Letter Details

When you click on a letter:
- Full letter content is displayed
- A link to the original FRBSF page is provided (opens in new tab)
- Question input form is available
- Previous questions and answers are shown (if any)

### 5. Ask Questions

To get AI-powered insights:
1. Type your question in the text area
2. Click **"Ask Question"**
3. Wait for the AI to generate an answer (may take a few seconds)
4. The question and answer will be displayed below
5. The Q&A is automatically saved to the database

Example questions:
- "What are the main findings of this letter?"
- "How does this relate to current inflation trends?"
- "What policy implications are discussed?"
- "Can you summarize the key data points?"

### 6. Manage Question History

All questions and answers are saved and displayed when you revisit a letter.

To delete a question:
1. Find the question card
2. Click the **"Delete"** button
3. Confirm the deletion
4. The question and answer will be removed

### 7. Navigate Back

Click the **"Back to List"** button to return to the main letter list.

## Tips

- **First Time Setup**: Always click "Fetch New Letters" when you first start the application
- **Regular Updates**: Click "Fetch New Letters" periodically to get the latest publications
- **Historical Research**: Use "Load More" to build a comprehensive archive of letters
- **Question Quality**: More specific questions tend to get better answers from the AI
- **Original Source**: Always check the original FRBSF page for charts, graphs, and formatting

## Troubleshooting

### No Letters Showing
- Click "Fetch New Letters" to populate the database
- Check your internet connection
- Verify the FRBSF website is accessible

### Questions Not Working
- Verify AWS credentials are configured correctly
- Check that the AWS_DEFAULT_PROFILE is set in .env
- Ensure you have access to AWS Bedrock in us-east-1
- Check the application logs for error messages

### Application Won't Start
- Ensure UV is installed: `uv --version`
- Run `uv sync` to install dependencies
- Check that port 8000 is not already in use
- Review the .env file for correct configuration

## Advanced Usage

### Custom Configuration

Edit the `.env` file to customize:
- Port number (default: 8000)
- Database location (default: ./data/letters.db)
- AWS region (default: us-east-1)
- Bedrock model ID
- Scraping timeout and retry settings

### Running on Different Port

Change the PORT in `.env`:
```
PORT=3000
```

Then restart the application.

### Database Management

The SQLite database is stored at `./data/letters.db`. You can:
- Back it up by copying the file
- Reset it by deleting the file (will be recreated on next start)
- Query it directly using any SQLite client

## API Usage

If you want to integrate with the API directly:

### Get Letters
```bash
curl http://localhost:8000/api/letters?limit=10&offset=0
```

### Fetch New Letters
```bash
curl -X POST http://localhost:8000/api/letters/fetch-new
```

### Submit Question
```bash
curl -X POST http://localhost:8000/api/letters/1/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main findings?"}'
```

### Delete Question
```bash
curl -X DELETE http://localhost:8000/api/questions/1
```

## Support

For issues or questions:
1. Check the application logs in the terminal
2. Review the README.md for configuration details
3. Verify AWS credentials and permissions
