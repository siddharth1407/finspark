"""
Security and audit services
"""
import hashlib
import base64
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import uuid4

logger = logging.getLogger(__name__)


class TenantManager:
    """
    Multi-tenant management with isolation.
    """

    def __init__(self):
        # In-memory tenant store (use DB in production)
        self.tenants: Dict[str, Dict] = {
            "tenant_demo": {
                "id": "tenant_demo",
                "name": "Demo Company",
                "is_active": True,
                "api_quota": 10000,
                "api_used": 0,
                "created_at": datetime.utcnow().isoformat()
            }
        }

    def create_tenant(self, tenant_id: str, name: str) -> Dict[str, Any]:
        """Create a new tenant."""
        if tenant_id in self.tenants:
            raise ValueError(f"Tenant {tenant_id} already exists")

        tenant = {
            "id": tenant_id,
            "name": name,
            "is_active": True,
            "api_quota": 1000,
            "api_used": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        self.tenants[tenant_id] = tenant
        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant by ID."""
        return self.tenants.get(tenant_id)

    def validate_tenant(self, tenant_id: str) -> bool:
        """Validate tenant exists and is active."""
        tenant = self.get_tenant(tenant_id)
        return tenant is not None and tenant.get("is_active", False)

    def check_quota(self, tenant_id: str) -> bool:
        """Check if tenant has remaining API quota."""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        return tenant["api_used"] < tenant["api_quota"]

    def increment_usage(self, tenant_id: str) -> None:
        """Increment API usage counter."""
        tenant = self.get_tenant(tenant_id)
        if tenant:
            tenant["api_used"] += 1


class CredentialVault:
    """
    Mock credential vault for secure credential storage.
    In production, use HashiCorp Vault or AWS Secrets Manager.
    """

    def __init__(self):
        # In-memory store (encrypted in production)
        self.credentials: Dict[str, Dict[str, Any]] = {}

    def _encrypt(self, value: str) -> str:
        """Mock encryption - use real encryption in production."""
        return base64.b64encode(value.encode()).decode()

    def _decrypt(self, value: str) -> str:
        """Mock decryption."""
        return base64.b64decode(value.encode()).decode()

    def store_credential(
        self,
        tenant_id: str,
        adapter_id: str,
        credential_name: str,
        credential_value: str,
        credential_type: str = "api_key"
    ) -> str:
        """Store a credential securely."""
        cred_id = str(uuid4())

        key = f"{tenant_id}:{adapter_id}:{credential_name}"
        self.credentials[key] = {
            "id": cred_id,
            "tenant_id": tenant_id,
            "adapter_id": adapter_id,
            "name": credential_name,
            "encrypted_value": self._encrypt(credential_value),
            "type": credential_type,
            "created_at": datetime.utcnow().isoformat()
        }

        logger.info(
            f"Stored credential {credential_name} for {tenant_id}/{adapter_id}")
        return cred_id

    def get_credential(
        self,
        tenant_id: str,
        adapter_id: str,
        credential_name: str
    ) -> Optional[str]:
        """Retrieve a credential (decrypted)."""
        key = f"{tenant_id}:{adapter_id}:{credential_name}"
        cred = self.credentials.get(key)

        if not cred:
            return None

        return self._decrypt(cred["encrypted_value"])

    def list_credentials(self, tenant_id: str) -> List[Dict[str, Any]]:
        """List credentials for a tenant (without values)."""
        return [
            {
                "id": c["id"],
                "adapter_id": c["adapter_id"],
                "name": c["name"],
                "type": c["type"],
                "created_at": c["created_at"]
            }
            for c in self.credentials.values()
            if c["tenant_id"] == tenant_id
        ]

    def delete_credential(
        self,
        tenant_id: str,
        adapter_id: str,
        credential_name: str
    ) -> bool:
        """Delete a credential."""
        key = f"{tenant_id}:{adapter_id}:{credential_name}"
        if key in self.credentials:
            del self.credentials[key]
            return True
        return False


class AuditLogger:
    """
    Audit logging for all configuration changes.
    """

    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def log(
        self,
        tenant_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        actor: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """Log an audit event."""
        log_id = str(uuid4())

        entry = {
            "log_id": log_id,
            "tenant_id": tenant_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "actor": actor,
            "details": details or {},
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logs.append(entry)
        logger.info(
            f"Audit: {tenant_id}/{actor} {action} {resource_type}/{resource_id}")

        return log_id

    def get_logs(
        self,
        tenant_id: str,
        resource_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit logs for a tenant."""
        filtered = [
            log for log in self.logs
            if log["tenant_id"] == tenant_id
            and (resource_type is None or log["resource_type"] == resource_type)
        ]

        # Return most recent first
        return sorted(filtered, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def get_resource_history(
        self,
        resource_type: str,
        resource_id: str
    ) -> List[Dict[str, Any]]:
        """Get history for a specific resource."""
        return [
            log for log in self.logs
            if log["resource_type"] == resource_type
            and log["resource_id"] == resource_id
        ]


# Singletons
_tenant_manager: Optional[TenantManager] = None
_credential_vault: Optional[CredentialVault] = None
_audit_logger: Optional[AuditLogger] = None


def get_tenant_manager() -> TenantManager:
    global _tenant_manager
    if _tenant_manager is None:
        _tenant_manager = TenantManager()
    return _tenant_manager


def get_credential_vault() -> CredentialVault:
    global _credential_vault
    if _credential_vault is None:
        _credential_vault = CredentialVault()
    return _credential_vault


def get_audit_logger() -> AuditLogger:
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
