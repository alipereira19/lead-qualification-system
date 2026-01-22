# Lead Qualification System

A lightweight system that captures leads, enriches company data, and uses AI to qualify and score them.

## What it does

1. Collects leads through a Google Form
2. Validates and normalizes the data
3. Finds company websites when missing
4. Uses Gemini to analyze fit and score leads
5. Stores everything in Google Sheets

## Project Structure

```
├── python-enrichment-service/
│   ├── main.py          # FastAPI server
│   ├── schemas.py       # Data validation
│   ├── enrichment.py    # Company discovery
│   ├── ai_service.py    # Gemini integration
│   └── requirements.txt
└── docs/
    └── WRITEUP.md       # Technical decisions
```

## Setup

### 1. Python Service

```bash
cd python-enrichment-service
python -m venv venv
venv\Scripts\activate      # This is for Windows
pip install -r requirements.txt
```

Create `.env` with your Gemini key:
```
GEMINI_API_KEY=your_key_here
```

Run the server:
```bash
python main.py
```

### 2. Expose with ngrok

In a new terminal:
```bash
ngrok http 8000
```

Copy the forwarding URL (e.g., `https://xxx.ngrok-free.app`)

### 3. n8n Workflow

1. Import the workflow or create manually
2. Configure Google Sheets credentials
3. Update the HTTP Request URL with your ngrok URL + `/enrich`
4. Activate the workflow

### 4. Google Form

Create a form with these fields:
- Full Name (required)
- Email Address (required)
- Company Name (required)
- Company Website
- Country (required)
- Lead Source (required)
- Estimated Budget (required)
- Notes
- Consent to Contact (required)

Link it to a Google Sheet with additional columns:
- Normalized Email
- Enrichment Status
- Enriched Website
- AI Summary
- AI Fit Score
- AI Recommendation
- Error Logs

## Testing

1. Start the Python server
2. Start ngrok
3. Activate the n8n workflow
4. Submit a test lead through the form
5. Check Google Sheets for the enrichment results

## Notes

- The system handles duplicates by checking email addresses
- Failed enrichments are marked with error status
- AI scoring considers industry fit, budget, and lead source
