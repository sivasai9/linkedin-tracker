import httpx
from bs4 import BeautifulSoup
from app.schemas import JobSearchResult
import re
from urllib.parse import quote_plus


async def search_linkedin_jobs(role: str, company: str = "", location: str = "", page: int = 0) -> list[JobSearchResult]:
    """
    Search LinkedIn public job listings by role/keyword.
    Uses LinkedIn's public job search page (no login required).
    If company is provided, it's included in the keywords and results are filtered to match.
    """
    search_terms = f"{role} {company}".strip() if company else role
    keywords = quote_plus(search_terms)
    location_param = quote_plus(location) if location else ""
    start = page * 25

    url = (
        f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords={keywords}&location={location_param}&start={start}"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    job_cards = soup.find_all("li")

    results = []
    for card in job_cards:
        try:
            title_el = card.find("h3", class_="base-search-card__title")
            company_el = card.find("h4", class_="base-search-card__subtitle")
            location_el = card.find("span", class_="job-search-card__location")
            date_el = card.find("time")
            link_el = card.find("a", class_="base-card__full-link")

            if not title_el:
                continue

            job_title = title_el.get_text(strip=True) if title_el else None
            company = company_el.get_text(strip=True) if company_el else None
            job_location = location_el.get_text(strip=True) if location_el else None
            posted_date = date_el.get("datetime") if date_el else None
            job_url = link_el.get("href") if link_el else None

            if job_title:
                results.append(JobSearchResult(
                    job_title=job_title,
                    company=company,
                    location=job_location,
                    posted_date=posted_date,
                    linkedin_url=job_url,
                ))
        except Exception:
            continue

    # Filter by company if specified
    if company:
        company_lower = company.lower()
        results = [
            r for r in results
            if r.company and company_lower in r.company.lower()
        ]

    return results
