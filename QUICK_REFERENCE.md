# Quick Reference Card

## Start Application
```bash
uv run python run.py
```
Or double-click: `start.bat` (Windows)

## Access Application
```
http://localhost:8000
```

## Key Commands

### Development
```bash
# Install dependencies
uv sync

# Add new package
uv add package-name

# Run application
uv run python run.py
```

### Service Management (EC2)
```bash
# Start
sudo systemctl start economic-letters

# Stop
sudo systemctl stop economic-letters

# Restart
sudo systemctl restart economic-letters

# View logs
sudo journalctl -u economic-letters -f
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve frontend |
| GET | `/api/letters` | Get letters (paginated) |
| POST | `/api/letters/fetch-new` | Fetch new letters |
| POST | `/api/letters/fetch-more` | Fetch older letters |
| GET | `/api/letters/{id}` | Get letter details |
| POST | `/api/letters/{id}/questions` | Submit question |
| DELETE | `/api/questions/{id}` | Delete question |

## Environment Variables

```bash
AWS_DEFAULT_PROFILE=aws-admin-profile
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-5-20250929-v1:0
DATABASE_PATH=./data/letters.db
HOST=0.0.0.0
PORT=8000
```

## Project Structure

```
├── app/
│   ├── db/              # Database layer
│   ├── models/          # Pydantic schemas
│   ├── services/        # Business logic
│   ├── config.py        # Configuration
│   └── main.py          # FastAPI app
├── static/
│   └── index.html       # VueJS frontend
├── data/
│   └── letters.db       # SQLite database
├── .env                 # Environment config
└── run.py              # Entry point
```

## Common Tasks

### Reset Database
```bash
rm data/letters.db
# Restart application - DB will be recreated
```

### View Logs
```bash
# Application logs are in terminal output
# Or if running as service:
sudo journalctl -u economic-letters -n 100
```

### Backup Database
```bash
cp data/letters.db data/letters_backup_$(date +%Y%m%d).db
```

### Change Port
Edit `.env`:
```
PORT=3000
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | Change PORT in .env |
| No letters | Click "Fetch New Letters" |
| AWS errors | Check AWS_DEFAULT_PROFILE in .env |
| DB errors | Delete letters.db and restart |
| Import errors | Run `uv sync` |

## URLs

- **Application**: http://localhost:8000
- **FRBSF Source**: https://www.frbsf.org/research-and-insights/publications/economic-letter/
- **API Docs**: http://localhost:8000/docs (FastAPI auto-generated)

## Support Files

- `README.md` - Full documentation
- `USAGE.md` - User guide
- `DEPLOYMENT.md` - EC2 deployment
- `PROJECT_SUMMARY.md` - Implementation details

## Key Features

✅ Browse FRBSF economic letters
✅ AI-powered Q&A with Claude Sonnet
✅ Persistent question history
✅ Fetch new and historical letters
✅ Link to original publications
✅ Delete unwanted questions

## Tech Stack

- **Backend**: FastAPI + Python 3.11
- **Frontend**: VueJS 3 + Vuetify 3
- **Database**: SQLite
- **AI**: AWS Bedrock (Claude Sonnet)
- **Tools**: UV package manager
