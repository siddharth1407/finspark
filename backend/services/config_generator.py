"""
Configuration generation and management service
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4

from ai_pipeline import get_ai_pipeline
from adapters import get_adapter_registry

logger = logging.getLogger(__name__)


class ConfigurationService:
    """
    Service for generating and managing integration configurations.
    """

    def __init__(self):
        self.ai_pipeline = get_ai_pipeline()
        self.adapter_registry = get_adapter_registry()

    async def generate_configuration(
        self,
        requirements: Dict[str, Any],
        requirement_id: UUID,
        tenant_id: str,
        target_adapters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete integration configuration from requirements.

        Args:
            requirements: Extracted requirements JSON
            requirement_id: ID of the requirements record
            tenant_id: Tenant identifier
            target_adapters: Optional list of specific adapters to use

        Returns:
            Complete integration configuration
        """
        logger.info(
            f"Generating configuration for requirement {requirement_id}")

        config_id = uuid4()
        adapters_config = []

        # Process each service in requirements
        services = requirements.get("services", [])

        for service in services:
            service_type = service.get("service_type")

            # Find appropriate adapter
            if target_adapters:
                # Use specified adapters
                adapter = None
                for adapter_id in target_adapters:
                    a = self.adapter_registry.get_adapter(adapter_id)
                    if a and a["service_type"] == service_type:
                        adapter = a
                        break
            else:
                # Get latest adapter for service type
                adapter = self.adapter_registry.get_latest_adapter(
                    service_type)

            if not adapter:
                logger.warning(
                    f"No adapter found for service type: {service_type}")
                continue

            # Generate field mappings using AI
            adapter_schema = adapter.get("field_schema", {})
            mapping = await self.ai_pipeline.generate_field_mappings(
                requirements=service,
                adapter_schema=adapter_schema,
                adapter_id=adapter["adapter_id"],
                adapter_version=adapter["version"]
            )

            # Build adapter configuration
            adapter_config = {
                "adapter_id": adapter["adapter_id"],
                "adapter_name": adapter["name"],
                "version": adapter["version"],
                "service_type": service_type,
                "base_url": adapter["base_url_template"],
                "auth_type": adapter["auth_types"][0] if adapter["auth_types"] else "api_key",
                "field_mappings": mapping.get("field_mappings", []),
                "endpoints": adapter.get("endpoints", []),
                "headers": {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                "timeout_seconds": 30,
                "retry_config": {
                    "max_retries": 3,
                    "backoff_factor": 2
                },
                "mapping_confidence": mapping.get("mapping_confidence", 0),
                "unmapped_fields": mapping.get("unmapped_source_fields", [])
            }

            adapters_config.append(adapter_config)

        # Build complete configuration
        config = {
            "config_id": str(config_id),
            "requirement_id": str(requirement_id),
            "tenant_id": tenant_id,
            "config_name": f"Integration Config - {requirements.get('project_name', 'Unnamed')}",
            "version": "1.0.0",
            "status": "draft",
            "adapters": adapters_config,
            "global_transforms": self._generate_global_transforms(requirements),
            "error_handling": {
                "on_error": "retry_then_fail",
                "max_retries": 3,
                "retry_delay_ms": 1000,
                "circuit_breaker": {
                    "enabled": True,
                    "failure_threshold": 5,
                    "reset_timeout_ms": 30000
                }
            },
            "security": {
                "encryption": "AES-256",
                "pii_fields": self._identify_pii_fields(adapters_config),
                "mask_in_logs": True
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        # Validate the configuration
        validation = await self.ai_pipeline.validate_configuration(config, requirements)
        config["validation"] = validation

        return config

    def _generate_global_transforms(self, requirements: Dict[str, Any]) -> List[Dict]:
        """Generate global transformation rules."""
        transforms = [
            {
                "name": "trim_strings",
                "type": "string",
                "apply_to": "all",
                "operation": "trim"
            },
            {
                "name": "uppercase_ids",
                "type": "string",
                "apply_to": ["pan_number", "gstin"],
                "operation": "uppercase"
            },
            {
                "name": "format_phone",
                "type": "string",
                "apply_to": ["mobile", "phone", "mobile_number"],
                "operation": "regex_replace",
                "pattern": "^\\+91",
                "replacement": ""
            }
        ]
        return transforms

    def _identify_pii_fields(self, adapters_config: List[Dict]) -> List[str]:
        """Identify PII fields across all adapters."""
        pii_keywords = ["aadhaar", "pan", "mobile",
                        "email", "phone", "dob", "address", "account"]
        pii_fields = set()

        for adapter in adapters_config:
            for mapping in adapter.get("field_mappings", []):
                source = mapping.get("source_field", "").lower()
                target = mapping.get("target_field", "").lower()

                if any(kw in source or kw in target for kw in pii_keywords):
                    pii_fields.add(mapping.get("source_field"))

        return list(pii_fields)

    def compare_versions(
        self,
        config_a: Dict[str, Any],
        config_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare two configuration versions."""
        diff = {
            "config_a_version": config_a.get("version"),
            "config_b_version": config_b.get("version"),
            "added_adapters": [],
            "removed_adapters": [],
            "modified_adapters": [],
            "field_changes": []
        }

        adapters_a = {a["adapter_id"]: a for a in config_a.get("adapters", [])}
        adapters_b = {a["adapter_id"]: a for a in config_b.get("adapters", [])}

        # Find added/removed adapters
        diff["added_adapters"] = list(
            set(adapters_b.keys()) - set(adapters_a.keys()))
        diff["removed_adapters"] = list(
            set(adapters_a.keys()) - set(adapters_b.keys()))

        # Find modified adapters
        common = set(adapters_a.keys()) & set(adapters_b.keys())
        for adapter_id in common:
            a = adapters_a[adapter_id]
            b = adapters_b[adapter_id]

            if a.get("version") != b.get("version"):
                diff["modified_adapters"].append({
                    "adapter_id": adapter_id,
                    "old_version": a.get("version"),
                    "new_version": b.get("version")
                })

            # Compare field mappings
            fields_a = {m["source_field"]                        : m for m in a.get("field_mappings", [])}
            fields_b = {m["source_field"]                        : m for m in b.get("field_mappings", [])}

            for field in set(fields_a.keys()) ^ set(fields_b.keys()):
                if field in fields_b:
                    diff["field_changes"].append({
                        "adapter": adapter_id,
                        "field": field,
                        "change": "added"
                    })
                else:
                    diff["field_changes"].append({
                        "adapter": adapter_id,
                        "field": field,
                        "change": "removed"
                    })

        # Calculate compatibility score
        total_changes = (
            len(diff["added_adapters"]) +
            len(diff["removed_adapters"]) +
            len(diff["modified_adapters"]) +
            len(diff["field_changes"])
        )
        diff["compatibility_score"] = max(0, 1 - (total_changes * 0.1))
        diff["is_backward_compatible"] = len(diff["removed_adapters"]) == 0

        return diff


# Singleton
_config_service: Optional[ConfigurationService] = None


def get_configuration_service() -> ConfigurationService:
    global _config_service
    if _config_service is None:
        _config_service = ConfigurationService()
    return _config_service
