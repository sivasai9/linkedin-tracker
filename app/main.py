from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.routers import scraper


app = FastAPI(
    title="LinkedIn Job Tracker",
    description="Search and fetch latest job listings from LinkedIn.",
    version="1.0.0",
)

app.include_router(scraper.router)

TEMPLATES_DIR = Path(__file__).parent / "templates"


@app.get("/", response_class=HTMLResponse)
async def root():
    html_file = TEMPLATES_DIR / "index.html"
    return html_file.read_text(encoding="utf-8")


@app.get("/health")
async def health():
    return {"status": "healthy"}
