from pydantic import BaseModel
from typing import Optional


class JobSearchRequest(BaseModel):
    role: str
    company: Optional[str] = ""
    location: Optional[str] = ""
    page: int = 0


class JobSearchResult(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    posted_date: Optional[str] = None
    linkedin_url: Optional[str] = None
