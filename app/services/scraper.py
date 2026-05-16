import httpx
from bs4 import BeautifulSoup
from app.schemas import ScrapeResponse, JobSearchResult
import re
from urllib.parse import quote_plus


async def scrape_linkedin_job(url: str) -> ScrapeResponse:
    """
    Scrape job details from a LinkedIn job posting URL.
    
    Uses the public page (no login required for some listings).
    LinkedIn may block requests - this works for publicly accessible job posts.
    """
    if not _is_valid_linkedin_url(url):
        raise ValueError("Invalid LinkedIn job URL")

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

    job_title = _extract_title(soup)
    company = _extract_company(soup)
    location = _extract_location(soup)
    description = _extract_description(soup)
    salary = _extract_salary(soup)

    return ScrapeResponse(
        job_title=job_title,
        company=company,
        location=location,
        job_description=description,
        salary_range=salary,
    )


def _is_valid_linkedin_url(url: str) -> bool:
    pattern = r"^https?://([a-z]{2,3}\.)?linkedin\.com/jobs/view/.+"
    return bool(re.match(pattern, url))


def _extract_title(soup: BeautifulSoup) -> str | None:
    # Try multiple selectors LinkedIn uses
    selectors = [
        "h1.top-card-layout__title",
        "h1.topcard__title",
        "h1[class*='job-title']",
        "h1",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return None


def _extract_company(soup: BeautifulSoup) -> str | None:
    selectors = [
        "a.topcard__org-name-link",
        "a[class*='company-name']",
        "span.topcard__flavor",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return None


def _extract_location(soup: BeautifulSoup) -> str | None:
    selectors = [
        "span.topcard__flavor--bullet",
        "span[class*='location']",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return None


def _extract_description(soup: BeautifulSoup) -> str | None:
    selectors = [
        "div.show-more-less-html__markup",
        "div[class*='description']",
        "section[class*='description']",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            text = el.get_text(separator="\n", strip=True)
            # Limit description length
            return text[:3000] if text else None
    return None


def _extract_salary(soup: BeautifulSoup) -> str | None:
    selectors = [
        "div[class*='salary']",
        "span[class*='compensation']",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return None


async def search_linkedin_jobs(role: str, location: str = "", page: int = 0) -> list[JobSearchResult]:
    """
    Search LinkedIn public job listings by role/keyword.
    Uses LinkedIn's public job search page (no login required).
    """
    keywords = quote_plus(role)
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

    return results
