"""
Configurations API - Generate and manage integration configurations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from services import get_configuration_service, get_audit_logger, get_tenant_manager
from api.requirements import requirements_store

router = APIRouter()

# In-memory storage
configurations_store = {}
config_versions_store = {}


class GenerateConfigRequest(BaseModel):
    requirement_id: str
    tenant_id: str = "tenant_demo"
    target_adapters: Optional[List[str]] = None
    config_name: Optional[str] = None


class UpdateConfigRequest(BaseModel):
    tenant_id: str = "tenant_demo"
    status: Optional[str] = None
    adapters: Optional[List[dict]] = None


class CompareConfigsRequest(BaseModel):
    config_id_a: str
    config_id_b: str
    tenant_id: str = "tenant_demo"


@router.post("/configurations/generate")
async def generate_configuration(request: GenerateConfigRequest):
    """
    Generate integration configuration from requirements.

    Uses AI to:
    - Match services to appropriate adapters
    - Generate field mappings
    - Create transformation rules
    - Set up error handling
    """
    # Validate tenant
    tenant_manager = get_tenant_manager()
    if not tenant_manager.validate_tenant(request.tenant_id):
        raise HTTPException(
            status_code=403, detail="Invalid or inactive tenant")

    # Get requirements
    requirement = requirements_store.get(request.requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    if requirement["tenant_id"] != request.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Generate configuration
    config_service = get_configuration_service()

    try:
        config = await config_service.generate_configuration(
            requirements=requirement,
            requirement_id=request.requirement_id,
            tenant_id=request.tenant_id,
            target_adapters=request.target_adapters
        )

        if request.config_name:
            config["config_name"] = request.config_name

        # Store configuration
        config_id = config["config_id"]
        configurations_store[config_id] = config

        # Store initial version
        version_id = str(uuid4())
        config_versions_store[version_id] = {
            "id": version_id,
            "config_id": config_id,
            "version": config["version"],
            "config_snapshot": config.copy(),
            "created_at": datetime.utcnow().isoformat()
        }

        # Audit log
        audit = get_audit_logger()
        audit.log(
            tenant_id=request.tenant_id,
            action="generate",
            resource_type="configuration",
            resource_id=config_id,
            actor="api_user",
            details={
                "requirement_id": request.requirement_id,
                "adapters_count": len(config.get("adapters", []))
            }
        )

        tenant_manager.increment_usage(request.tenant_id)

        return {
            "success": True,
            "config_id": config_id,
            "config_name": config["config_name"],
            "version": config["version"],
            "status": config["status"],
            "adapters_count": len(config.get("adapters", [])),
            "validation": config.get("validation", {}),
            "configuration": config
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Configuration generation failed: {str(e)}")


@router.get("/configurations/{config_id}")
async def get_configuration(config_id: str, tenant_id: str = "tenant_demo"):
    """Get configuration by ID."""
    config = configurations_store.get(config_id)

    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    if config["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return config


@router.get("/configurations")
async def list_configurations(tenant_id: str = "tenant_demo", status: Optional[str] = None):
    """List all configurations for a tenant."""
    configs = [
        {
            "config_id": c["config_id"],
            "config_name": c["config_name"],
            "version": c["version"],
            "status": c["status"],
            "adapters_count": len(c.get("adapters", [])),
            "created_at": c["created_at"]
        }
        for c in configurations_store.values()
        if c["tenant_id"] == tenant_id and (status is None or c["status"] == status)
    ]
    return {"configurations": configs, "count": len(configs)}


@router.put("/configurations/{config_id}")
async def update_configuration(config_id: str, request: UpdateConfigRequest):
    """Update a configuration."""
    config = configurations_store.get(config_id)

    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    if config["tenant_id"] != request.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Store old version
    old_version = config["version"]
    new_version = _increment_version(old_version)

    version_id = str(uuid4())
    config_versions_store[version_id] = {
        "id": version_id,
        "config_id": config_id,
        "version": old_version,
        "config_snapshot": config.copy(),
        "created_at": datetime.utcnow().isoformat()
    }

    # Update config
    if request.status:
        config["status"] = request.status
    if request.adapters:
        config["adapters"] = request.adapters

    config["version"] = new_version
    config["updated_at"] = datetime.utcnow().isoformat()

    # Audit log
    audit = get_audit_logger()
    audit.log(
        tenant_id=request.tenant_id,
        action="update",
        resource_type="configuration",
        resource_id=config_id,
        actor="api_user",
        details={"old_version": old_version, "new_version": new_version}
    )

    return {
        "success": True,
        "config_id": config_id,
        "old_version": old_version,
        "new_version": new_version
    }


@router.post("/configurations/compare")
async def compare_configurations(request: CompareConfigsRequest):
    """Compare two configuration versions."""
    config_a = configurations_store.get(request.config_id_a)
    config_b = configurations_store.get(request.config_id_b)

    if not config_a or not config_b:
        raise HTTPException(
            status_code=404, detail="One or both configurations not found")

    if config_a["tenant_id"] != request.tenant_id or config_b["tenant_id"] != request.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    config_service = get_configuration_service()
    diff = config_service.compare_versions(config_a, config_b)

    return diff


@router.get("/configurations/{config_id}/versions")
async def get_config_versions(config_id: str, tenant_id: str = "tenant_demo"):
    """Get version history for a configuration."""
    versions = [
        {
            "version_id": v["id"],
            "version": v["version"],
            "created_at": v["created_at"]
        }
        for v in config_versions_store.values()
        if v["config_id"] == config_id
    ]
    return {"versions": sorted(versions, key=lambda x: x["created_at"], reverse=True)}


@router.post("/configurations/{config_id}/rollback/{version}")
async def rollback_configuration(config_id: str, version: str, tenant_id: str = "tenant_demo"):
    """Rollback configuration to a previous version."""
    config = configurations_store.get(config_id)

    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    if config["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Find version
    target_version = None
    for v in config_versions_store.values():
        if v["config_id"] == config_id and v["version"] == version:
            target_version = v
            break

    if not target_version:
        raise HTTPException(
            status_code=404, detail=f"Version {version} not found")

    # Store current as new version before rollback
    current_version = config["version"]
    version_id = str(uuid4())
    config_versions_store[version_id] = {
        "id": version_id,
        "config_id": config_id,
        "version": current_version,
        "config_snapshot": config.copy(),
        "change_summary": f"Pre-rollback snapshot from {current_version}",
        "created_at": datetime.utcnow().isoformat()
    }

    # Rollback
    snapshot = target_version["config_snapshot"]
    for key in ["adapters", "global_transforms", "error_handling"]:
        if key in snapshot:
            config[key] = snapshot[key]

    config["version"] = _increment_version(current_version)
    config["updated_at"] = datetime.utcnow().isoformat()

    # Audit log
    audit = get_audit_logger()
    audit.log(
        tenant_id=tenant_id,
        action="rollback",
        resource_type="configuration",
        resource_id=config_id,
        actor="api_user",
        details={
            "from_version": current_version,
            "to_version": version,
            "new_version": config["version"]
        }
    )

    return {
        "success": True,
        "config_id": config_id,
        "rolled_back_from": current_version,
        "rolled_back_to": version,
        "new_version": config["version"]
    }


def _increment_version(version: str) -> str:
    """Increment version number (1.0.0 -> 1.0.1)."""
    parts = version.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)
