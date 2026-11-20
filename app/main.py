
from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Drive-to-Text",
    description="Extract text from Google Drive PDFs and images using PDF parsing and OCR.",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Drive-to-Text!",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
