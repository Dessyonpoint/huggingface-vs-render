from fastapi import FastAPI, Query, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Worker Search API", version="1.0.0", description="API to search and find recommended workers")

# Nigerian local job types
LOCAL_JOB_TYPES = [
    "Carpenter", "Plumber", "Electrician", "Welder", "Mason", "Painter", "Mechanic",
    "Generator Repair Technician", "Aluminum Fabricator", "POP Ceiling Installer",
    "CNG Technician", "Technician", "Cleaner", "Nanny", "Housekeeper", "Cook",
    "Laundry Services", "Security Guard", "Driver", "Tailor", "Hairdresser", "Barber",
    "Makeup Artist", "Event Decorator", "Photographer", "Vulcanizer", "Tiler",
    "Panel Beater", "AC Installer", "Refrigerator Repairer", "Phone Repair Technician",
    "Computer Repairer", "Solar Installer", "CCTV Installer", "Internet Technician",
    "Site Labourer", "Site Supervisor", "Scaffolder", "Plasterer", "POS Agent",
    "Dispatch Rider", "Market Delivery Agent", "Shoemaker", "Dry Cleaner",
    "Waste Collector"
]

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
    job_type: str
    phone: str
    verified: bool

class WorkerSearchResponse(BaseModel):
    workers: List[Worker]
    total_found: int
    search_query: str

# Generate sample worker data with Nigerian job types
def generate_sample_workers():
    nigerian_names = [
        "Adebayo Ogundimu", "Chioma Okafor", "Ibrahim Musa", "Fatima Abdullahi", 
        "Emeka Nwosu", "Blessing Okoro", "Yusuf Hassan", "Grace Adamu",
        "Kunle Ajayi", "Nkechi Okoye", "Aliyu Garba", "Patience Eze",
        "Tunde Bakare", "Mary Ogbonna", "Sani Umar", "Joy Anyanwu",
        "Femi Adewale", "Ngozi Okorie", "Murtala Yusuf", "Esther Oduya",
        "Ola Taiwo", "Amina Bello", "Chinedu Obi", "Kemi Adesola",
        "Usman Aliyu", "Rita Nnamdi", "Kabir Suleiman", "Folake Adebisi",
        "Ahmad Tijani", "Ifeoma Uzoma", "Garba Mohammed", "Funmi Ogunleye",
        "Salisu Yakubu", "Chinwe Ejiofor", "Bashir Abdullahi", "Doris Nwankwo",
        "Ismail Haruna", "Stella Okwu", "Nasir Ahmad", "Vivian Okafor"
    ]
    
    locations = ["Lagos, Nigeria", "Abuja, Nigeria"]
    
    time_slots = [
        "7:00 AM - 4:00 PM", "8:00 AM - 5:00 PM", "9:00 AM - 6:00 PM",
        "10:00 AM - 7:00 PM", "6:00 AM - 3:00 PM", "12:00 PM - 9:00 PM",
        "8:00 AM - 4:00 PM", "9:00 AM - 5:00 PM", "24/7 Available"
    ]
    
    phone_prefixes = ["080", "081", "070", "090", "091"]
    
    workers = []
    
    for i, job_type in enumerate(LOCAL_JOB_TYPES):
        for location in locations:
            worker_id = len(workers) + 1
            name = random.choice(nigerian_names)
            
            # Generate skills based on job type
            skills = [job_type]
            if "Repair" in job_type or "Technician" in job_type:
                skills.extend(["Troubleshooting", "Equipment Maintenance"])
            if job_type in ["Carpenter", "Mason", "Welder", "Tiler"]:
                skills.extend(["Construction", "Blueprint Reading"])
            if job_type in ["Hairdresser", "Barber", "Makeup Artist"]:
                skills.extend(["Customer Service", "Beauty Treatments"])
            if job_type in ["Driver", "Dispatch Rider"]:
                skills.extend(["Navigation", "Vehicle Maintenance"])
            if job_type in ["Cleaner", "Housekeeper", "Nanny"]:
                skills.extend(["Home Management", "Organization"])
            
            # Generate rates based on job type complexity
            if job_type in ["Generator Repair Technician", "Solar Installer", "CCTV Installer", "Site Supervisor"]:
                hourly_rate = random.uniform(35, 80)
            elif job_type in ["Electrician", "Plumber", "Mechanic", "AC Installer"]:
                hourly_rate = random.uniform(25, 60)
            elif job_type in ["Carpenter", "Welder", "Mason", "Painter", "Tiler"]:
                hourly_rate = random.uniform(20, 45)
            elif job_type in ["Photographer", "Event Decorator", "Makeup Artist"]:
                hourly_rate = random.uniform(30, 70)
            else:
                hourly_rate = random.uniform(15, 35)
            
            worker = Worker(
                id=worker_id,
                name=name,
                location=location,
                available_time=random.choice(time_slots),
                rating=round(random.uniform(3.5, 5.0), 1),
                hourly_rate=round(hourly_rate, 0),
                skills=skills,
                experience_years=random.randint(1, 15),
                description=f"Professional {job_type.lower()} with extensive experience in {location.split(',')[0]}. Reliable and skilled service provider.",
                job_type=job_type,
                phone=f"{random.choice(phone_prefixes)}{random.randint(10000000, 99999999)}",
                verified=random.choice([True, True, True, False])  # 75% verification rate
            )
            workers.append(worker)
    
    return workers

