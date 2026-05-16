from fastapi import APIRouter, HTTPException
from app.models import Reminder
from app.schemas import ReminderCreate, ReminderResponse
from beanie import PydanticObjectId
from datetime import datetime

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.post("/", response_model=ReminderResponse, status_code=201)
async def create_reminder(reminder: ReminderCreate):
    new_reminder = Reminder(**reminder.model_dump())
    await new_reminder.insert()
    return _to_response(new_reminder)


@router.get("/", response_model=list[ReminderResponse])
async def list_reminders(include_completed: bool = False):
    query = {} if include_completed else {"is_completed": False}
    reminders = await Reminder.find(query).sort("+reminder_date").to_list()
    return [_to_response(r) for r in reminders]


@router.get("/due", response_model=list[ReminderResponse])
async def get_due_reminders():
    """Get all reminders that are due (reminder_date <= now and not completed)."""
    now = datetime.utcnow()
    reminders = await Reminder.find(
        {"reminder_date": {"$lte": now}, "is_completed": False}
    ).to_list()
    return [_to_response(r) for r in reminders]


@router.get("/job/{job_id}", response_model=list[ReminderResponse])
async def get_reminders_for_job(job_id: str):
    reminders = await Reminder.find({"job_application_id": job_id}).to_list()
    return [_to_response(r) for r in reminders]


@router.patch("/{reminder_id}/complete", response_model=ReminderResponse)
async def complete_reminder(reminder_id: str):
    reminder = await Reminder.get(PydanticObjectId(reminder_id))
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    await reminder.set({"is_completed": True})
    return _to_response(reminder)


@router.delete("/{reminder_id}", status_code=204)
async def delete_reminder(reminder_id: str):
    reminder = await Reminder.get(PydanticObjectId(reminder_id))
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    await reminder.delete()


def _to_response(reminder: Reminder) -> ReminderResponse:
    return ReminderResponse(
        id=str(reminder.id),
        job_application_id=reminder.job_application_id,
        reminder_date=reminder.reminder_date,
        message=reminder.message,
        is_completed=reminder.is_completed,
        created_at=reminder.created_at,
    )
