"""
Requirements API - Parse and manage extracted requirements
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from ai_pipeline import get_ai_pipeline
from services import get_audit_logger, get_tenant_manager
from api.documents import documents_store

router = APIRouter()

# In-memory storage
requirements_store = {}


class ParseRequest(BaseModel):
    document_id: str
    tenant_id: str = "tenant_demo"


@router.post("/requirements/parse")
async def parse_requirements(request: ParseRequest):
    """
    Parse requirements from an uploaded document using AI.

    This endpoint uses LLM to:
    - Extract services (KYC, Payment, GST, etc.)
    - Identify mandatory vs optional services
    - Extract API endpoints and fields
    - Identify integration points and data flows
    """
    # Validate tenant
    tenant_manager = get_tenant_manager()
    if not tenant_manager.validate_tenant(request.tenant_id):
        raise HTTPException(
            status_code=403, detail="Invalid or inactive tenant")

    # Get document
    document = documents_store.get(request.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document["tenant_id"] != request.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Update document status
    document["status"] = "parsing"

    # Use AI pipeline to extract requirements
    pipeline = get_ai_pipeline()

    try:
        extracted = await pipeline.extract_requirements(document["raw_text"])

        # Generate requirement ID
        req_id = str(uuid4())

        # Store requirements
        requirement = {
            "id": req_id,
            "document_id": request.document_id,
            "tenant_id": request.tenant_id,
            "project_name": extracted.get("project_name", "Unnamed Project"),
            "services": extracted.get("services", []),
            "integration_points": extracted.get("integration_points", []),
            "data_flows": extracted.get("data_flows", []),
            "security_requirements": extracted.get("security_requirements", []),
            "compliance_requirements": extracted.get("compliance_requirements", []),
            "confidence_score": extracted.get("confidence_score", 0),
            "extraction_model": extracted.get("extraction_model", "unknown"),
            "raw_text_preview": document["raw_text"][:1000],
            "created_at": datetime.utcnow().isoformat()
        }
        requirements_store[req_id] = requirement

        # Update document status
        document["status"] = "parsed"
        document["requirement_id"] = req_id

        # Audit log
        audit = get_audit_logger()
        audit.log(
            tenant_id=request.tenant_id,
            action="parse",
            resource_type="requirement",
            resource_id=req_id,
            actor="api_user",
            details={
                "document_id": request.document_id,
                "services_found": len(extracted.get("services", [])),
                "confidence": extracted.get("confidence_score", 0)
            }
        )

        tenant_manager.increment_usage(request.tenant_id)

        return {
            "success": True,
            "requirement_id": req_id,
            "project_name": requirement["project_name"],
            "services_count": len(requirement["services"]),
            "confidence_score": requirement["confidence_score"],
            "services": requirement["services"],
            "integration_points": requirement["integration_points"]
        }

    except Exception as e:
        document["status"] = "failed"
        raise HTTPException(
            status_code=500, detail=f"Parsing failed: {str(e)}")


@router.get("/requirements/{requirement_id}")
async def get_requirement(requirement_id: str, tenant_id: str = "tenant_demo"):
    """Get extracted requirements by ID."""
    requirement = requirements_store.get(requirement_id)

    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    if requirement["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return requirement


@router.get("/requirements")
async def list_requirements(tenant_id: str = "tenant_demo"):
    """List all requirements for a tenant."""
    reqs = [
        {
            "id": req["id"],
            "document_id": req["document_id"],
            "project_name": req["project_name"],
            "services_count": len(req["services"]),
            "confidence_score": req["confidence_score"],
            "created_at": req["created_at"]
        }
        for req in requirements_store.values()
        if req["tenant_id"] == tenant_id
    ]
    return {"requirements": reqs, "count": len(reqs)}


@router.get("/requirements/{requirement_id}/services")
async def get_services(requirement_id: str, tenant_id: str = "tenant_demo"):
    """Get extracted services from requirements."""
    requirement = requirements_store.get(requirement_id)

    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    if requirement["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "services": requirement["services"],
        "count": len(requirement["services"]),
        "service_types": list(set(s.get("service_type") for s in requirement["services"]))
    }