# Generate sample workers
SAMPLE_WORKERS = generate_sample_workers()

@app.on_event("startup")
async def startup_event():
    logger.info("Worker Search API is starting up...")
    logger.info(f"Loaded {len(SAMPLE_WORKERS)} workers across {len(LOCAL_JOB_TYPES)} job types")

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
        "total_workers": len(SAMPLE_WORKERS),
        "job_types_available": len(LOCAL_JOB_TYPES),
        "locations": ["Lagos, Nigeria", "Abuja, Nigeria"],
        "endpoints": {
            "search_workers": "/workers/search",
            "get_worker": "/workers/{worker_id}",
            "get_job_types": "/job-types",
            "health_check": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
@app.head("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "active", 
        "workers_available": len(SAMPLE_WORKERS),
        "job_types": len(LOCAL_JOB_TYPES)
    }

@app.get("/job-types")
def get_job_types():
    """Get all available job types"""
    return {
        "job_types": LOCAL_JOB_TYPES,
        "total_count": len(LOCAL_JOB_TYPES)
    }

@app.get("/workers/search", response_model=WorkerSearchResponse)
def search_workers(
    location: Optional[str] = Query(None, description="Filter by location (Lagos or Abuja)"),
    skill: Optional[str] = Query(None, description="Filter by skill"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    max_rate: Optional[float] = Query(None, ge=0, description="Maximum hourly rate"),
    min_experience: Optional[int] = Query(None, ge=0, description="Minimum years of experience"),
    verified_only: Optional[bool] = Query(False, description="Show only verified workers")
):
    """
    Search for workers based on various criteria:
    - location: Filter by worker location (Lagos or Abuja)
    - skill: Filter by specific skill
    - job_type: Filter by job type (e.g., Plumber, Electrician, etc.)
    - min_rating: Minimum rating (0-5)
    - max_rate: Maximum hourly rate
    - min_experience: Minimum years of experience
    - verified_only: Show only verified workers
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
    
    # Filter by job type
    if job_type:
        filtered_workers = [w for w in filtered_workers if job_type.lower() in w.job_type.lower()]
        search_terms.append(f"job_type: {job_type}")
    
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
    
    # Filter by verification status
    if verified_only:
        filtered_workers = [w for w in filtered_workers if w.verified]
        search_terms.append("verified_only: true")
    
    # Sort by rating (highest first), then by verification status
    filtered_workers.sort(key=lambda x: (x.rating, x.verified), reverse=True)
    
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
def get_recommended_workers(limit: int = Query(3, ge=1, le=20, description="Number of workers to return")):
    """Get top recommended workers based on rating and verification status"""
    # Sort by rating and verification status, return top workers
    recommended = sorted(SAMPLE_WORKERS, key=lambda x: (x.rating, x.verified), reverse=True)[:limit]
    
    return WorkerSearchResponse(
        workers=recommended,
        total_found=len(recommended),
        search_query=f"top {limit} recommended workers"
    )

@app.get("/workers/by-location/{city}")
def get_workers_by_city(city: str, limit: int = Query(10, ge=1, le=50)):
    """Get workers by city (Lagos or Abuja)"""
    city_workers = [w for w in SAMPLE_WORKERS if city.lower() in w.location.lower()]
    
    if not city_workers:
        raise HTTPException(status_code=404, detail=f"No workers found in {city}")
    
    # Sort by rating
    city_workers.sort(key=lambda x: x.rating, reverse=True)
    
    return WorkerSearchResponse(
        workers=city_workers[:limit],
        total_found=len(city_workers),
        search_query=f"workers in {city}"
    )

@app.get("/workers/by-job-type/{job_type}")
def get_workers_by_job_type(job_type: str, limit: int = Query(10, ge=1, le=50)):
    """Get workers by specific job type"""
    job_workers = [w for w in SAMPLE_WORKERS if job_type.lower() in w.job_type.lower()]
    
    if not job_workers:
        raise HTTPException(status_code=404, detail=f"No workers found for job type: {job_type}")
    
    # Sort by rating
    job_workers.sort(key=lambda x: x.rating, reverse=True)
    
    return WorkerSearchResponse(
        workers=job_workers[:limit],
        total_found=len(job_workers),
        search_query=f"{job_type} workers"
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
