from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import sheets, release_plans
from app.models.database import Base
from app.db.database import engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(sheets.router, prefix="/api/v1/sheets")
app.include_router(release_plans.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Google Sheets Integration Backend Running"} 