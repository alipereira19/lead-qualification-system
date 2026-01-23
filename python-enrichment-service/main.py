from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging

from schemas import LeadRequest, EnrichmentResponse, ErrorResponse
from enrichment import enrich_company
from ai_service import configure_gemini, analyze_lead

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lead Enrichment Service",
    description="Lead qualification API for ABC Company",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not found in environment.")
    else:
        configure_gemini(api_key)
        logger.info("Gemini API configured successfully")


def normalize_data(lead: LeadRequest) -> dict:
    return {
        "fullName": lead.fullName.strip(),
        "email": lead.email.lower().strip(),
        "companyName": lead.companyName.strip(),
        "website": lead.website.strip() if lead.website else "",
        "country": lead.country.strip(),
        "leadSource": lead.leadSource.strip(),
        "budget": lead.budget.strip(),
        "notes": lead.notes.strip() if lead.notes else "",
        "consent": lead.consent,
        "rowNumber": lead.rowNumber
    }


@app.get("/")
async def root():
    return {"status": "healthy", "service": "Lead Enrichment Service"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/enrich", response_model=EnrichmentResponse)
async def enrich_lead(lead: LeadRequest):
    logger.info(f"Received lead for enrichment: {lead.companyName}")
    
    try:
        normalized = normalize_data(lead)
        logger.info(f"Normalized email: {normalized['email']}")
        
        enriched_website, company_info = await enrich_company(
            company_name=normalized['companyName'],
            website=normalized['website']
        )
        logger.info(f"Enriched website: {enriched_website}")
        
        ai_analysis = await analyze_lead(
            company_name=normalized['companyName'],
            company_info=company_info,
            lead_source=normalized['leadSource'],
            budget=normalized['budget'],
            notes=normalized['notes'],
            country=normalized['country']
        )
        logger.info(f"AI Score: {ai_analysis.leadScore}")
        
        error_msg = None
        if ai_analysis.reasoning.startswith("Error:") or ai_analysis.reasoning.startswith("JSON parsing error:"):
            error_msg = ai_analysis.reasoning
        
        response = EnrichmentResponse(
            status="success" if not error_msg else "partial",
            normalizedEmail=normalized['email'],
            enrichedWebsite=enriched_website,
            companyInfo=company_info,
            aiSummary=ai_analysis.companySummary,
            aiFitScore=ai_analysis.leadScore,
            aiRecommendation=ai_analysis.recommendation,
            aiReasoning=ai_analysis.reasoning,
            errorMessage=error_msg
        )
        
        logger.info(f"Successfully enriched lead: {normalized['companyName']}")
        return response
        
    except Exception as e:
        logger.error(f"Error enriching lead: {str(e)}")
        return EnrichmentResponse(
            status="error",
            normalizedEmail=lead.email.lower().strip() if lead.email else "",
            enrichedWebsite="",
            companyInfo="",
            aiSummary="",
            aiFitScore=0,
            aiRecommendation="Manual review required",
            aiReasoning="",
            errorMessage=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
