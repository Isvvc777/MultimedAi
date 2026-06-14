from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "ok", "message": f"{settings.api_title} is running"}

# Include API routers
from app.routers import router as api_router
app.include_router(api_router)
