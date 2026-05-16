from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models import ApplicationStatus


# --- Job Application Schemas ---

class JobApplicationCreate(BaseModel):
    job_title: str
    company: str
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_description: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.SAVED
    date_applied: Optional[datetime] = None
    salary_range: Optional[str] = None
    notes: Optional[str] = None
    tags: list[str] = []


class JobApplicationUpdate(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_description: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    date_applied: Optional[datetime] = None
    salary_range: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[list[str]] = None


class JobApplicationResponse(BaseModel):
    id: str
    job_title: str
    company: str
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_description: Optional[str] = None
    status: ApplicationStatus
    date_saved: datetime
    date_applied: Optional[datetime] = None
    salary_range: Optional[str] = None
    notes: Optional[str] = None
    tags: list[str] = []


# --- Reminder Schemas ---

class ReminderCreate(BaseModel):
    job_application_id: str
    reminder_date: datetime
    message: str


class ReminderResponse(BaseModel):
    id: str
    job_application_id: str
    reminder_date: datetime
    message: str
    is_completed: bool
    created_at: datetime


# --- Scraper Schemas ---

class ScrapeRequest(BaseModel):
    linkedin_url: str


class ScrapeResponse(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    job_description: Optional[str] = None
    salary_range: Optional[str] = None


# --- Job Search Schemas ---

class JobSearchRequest(BaseModel):
    role: str
    location: Optional[str] = ""
    page: int = 0


class JobSearchResult(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    posted_date: Optional[str] = None
    linkedin_url: Optional[str] = None
