from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.extraction import router as extraction_router

app = FastAPI(
    title="Feature Extraction Service",
    description="Service for extracting sEMG features (Time Domain, Frequency Domain).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(extraction_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "feature-extraction-service"}
