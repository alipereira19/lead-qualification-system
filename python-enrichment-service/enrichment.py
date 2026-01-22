import httpx
from bs4 import BeautifulSoup
from typing import Tuple
import re


async def discover_website(company_name: str) -> str:
    if not company_name:
        return ""
    
    clean_name = re.sub(r'[^\w\s]', '', company_name).strip()
    
    common_domains = [
        f"https://www.{clean_name.lower().replace(' ', '')}.com",
        f"https://{clean_name.lower().replace(' ', '')}.com",
        f"https://www.{clean_name.lower().replace(' ', '-')}.com",
    ]
    
    async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
        for domain in common_domains:
            try:
                response = await client.head(domain)
                if response.status_code < 400:
                    return domain
            except:
                continue
    
    return ""


async def fetch_company_info(website: str) -> str:
    if not website:
        return "No website available for enrichment."
    
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(website)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            info_parts = []
            
            title = soup.find('title')
            if title:
                info_parts.append(f"Title: {title.get_text().strip()}")
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                info_parts.append(f"Description: {meta_desc['content'].strip()}")
            
            h1_tags = soup.find_all('h1', limit=3)
            if h1_tags:
                headings = [h.get_text().strip() for h in h1_tags if h.get_text().strip()]
                if headings:
                    info_parts.append(f"Main headings: {', '.join(headings)}")
            
            about_link = soup.find('a', href=re.compile(r'about', re.I))
            if about_link:
                info_parts.append("Has about page: Yes")
            
            if info_parts:
                return " | ".join(info_parts)
            else:
                return f"Website accessible at {website}, but limited content extracted."
                
    except httpx.TimeoutException:
        return f"Website {website} timed out during fetch."
    except httpx.HTTPStatusError as e:
        return f"Website returned error: {e.response.status_code}"
    except Exception as e:
        return f"Could not fetch website info: {str(e)}"


async def enrich_company(company_name: str, website: str) -> Tuple[str, str]:
    enriched_website = website
    if not website:
        enriched_website = await discover_website(company_name)
    
    company_info = await fetch_company_info(enriched_website)
    
    return enriched_website, company_info
