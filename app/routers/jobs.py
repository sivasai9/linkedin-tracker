from fastapi import APIRouter, HTTPException
from app.models import JobApplication, ApplicationStatus
from app.schemas import JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse
from beanie import PydanticObjectId
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobApplicationResponse, status_code=201)
async def create_job(job: JobApplicationCreate):
    application = JobApplication(**job.model_dump())
    await application.insert()
    return _to_response(application)


@router.get("/", response_model=list[JobApplicationResponse])
async def list_jobs(
    status: Optional[ApplicationStatus] = None,
    company: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
):
    query = {}
    if status:
        query["status"] = status
    if company:
        query["company"] = {"$regex": company, "$options": "i"}

    jobs = await JobApplication.find(query).skip(skip).limit(limit).to_list()
    return [_to_response(job) for job in jobs]


@router.get("/{job_id}", response_model=JobApplicationResponse)
async def get_job(job_id: str):
    application = await JobApplication.get(PydanticObjectId(job_id))
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")
    return _to_response(application)


@router.patch("/{job_id}", response_model=JobApplicationResponse)
async def update_job(job_id: str, update: JobApplicationUpdate):
    application = await JobApplication.get(PydanticObjectId(job_id))
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")

    update_data = update.model_dump(exclude_unset=True)

    # Auto-set date_applied when status changes to "applied"
    if update_data.get("status") == ApplicationStatus.APPLIED and not application.date_applied:
        update_data["date_applied"] = datetime.utcnow()

    await application.set(update_data)
    return _to_response(application)


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: str):
    application = await JobApplication.get(PydanticObjectId(job_id))
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")
    await application.delete()


@router.get("/stats/summary")
async def get_stats():
    total = await JobApplication.count()
    stats = {}
    for status in ApplicationStatus:
        count = await JobApplication.find({"status": status.value}).count()
        stats[status.value] = count
    return {"total": total, "by_status": stats}


def _to_response(app: JobApplication) -> JobApplicationResponse:
    return JobApplicationResponse(
        id=str(app.id),
        job_title=app.job_title,
        company=app.company,
        location=app.location,
        linkedin_url=app.linkedin_url,
        job_description=app.job_description,
        status=app.status,
        date_saved=app.date_saved,
        date_applied=app.date_applied,
        salary_range=app.salary_range,
        notes=app.notes,
        tags=app.tags,
    )
