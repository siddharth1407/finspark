"""
FastAPI Application - Main entry point
"""
from api import documents, requirements, configurations, simulations, adapters, tenants
import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv(
        "DEBUG", "false").lower() == "true" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("🚀 Starting AI Integration Configuration Engine")
    yield
    logger.info("👋 Shutting down")


# Create FastAPI app
app = FastAPI(
    title="AI Integration Configuration Engine",
    description="""
    ## AI-Assisted Integration Configuration & Orchestration Engine
    
    Convert requirement documents (BRDs, SOWs, API specs) into production-ready 
    integration configurations automatically using AI.
    
    ### Features
    - 📄 **Document Upload & Parsing** - Upload BRDs, SOWs, API specs
    - 🧠 **AI-Powered Extraction** - Extract services, fields, integrations
    - ⚙️ **Auto-Configuration** - Generate field mappings and configs
    - 🧪 **Simulation Engine** - Test configurations with mock APIs
    - 🔒 **Multi-Tenant Security** - Tenant isolation and audit logs
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/v1", tags=["Documents"])
app.include_router(requirements.router, prefix="/api/v1",
                   tags=["Requirements"])
app.include_router(configurations.router, prefix="/api/v1",
                   tags=["Configurations"])
app.include_router(simulations.router, prefix="/api/v1", tags=["Simulations"])
app.include_router(adapters.router, prefix="/api/v1", tags=["Adapters"])
app.include_router(tenants.router, prefix="/api/v1", tags=["Tenants"])


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "service": "AI Integration Configuration Engine",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "api": "up",
            "ai_pipeline": "ready",
            "adapters": "loaded"
        }
    }
