"""
Pydantic models for the Integration Engine
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


# ============== ENUMS ==============
class ServiceType(str, Enum):
    KYC = "kyc"
    PAYMENT = "payment"
    GST = "gst"
    BANKING = "banking"
    INSURANCE = "insurance"
    CUSTOM = "custom"


class ServicePriority(str, Enum):
    MANDATORY = "mandatory"
    OPTIONAL = "optional"
    CONDITIONAL = "conditional"


class ConfigStatus(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


class SimulationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ============== REQUEST MODELS ==============
class DocumentUploadRequest(BaseModel):
    tenant_id: str
    document_name: str
    document_type: str = "brd"  # brd, sow, api_spec


class ParseRequirementsRequest(BaseModel):
    document_id: UUID
    tenant_id: str


class GenerateConfigRequest(BaseModel):
    requirement_id: UUID
    tenant_id: str
    target_adapters: Optional[List[str]] = None


class SimulationRequest(BaseModel):
    config_id: UUID
    tenant_id: str
    test_scenarios: Optional[List[str]] = None


class CompareConfigsRequest(BaseModel):
    config_id_a: UUID
    config_id_b: UUID
    tenant_id: str


# ============== RESPONSE MODELS ==============
class ExtractedService(BaseModel):
    """Single service extracted from requirements"""
    service_type: ServiceType
    service_name: str
    priority: ServicePriority
    description: str
    api_endpoints: List[Dict[str, Any]] = []
    required_fields: List[Dict[str, str]] = []
    optional_fields: List[Dict[str, str]] = []
    constraints: List[str] = []


class ExtractedRequirements(BaseModel):
    """Full extracted requirements from a document"""
    document_id: UUID
    document_name: str
    project_name: str
    services: List[ExtractedService]
    integration_points: List[Dict[str, Any]]
    data_flows: List[Dict[str, Any]]
    security_requirements: List[str]
    compliance_requirements: List[str]
    extracted_at: datetime
    confidence_score: float = Field(ge=0, le=1)
    raw_text_preview: str


class FieldMapping(BaseModel):
    """Single field mapping between source and target"""
    source_field: str
    target_field: str
    transformation: Optional[str] = None
    default_value: Optional[Any] = None
    is_required: bool = True
    validation_rules: List[str] = []


class AdapterConfig(BaseModel):
    """Configuration for a single adapter"""
    adapter_id: str
    adapter_name: str
    version: str
    base_url: str
    auth_type: str
    field_mappings: List[FieldMapping]
    headers: Dict[str, str] = {}
    timeout_seconds: int = 30
    retry_config: Dict[str, Any] = {}


class IntegrationConfig(BaseModel):
    """Complete integration configuration"""
    config_id: UUID
    requirement_id: UUID
    tenant_id: str
    config_name: str
    version: str
    status: ConfigStatus
    adapters: List[AdapterConfig]
    global_transforms: List[Dict[str, Any]] = []
    error_handling: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    created_by: str


class SimulationResult(BaseModel):
    """Result of a simulation run"""
    simulation_id: UUID
    config_id: UUID
    status: SimulationStatus
    test_scenarios_run: int
    test_scenarios_passed: int
    test_scenarios_failed: int
    execution_time_ms: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    executed_at: datetime


class ConfigDiff(BaseModel):
    """Difference between two configurations"""
    config_a_id: UUID
    config_b_id: UUID
    added_fields: List[Dict[str, Any]]
    removed_fields: List[Dict[str, Any]]
    modified_fields: List[Dict[str, Any]]
    added_adapters: List[str]
    removed_adapters: List[str]
    compatibility_score: float = Field(ge=0, le=1)
    migration_notes: List[str]


# ============== ADAPTER REGISTRY MODELS ==============
class AdapterMetadata(BaseModel):
    """Metadata for an integration adapter"""
    adapter_id: str
    name: str
    service_type: ServiceType
    version: str
    supported_versions: List[str]
    description: str
    base_url_template: str
    auth_types: List[str]
    endpoints: List[Dict[str, Any]]
    field_schema: Dict[str, Any]
    rate_limits: Dict[str, int] = {}
    is_active: bool = True


# ============== TENANT MODELS ==============
class Tenant(BaseModel):
    """Tenant information"""
    tenant_id: str
    tenant_name: str
    is_active: bool = True
    created_at: datetime
    config_count: int = 0
    api_quota: int = 1000


class AuditLog(BaseModel):
    """Audit log entry"""
    log_id: UUID
    tenant_id: str
    action: str
    resource_type: str
    resource_id: str
    actor: str
    details: Dict[str, Any]
    timestamp: datetime
    ip_address: Optional[str] = None


# ============== GENERIC RESPONSES ==============
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
