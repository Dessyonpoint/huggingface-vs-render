from fastapi import FastAPI, Request
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="My API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting up...")

@app.on_event("shutdown") 
async def shutdown_event():
    logger.info("Application is shutting down...")

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
    return {"message": "Hello World", "status": "ok", "service": "running"}

@app.get("/health")
@app.head("/health")
def health_check():
    return {"status": "healthy", "service": "active"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
