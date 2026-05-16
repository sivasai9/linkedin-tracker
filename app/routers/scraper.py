from fastapi import APIRouter, HTTPException
from app.schemas import JobSearchRequest, JobSearchResult
from app.services.scraper import search_linkedin_jobs

router = APIRouter(prefix="/scraper", tags=["Scraper"])


@router.post("/search", response_model=list[JobSearchResult])
async def search_jobs(request: JobSearchRequest):
    """Search LinkedIn for latest job listings by role/keyword."""
    try:
        results = await search_linkedin_jobs(
            role=request.role,
            location=request.location or "",
            page=request.page,
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to search LinkedIn jobs. Error: {str(e)}",
        )
