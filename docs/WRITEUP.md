# Technical Write-up

## Architecture Overview

The system follows an event-driven architecture with intelligent routing:

```
Google Form → Google Sheets → n8n → Python Service → AI Analysis → Score Routing
```

When someone submits a lead:
1. Google Forms writes to Sheets
2. n8n detects the new row and checks for duplicates
3. Python service enriches company data and calls Gemini AI
4. n8n routes the lead based on AI score (Hot/Warm/Cold)
5. Automated actions are triggered (calendar events, emails)

I kept the architecture simple intentionally. The exam mentioned this is for "small and mid-sized e-commerce businesses" - they don't need Kubernetes or complex microservices. A single Python service handles all enrichment and AI logic.

## Tool Choices

### n8n over Make

I chose n8n because:
- Self-hosted, no operation limits
- Code nodes for custom JavaScript logic
- Free forever (not just free tier)
- Easy integration with Google services via OAuth

Make would've worked, but the 1000 operations/month limit felt restrictive for testing and production use.

### FastAPI over Flask

FastAPI handles async natively. Since we make HTTP calls to websites and the Gemini API concurrently, async performance matters. Pydantic validation is built-in, saving boilerplate code.

### Google Sheets as Database

For a lead system handling hundreds of leads per month, Sheets is sufficient:
- Free and familiar to sales teams
- Easy to share and collaborate
- Built-in filtering and charts
- Good enough for this scale

For thousands of leads, I'd migrate to PostgreSQL or similar.

### Google Gemini 2.5 Flash

Selected for structured JSON responses with good speed. The `max_output_tokens=4000` setting ensures complete responses without truncation.

## AI Strategy

### Prompt Design

The prompt provides clear context about ABC Company's target market (small/mid-sized e-commerce). It requests structured outputs:

1. **Company Summary** - Brief description of what the company does
2. **Fit Assessment** - How well they match ABC's ideal customer profile
3. **Lead Score (0-100)** - Weighted scoring across categories
4. **Recommendation** - Specific next action for sales team
5. **Reasoning** - Explanation of the score breakdown

### Scoring Weights

Breaking the score into weighted categories produces more consistent results:
- Industry Fit: 30 points
- Budget Alignment: 25 points
- Lead Source Quality: 20 points
- Growth Potential: 25 points

### Response Parsing

AI responses are extracted using regex to handle markdown code blocks:

```python
json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response_text)
if json_match:
    response_text = json_match.group(1).strip()
```

Every response goes through Pydantic validation:

```python
class AIAnalysis(BaseModel):
    companySummary: str
    fitAssessment: str
    leadScore: int = Field(ge=0, le=100)
    recommendation: str
    reasoning: str
```

If malformed or missing fields, we return a fallback response (score 50, "manual review required").

## Lead Routing Logic

After AI analysis, n8n routes leads based on score:

| Score Range | Classification | Actions |
|-------------|---------------|---------|
| ≥70 | Hot Lead | Schedule call (next day) + Send email |
| 40-69 | Warm Lead | Set reminder (3 days) + Draft email |
| <40 | Cold Lead | No action, stored for future reference |

### Consent Check

Before routing, the workflow verifies `consent === true`. Leads without consent are not contacted, only stored.

## Error Handling

### Timeouts

HTTP calls to company websites use a 5-second timeout:

```python
async with httpx.AsyncClient(timeout=5.0) as client:
    response = await client.head(domain)
```

### AI Failures

Multiple failure modes are handled:
- Empty response → neutral score (50), flag for manual review
- JSON parse error → same fallback, error logged
- API quota exceeded → same graceful degradation

The lead is always recorded; it just won't have AI analysis until manually retried.

### Empty Response Detection

```python
if not response_text:
    return AIAnalysis(
        companySummary=f"Could not analyze {company_name}...",
        leadScore=50,
        recommendation="Manual review required."
    )
```

### Duplicates

n8n checks for existing emails before processing. Duplicate submissions are marked as "DUPLICATE" and skipped.

## n8n Workflow Structure

```
Google Sheets Trigger
        ↓
Get All Rows (for duplicate check)
        ↓
Code in JavaScript (normalize, detect duplicates)
        ↓
    IF: Duplicate?
    ├── Yes → Update Row (mark duplicate)
    └── No → HTTP Request (call enrichment API)
                    ↓
            IF: API OK?
            ├── No → Error Log
            └── Yes → Update Row (save results)
                            ↓
                    IF: Has Consent?
                    ├── No → Done (No Consent)
                    └── Yes → Switch: Route by Score
                                ├── Hot → Schedule Call → Send Email
                                ├── Warm → Set Reminder → Draft Email
                                └── Cold → Done (Cold)
```

## Integrations

### Google Calendar

Hot leads trigger an event creation for the next business day:
- Title: "Follow up: {Company Name}"
- Duration: 30 minutes
- Description: Lead details and AI recommendation

Warm leads get a reminder event 3 days out.

### Gmail

Hot leads receive an automatic email thanking them for their interest.
Warm leads get a draft email created for manual review and sending.

## What I'd Improve

Given more time:

1. **Retry logic** - Add exponential backoff for transient API errors
2. **Better company discovery** - Integrate a company database API (Clearbit, Hunter.io)
3. **Webhook trigger** - Replace polling with Google Apps Script instant trigger
4. **Bulk import** - CSV upload for existing lead lists
5. **Dashboard** - Web UI showing lead pipeline, score distribution, conversion rates
6. **CRM integration** - Push qualified leads to Salesforce or HubSpot
7. **Email templates** - Customizable templates based on industry/score

## What Went Well

- End-to-end flow works reliably
- Deduplication prevents double-processing
- AI scoring is consistent and explainable
- Score-based routing automates follow-up prioritization
- Calendar/email integration saves manual work
- Error handling ensures no leads are lost
- Easy to set up and run locally
