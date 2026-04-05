"""
Tenants API - Multi-tenant management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services import (
    get_tenant_manager,
    get_credential_vault,
    get_audit_logger
)

router = APIRouter()


class CreateTenantRequest(BaseModel):
    tenant_id: str
    name: str


class StoreCredentialRequest(BaseModel):
    tenant_id: str
    adapter_id: str
    credential_name: str
    credential_value: str
    credential_type: str = "api_key"


@router.post("/tenants")
async def create_tenant(request: CreateTenantRequest):
    """Create a new tenant."""
    manager = get_tenant_manager()

    try:
        tenant = manager.create_tenant(request.tenant_id, request.name)
        return {"success": True, "tenant": tenant}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Get tenant details."""
    manager = get_tenant_manager()
    tenant = manager.get_tenant(tenant_id)

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return tenant


@router.get("/tenants/{tenant_id}/quota")
async def check_quota(tenant_id: str):
    """Check tenant API quota."""
    manager = get_tenant_manager()
    tenant = manager.get_tenant(tenant_id)

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {
        "tenant_id": tenant_id,
        "quota": tenant["api_quota"],
        "used": tenant["api_used"],
        "remaining": tenant["api_quota"] - tenant["api_used"],
        "has_quota": manager.check_quota(tenant_id)
    }


# Credential management
@router.post("/tenants/{tenant_id}/credentials")
async def store_credential(tenant_id: str, request: StoreCredentialRequest):
    """Store a credential in the vault."""
    manager = get_tenant_manager()
    if not manager.validate_tenant(tenant_id):
        raise HTTPException(status_code=403, detail="Invalid tenant")

    vault = get_credential_vault()
    cred_id = vault.store_credential(
        tenant_id=tenant_id,
        adapter_id=request.adapter_id,
        credential_name=request.credential_name,
        credential_value=request.credential_value,
        credential_type=request.credential_type
    )

    # Audit log (don't log the actual credential value!)
    audit = get_audit_logger()
    audit.log(
        tenant_id=tenant_id,
        action="store_credential",
        resource_type="credential",
        resource_id=cred_id,
        actor="api_user",
        details={"adapter_id": request.adapter_id,
                 "credential_name": request.credential_name}
    )

    return {"success": True, "credential_id": cred_id}


@router.get("/tenants/{tenant_id}/credentials")
async def list_credentials(tenant_id: str):
    """List credentials for a tenant (without values)."""
    vault = get_credential_vault()
    credentials = vault.list_credentials(tenant_id)
    return {"credentials": credentials, "count": len(credentials)}


@router.delete("/tenants/{tenant_id}/credentials/{adapter_id}/{credential_name}")
async def delete_credential(tenant_id: str, adapter_id: str, credential_name: str):
    """Delete a credential."""
    vault = get_credential_vault()
    deleted = vault.delete_credential(tenant_id, adapter_id, credential_name)

    if not deleted:
        raise HTTPException(status_code=404, detail="Credential not found")

    return {"success": True, "message": "Credential deleted"}


# Audit logs
@router.get("/tenants/{tenant_id}/audit-logs")
async def get_audit_logs(
    tenant_id: str,
    resource_type: Optional[str] = None,
    limit: int = 100
):
    """Get audit logs for a tenant."""
    audit = get_audit_logger()
    logs = audit.get_logs(tenant_id, resource_type, limit)
    return {"logs": logs, "count": len(logs)}
