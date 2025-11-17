from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
import logging
from config import CORS_ORIGINS, API_TIMEOUT_SECONDS
from api import reviews, reprints, freshdesk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quality/Damage Analysis API", version="1.0.0")

# SECURITY: Restrict CORS to specific origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Only allow configured origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Restrict methods
    allow_headers=["Content-Type", "Authorization"],  # Restrict headers
    max_age=3600,  # Cache preflight requests
)

# Request timeout middleware
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        if process_time > API_TIMEOUT_SECONDS:
            logger.warning(f"Request {request.url} took {process_time:.2f}s (exceeded {API_TIMEOUT_SECONDS}s)")
        return response
    except Exception as e:
        logger.error(f"Request error: {e}", exc_info=True)
        raise

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# Include routers
app.include_router(reviews.router)
app.include_router(reprints.router)
app.include_router(freshdesk.router)

@app.get("/")
async def root():
    return {"message": "Quality/Damage Analysis API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

