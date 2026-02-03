# Lead Qualification System

AI-powered automation system for intelligent lead qualification and routing.

## What it does

1. Collects leads through a Google Form
2. Validates, normalizes, and deduplicates data
3. Enriches company data via web scraping
4. Uses Google Gemini AI to analyze fit and score leads (0-100)
5. Routes leads based on score: Hot (≥70), Warm (40-69), Cold (<40)
6. Automatically schedules follow-ups and drafts emails

## Architecture

```
Google Form → Google Sheets → n8n Workflow → Python Service → AI Analysis
                                    ↓
                            Route by Score
                    ┌───────────┼───────────┐
                Hot Lead    Warm Lead    Cold Lead
                    ↓           ↓           ↓
            Schedule Call   Set Reminder   Done
                    ↓           ↓
              Send Email   Draft Email
```

## Project Structure

```
├── python-enrichment-service/
│   ├── main.py              # FastAPI server with enrichment endpoint
│   ├── schemas.py           # Pydantic data validation models
│   ├── enrichment.py        # Company website discovery & scraping
│   ├── ai_service.py        # Google Gemini AI integration
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # API keys (not in repo)
├── docs/
│   └── WRITEUP.md           # Technical decisions & architecture
├── Lead_Qualification_System.json  # n8n workflow export
└── requirements.txt         # Root dependencies
```

## Setup

### 1. Python Service

```bash
cd python-enrichment-service
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # Linux/Mac
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

```bash
ngrok http 8000
```

Copy the forwarding URL (e.g., `https://xxx.ngrok-free.app`)

### 3. n8n Workflow

1. Create a new workflow in n8n
2. Configure Google Sheets, Calendar, and Gmail credentials
3. Set up the workflow nodes (see docs/WORKFLOW.md)
4. Update the HTTP Request URL with your ngrok URL + `/enrich`
5. Activate the workflow

### 4. Google Form

Create a form with these fields:
- Full Name (required)
- Email Address (required)
- Company Name (required)
- Company Website (optional)
- Country (required)
- Lead Source (required)
- Estimated Budget (required)
- Notes (optional)
- Consent to Contact (required)

Link it to a Google Sheet with additional columns:
- Normalized Email
- Enrichment Status
- Enriched Website
- AI Summary
- AI Fit Score
- AI Recommendation
- Error Logs

## API Endpoint

**POST /enrich**

Request:
```json
{
  "fullName": "John Doe",
  "email": "john@company.com",
  "companyName": "Company Inc",
  "companyWebsite": "",
  "country": "United States",
  "leadSource": "Website",
  "estimatedBudget": "$10,000-$25,000",
  "notes": "",
  "consent": true
}
```

Response:
```json
{
  "status": "success",
  "normalizedEmail": "john@company.com",
  "enrichedWebsite": "https://company.com",
  "aiSummary": "Company Inc is a mid-sized e-commerce retailer...",
  "aiFitScore": 75,
  "aiRecommendation": "Schedule discovery call within 48 hours...",
  "errorMessage": null
}
```

## Technologies

- **Backend:** Python, FastAPI, Pydantic
- **AI:** Google Gemini 2.5 Flash
- **Automation:** n8n
- **Integrations:** Google Sheets, Google Calendar, Gmail
- **Web Scraping:** httpx, BeautifulSoup4

## Testing

1. Start the Python server (`python main.py`)
2. Start ngrok (`ngrok http 8000`)
3. Activate the n8n workflow
4. Submit a test lead (try "Warby Parker" or "Allbirds" for high scores)
5. Check Google Sheets, Calendar, and Gmail for results

## Notes

- Duplicates are detected by normalized email address
- Failed enrichments are marked with error status and flagged for manual review
- AI scoring uses weighted categories: industry fit (30%), budget (25%), lead source (20%), growth potential (25%)
- Hot leads (≥70) get immediate calendar events and emails
- Warm leads (40-69) get reminder events and draft emails for review
