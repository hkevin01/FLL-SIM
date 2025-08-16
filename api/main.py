"""
FLL-Sim Educational Platform API
FastAPI-based REST API for the FLL-Sim educational platform
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

# Add project src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from api.auth import verify_token
from api.database import get_db, init_db
from api.models import User
from api.routers import analytics, auth, missions, simulations, students
from fll_sim.education.educational_platform import EducationalPlatform
from fll_sim.utils.logger import FLLLogger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = FLLLogger('FLLSimAPI')

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting FLL-Sim API...")
    await init_db()
    logger.info("Database initialized")

    # Initialize educational platform
    app.state.edu_platform = EducationalPlatform()
    logger.info("Educational platform initialized")

    yield

    # Shutdown
    logger.info("Shutting down FLL-Sim API...")

# Create FastAPI application
app = FastAPI(
    title="FLL-Sim Educational Platform API",
    description="REST API for the FLL-Sim educational robotics platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/v1/students", tags=["Students"])
app.include_router(missions.router, prefix="/api/v1/missions", tags=["Missions"])
app.include_router(simulations.router, prefix="/api/v1/simulations", tags=["Simulations"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FLL-Sim Educational Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db = next(get_db())
        db.execute("SELECT 1")

        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

@app.get("/api/v1/platform/status")
async def platform_status(current_user: User = Depends(verify_token)):
    """Get educational platform status"""
    try:
        edu_platform = app.state.edu_platform

        return {
            "platform_active": True,
            "active_sessions": len(edu_platform.active_sessions),
            "available_missions": len(edu_platform.mission_builder.missions),
            "system_status": "operational"
        }
    except Exception as e:
        logger.error(f"Platform status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get platform status"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    )
