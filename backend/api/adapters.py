"""
Adapters API - Manage integration adapters
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from adapters import get_adapter_registry

router = APIRouter()


@router.get("/adapters")
async def list_adapters(service_type: Optional[str] = None, active_only: bool = True):
    """List all available adapters."""
    registry = get_adapter_registry()

    if service_type:
        adapters = registry.get_adapters_by_type(service_type)
    else:
        adapters = registry.list_all_adapters()

    if active_only:
        adapters = [a for a in adapters if a.get("is_active", True)]

    return {
        "adapters": [
            {
                "adapter_id": a["adapter_id"],
                "name": a["name"],
                "service_type": a["service_type"],
                "version": a["version"],
                "description": a["description"],
                "auth_types": a["auth_types"],
                "is_active": a["is_active"]
            }
            for a in adapters
        ],
        "count": len(adapters)
    }


@router.get("/adapters/{adapter_id}")
async def get_adapter(adapter_id: str):
    """Get adapter details by ID."""
    registry = get_adapter_registry()
    adapter = registry.get_adapter(adapter_id)

    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found")

    return adapter


@router.get("/adapters/{adapter_id}/schema")
async def get_adapter_schema(adapter_id: str):
    """Get field schema for an adapter."""
    registry = get_adapter_registry()
    schema = registry.get_field_schema(adapter_id)

    if not schema:
        raise HTTPException(status_code=404, detail="Adapter not found")

    return {
        "adapter_id": adapter_id,
        "field_schema": schema
    }


@router.get("/adapters/{adapter_id}/compatibility/{required_version}")
async def check_compatibility(adapter_id: str, required_version: str):
    """Check if adapter supports required version."""
    registry = get_adapter_registry()
    result = registry.check_version_compatibility(adapter_id, required_version)
    return result


@router.get("/adapters/migration/{from_adapter}/{to_adapter}")
async def get_migration_path(from_adapter: str, to_adapter: str):
    """Get migration path between adapter versions."""
    registry = get_adapter_registry()
    result = registry.get_migration_path(from_adapter, to_adapter)
    return result


@router.get("/adapters/types")
async def get_service_types():
    """Get all available service types."""
    registry = get_adapter_registry()
    adapters = registry.list_all_adapters()

    types = {}
    for adapter in adapters:
        stype = adapter["service_type"]
        if stype not in types:
            types[stype] = {"count": 0, "adapters": []}
        types[stype]["count"] += 1
        types[stype]["adapters"].append(adapter["adapter_id"])

    return {"service_types": types}
