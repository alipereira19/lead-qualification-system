# Technical Write-up

## Architecture Overview

The system follows a simple event-driven architecture:


Google Form → Google Sheets → n8n → Python Service → Google Sheets


When someone submits a lead, Google Forms writes to Sheets, n8n picks it up, calls our Python service for enrichment, and updates the row with AI analysis.

I kept things simple on purpose. The exam mentioned this is for "small and mid-sized e-commerce businesses" - they don't need Kubernetes or a complex microservices setup. A single Python service handles everything.

## Tool Choices

### n8n over Make

I went with n8n because:
- Runs locally, no account limits
- Code nodes let me write custom logic
- Free forever, not just free tier

Make would've worked too, but the 1000 operations/month limit felt restrictive for testing.

### FastAPI over Flask

FastAPI handles async out of the box. Since we're making HTTP calls to websites and the Gemini API, async matters. Also, Pydantic validation saves a lot of boilerplate.

### Google Sheets as Database

For a lead qualification system handling maybe a few hundred leads per month, Sheets is fine. It's:
- Free
- Everyone knows how to use it
- Easy to share with sales teams
- Good enough for this use case

If this grew to thousands of leads, I'd move to a proper database.

## AI Strategy

### Prompt Design

The prompt gives Gemini clear context about ABC Company's target market. It asks for specific outputs:

1. Company summary
2. Fit assessment
3. Score from 0-100
4. Recommended action

Breaking the score into weighted categories (industry fit 30pts, budget 25pts, lead source 20pts, potential 25pts) gives more consistent results than asking for a single number.

### Response Validation

Every AI response goes through Pydantic validation:

```python
class AIAnalysis(BaseModel):
    companySummary: str
    fitAssessment: str
    leadScore: int = Field(ge=0, le=100)
    recommendation: str
    reasoning: str
```

If the AI returns malformed JSON or missing fields, we catch it and return a fallback response with score 50 and "manual review required."

## Error Handling

### Timeouts

HTTP calls to company websites have a 5-second timeout. Some sites are slow or don't respond at all. Rather than hang forever, we move on with whatever info we got.

```python
async with httpx.AsyncClient(timeout=5.0) as client:
    response = await client.head(domain)
```

### AI Failures

If Gemini returns an unexpected response or the API is down:
- Parse errors → neutral score (50), flag for manual review
- API errors → same fallback, error logged

The lead still gets recorded; it just won't have AI analysis until someone manually retries.

### Duplicates

The n8n workflow checks for existing emails before processing. If someone submits twice with the same email, the second submission gets marked as "DUPLICATE" and skipped.

## What I'd Improve

Given more time:

1. **Retry logic** - Right now if something fails, it fails. Would add exponential backoff for transient errors.

2. **Better company discovery** - Currently just guesses domains like `companyname.com`. Could add a proper search API.

3. **Webhook instead of polling** - n8n polls Sheets every minute. A Google Apps Script trigger would be instant.

4. **Bulk import** - CSV upload for importing existing lead lists.

5. **Dashboard** - Simple web UI showing lead pipeline and scores.

## What Went Well

- End-to-end flow works reliably
- Deduplication prevents double-processing
- AI scoring is consistent and explainable
- Easy to set up and run locally
