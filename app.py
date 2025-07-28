from fastapi import FastAPI, Query, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Worker Search API", version="1.0.0", description="API to search and find recommended workers")

# Pydantic models for structured responses
class Worker(BaseModel):
    id: int
    name: str
    location: str
    available_time: str
    rating: float
    hourly_rate: float
    skills: List[str]
    experience_years: int
    description: str

class WorkerSearchResponse(BaseModel):
    workers: List[Worker]
    total_found: int
    search_query: str

# Sample worker data (in production, this would come from a database)
SAMPLE_WORKERS = [
    Worker(
        id=1,
        name="John Smith",
        location="Lagos, Nigeria",
        available_time="9:00 AM - 5:00 PM",
        rating=4.8,
        hourly_rate=25.0,
        skills=["Web Development", "Python", "FastAPI"],
        experience_years=5,
        description="Experienced full-stack developer specializing in Python and modern web frameworks."
    ),
    Worker(
        id=2,
        name="Sarah Johnson",
        location="Abuja, Nigeria",
        available_time="10:00 AM - 6:00 PM",
        rating=4.9,
        hourly_rate=30.0,
        skills=["Data Science", "Machine Learning", "Python"],
        experience_years=7,
        description="Data scientist with expertise in ML algorithms and statistical analysis."
    ),
    Worker(
        id=3,
        name="Michael Chen",
        location="Port Harcourt, Nigeria",
        available_time="8:00 AM - 4:00 PM",
        rating=4.7,
        hourly_rate=22.0,
        skills=["Mobile Development", "React Native", "JavaScript"],
        experience_years=4,
        description="Mobile app developer creating cross-platform applications."
    ),
    Worker(
        id=4,
        name="Aisha Mohammed",
        location="Lagos, Nigeria",
        available_time="1:00 PM - 9:00 PM",
        rating=4.9,
        hourly_rate=35.0,
        skills=["UI/UX Design", "Graphic Design", "Figma"],
        experience_years=6,
        description="Creative designer with a passion for user-centered design solutions."
    ),
    Worker(
        id=5,
        name="David Okafor",
        location="Kano, Nigeria",
        available_time="9:00 AM - 5:00 PM",
        rating=4.6,
        hourly_rate=20.0,
        skills=["Digital Marketing", "SEO", "Content Creation"],
        experience_years=3,
        description="Digital marketing specialist helping businesses grow their online presence."
    )
]

@app.on_event("startup")
async def startup_event():
    logger.info("Worker Search API is starting up...")

@app.on_event("shutdown") 
async def shutdown_event():
    logger.info("Worker Search API is shutting down...")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Received {request.method} request to {request.url}")
    response = await call_next(request)
    logger.info(f"Returning {response.status_code}")
    return response

@app.get("/")
@app.head("/")
def read_root():
    logger.info("Root endpoint called")
    return {
        "message": "Worker Search API", 
        "status": "ok", 
        "service": "running",
        "endpoints": {
            "search_workers": "/workers/search",
            "get_worker": "/workers/{worker_id}",
            "health_check": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
@app.head("/health")
def health_check():
    return {"status": "healthy", "service": "active", "workers_available": len(SAMPLE_WORKERS)}

@app.get("/workers/search", response_model=WorkerSearchResponse)
def search_workers(
    location: Optional[str] = Query(None, description="Filter by location"),
    skill: Optional[str] = Query(None, description="Filter by skill"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    max_rate: Optional[float] = Query(None, ge=0, description="Maximum hourly rate"),
    min_experience: Optional[int] = Query(None, ge=0, description="Minimum years of experience")
):
    """
    Search for workers based on various criteria:
    - location: Filter by worker location
    - skill: Filter by specific skill
    - min_rating: Minimum rating (0-5)
    - max_rate: Maximum hourly rate
    - min_experience: Minimum years of experience
    """
    
    filtered_workers = SAMPLE_WORKERS.copy()
    search_terms = []
    
    # Filter by location
    if location:
        filtered_workers = [w for w in filtered_workers if location.lower() in w.location.lower()]
        search_terms.append(f"location: {location}")
    
    # Filter by skill
    if skill:
        filtered_workers = [w for w in filtered_workers if any(skill.lower() in s.lower() for s in w.skills)]
        search_terms.append(f"skill: {skill}")
    
    # Filter by minimum rating
    if min_rating is not None:
        filtered_workers = [w for w in filtered_workers if w.rating >= min_rating]
        search_terms.append(f"min_rating: {min_rating}")
    
    # Filter by maximum rate
    if max_rate is not None:
        filtered_workers = [w for w in filtered_workers if w.hourly_rate <= max_rate]
        search_terms.append(f"max_rate: {max_rate}")
    
    # Filter by minimum experience
    if min_experience is not None:
        filtered_workers = [w for w in filtered_workers if w.experience_years >= min_experience]
        search_terms.append(f"min_experience: {min_experience}")
    
    # Sort by rating (highest first)
    filtered_workers.sort(key=lambda x: x.rating, reverse=True)
    
    search_query = ", ".join(search_terms) if search_terms else "all workers"
    
    return WorkerSearchResponse(
        workers=filtered_workers,
        total_found=len(filtered_workers),
        search_query=search_query
    )

@app.get("/workers/{worker_id}", response_model=Worker)
def get_worker(worker_id: int):
    """Get detailed information about a specific worker by ID"""
    worker = next((w for w in SAMPLE_WORKERS if w.id == worker_id), None)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker

@app.get("/workers/recommended", response_model=WorkerSearchResponse)
def get_recommended_workers(limit: int = Query(3, ge=1, le=10, description="Number of workers to return")):
    """Get top recommended workers based on rating"""
    # Sort by rating and return top workers
    recommended = sorted(SAMPLE_WORKERS, key=lambda x: x.rating, reverse=True)[:limit]
    
    return WorkerSearchResponse(
        workers=recommended,
        total_found=len(recommended),
        search_query=f"top {limit} recommended workers"
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
