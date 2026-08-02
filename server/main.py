from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middlewares.exception_handlers import catch_exception_middleware
from routes.ask_question import router as ask_router
from routes.upload_pdfs import router as upload_router


app = FastAPI(
    title="Medical Assistant API",
    description="API for an AI-powered medical document assistant.",
)


# Allow frontend applications to communicate with the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception-handling middleware.
app.middleware("http")(catch_exception_middleware)


# Register API routes.
app.include_router(upload_router)
app.include_router(ask_router)


@app.get("/")
def health_check():
    """Simple endpoint to verify that the API is running."""
    return {
        "status": "running",
        "message": "Medical Assistant API is available.",
    }