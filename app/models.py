from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ApplicationStatus(str, Enum):
    SAVED = "saved"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class JobApplication(Document):
    job_title: str
    company: str
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_description: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.SAVED
    date_saved: datetime = Field(default_factory=datetime.utcnow)
    date_applied: Optional[datetime] = None
    salary_range: Optional[str] = None
    notes: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

    class Settings:
        name = "job_applications"


class Reminder(Document):
    job_application_id: str
    reminder_date: datetime
    message: str
    is_completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "reminders"
