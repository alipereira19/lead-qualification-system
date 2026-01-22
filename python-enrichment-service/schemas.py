from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class LeadSource(str, Enum):
    WEBSITE = "Website"
    REFERRAL = "Referral"
    LINKEDIN = "LinkedIn"
    EVENT = "Event"
    OTHER = "Other"


class LeadRequest(BaseModel):
    fullName: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    companyName: str = Field(..., min_length=1)
    website: Optional[str] = ""
    country: str = Field(..., min_length=1)
    leadSource: str = Field(..., min_length=1)
    budget: str = Field(..., min_length=1)
    notes: Optional[str] = ""
    consent: bool = True
    rowNumber: Optional[int] = None


class AIAnalysis(BaseModel):
    companySummary: str
    fitAssessment: str
    leadScore: int = Field(..., ge=0, le=100)
    recommendation: str
    reasoning: str


class EnrichmentResponse(BaseModel):
    status: str = "success"
    normalizedEmail: str
    enrichedWebsite: str
    companyInfo: Optional[str] = ""
    aiSummary: str
    aiFitScore: int
    aiRecommendation: str
    aiReasoning: str
    errorMessage: Optional[str] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    errorMessage: str
    normalizedEmail: Optional[str] = None
