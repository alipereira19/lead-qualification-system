# Python Enrichment Service

This service handles lead data normalization, company enrichment, and AI-powered lead scoring.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your API key:
```
GEMINI_API_KEY=your_api_key_here
```

4. Run the server:
```bash
python main.py
```

5. Expose with ngrok:
```bash
ngrok http 8000
```

## API Endpoints

### POST /enrich
Receives lead data, normalizes it, enriches company info, and returns AI analysis.

**Request Body:**
```json
{
  "fullName": "John Doe",
  "email": "john@company.com",
  "companyName": "Acme Inc",
  "website": "",
  "country": "USA",
  "leadSource": "Website",
  "budget": "$5k-$20k",
  "notes": "Interested in AI support",
  "consent": true
}
```

**Response:**
```json
{
  "status": "success",
  "normalizedEmail": "john@company.com",
  "enrichedWebsite": "https://acme.com",
  "aiSummary": "Acme Inc is a...",
  "aiFitScore": 75,
  "aiRecommendation": "Schedule demo call"
}
```
