from fastapi import FastAPI

from app.database import Base, engine
from app.routers import customers

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Customer API",
    description="A CRUD API for managing customers, built with FastAPI, Pydantic, and SQLAlchemy.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(customers.router)


@app.get("/health", tags=["Health"], summary="Health check")
def health_check():
    return {"status": "ok"}
