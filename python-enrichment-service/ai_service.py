import google.generativeai as genai
import json
import os
from schemas import AIAnalysis


ABC_COMPANY_CONTEXT = """
ABC Company builds AI-powered customer support solutions designed for small and mid-sized 
e-commerce businesses. The platform helps online retailers automate first-line support, 
reduce response times, and improve customer satisfaction by combining conversational AI 
with human-in-the-loop workflows.

Target customers:
- Small to mid-sized e-commerce businesses
- Online retailers
- Companies looking to automate customer support
- Businesses wanting to reduce support response times
"""


def configure_gemini(api_key: str):
    genai.configure(api_key=api_key)


def build_analysis_prompt(
    company_name: str,
    company_info: str,
    lead_source: str,
    budget: str,
    notes: str,
    country: str
) -> str:
    
    return f"""You are a lead qualification AI for ABC Company.

{ABC_COMPANY_CONTEXT}

Analyze the following lead and provide a structured assessment:

LEAD INFORMATION:
- Company Name: {company_name}
- Country: {country}
- Lead Source: {lead_source}
- Estimated Budget: {budget}
- Additional Notes: {notes or 'None provided'}
- Company Website Info: {company_info or 'No website information available'}

TASK:
1. Summarize what this company appears to do (2-3 sentences)
2. Assess how well this lead fits ABC Company's target market
3. Provide a lead quality score from 0-100 based on:
   - Fit with e-commerce/retail industry (0-30 points)
   - Budget alignment (0-25 points)
   - Lead source quality (0-20 points)
   - Overall potential (0-25 points)
4. Recommend a specific next action

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "companySummary": "Brief 2-3 sentence summary of the company",
    "fitAssessment": "How well they fit as a potential customer",
    "leadScore": 75,
    "recommendation": "Specific next action to take",
    "reasoning": "Brief explanation of score and recommendation"
}}

IMPORTANT: Respond ONLY with valid JSON, no additional text."""


async def analyze_lead(
    company_name: str,
    company_info: str,
    lead_source: str,
    budget: str,
    notes: str,
    country: str
) -> AIAnalysis:
    
    prompt = build_analysis_prompt(
        company_name=company_name,
        company_info=company_info,
        lead_source=lead_source,
        budget=budget,
        notes=notes,
        country=country
    )
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=500,
            )
        )
        
        response_text = response.text.strip()
        
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        response_text = response_text.strip()
        
        parsed = json.loads(response_text)
        analysis = AIAnalysis(**parsed)
        
        return analysis
        
    except json.JSONDecodeError as e:
        return AIAnalysis(
            companySummary=f"Could not analyze {company_name} - AI response was not valid JSON.",
            fitAssessment="Unable to assess fit due to processing error.",
            leadScore=50,
            recommendation="Manual review required - AI analysis failed.",
            reasoning=f"JSON parsing error: {str(e)}"
        )
    except Exception as e:
        
        import logging
        logging.error(f"AI Service Error: {str(e)}")
        return AIAnalysis(
            companySummary=f"Error analyzing {company_name}.",
            fitAssessment="Unable to assess.",
            leadScore=50,
            recommendation="Manual review required.",
            reasoning=f"Error: {str(e)}"
        )
