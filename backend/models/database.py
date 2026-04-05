"""
SQLAlchemy ORM models for database tables
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, Integer, Float, DateTime, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()


class Tenant(Base):
    """Multi-tenant isolation table"""
    __tablename__ = "tenants"

    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    api_quota = Column(Integer, default=1000)
    api_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="tenant")
    configurations = relationship("Configuration", back_populates="tenant")
    audit_logs = relationship("AuditLog", back_populates="tenant")


class Document(Base):
    """Uploaded documents (BRDs, SOWs, API specs)"""
    __tablename__ = "documents"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)  # brd, sow, api_spec
    file_path = Column(String(500))
    raw_text = Column(Text)
    file_size = Column(Integer)
    # uploaded, parsing, parsed, failed
    status = Column(String(50), default="uploaded")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="documents")
    requirements = relationship("Requirement", back_populates="document")

    __table_args__ = (
        Index("idx_documents_tenant", "tenant_id"),
    )


class Requirement(Base):
    """Extracted requirements from documents"""
    __tablename__ = "requirements"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(PGUUID(as_uuid=True), ForeignKey(
        "documents.id"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    project_name = Column(String(255))
    services = Column(JSON, default=list)  # List of extracted services
    integration_points = Column(JSON, default=list)
    data_flows = Column(JSON, default=list)
    security_requirements = Column(JSON, default=list)
    compliance_requirements = Column(JSON, default=list)
    confidence_score = Column(Float, default=0.0)
    extraction_model = Column(String(100))
    extraction_tokens = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="requirements")
    configurations = relationship(
        "Configuration", back_populates="requirement")

    __table_args__ = (
        Index("idx_requirements_tenant", "tenant_id"),
        Index("idx_requirements_document", "document_id"),
    )


class Adapter(Base):
    """Integration adapter registry"""
    __tablename__ = "adapters"

    id = Column(String(100), primary_key=True)  # e.g., "kyc_aadhaar_v2"
    name = Column(String(255), nullable=False)
    # kyc, payment, gst, etc.
    service_type = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)
    supported_versions = Column(JSON, default=list)
    description = Column(Text)
    base_url_template = Column(String(500))
    auth_types = Column(JSON, default=list)  # api_key, oauth2, basic, etc.
    endpoints = Column(JSON, default=list)
    field_schema = Column(JSON, default=dict)
    rate_limits = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)


class Configuration(Base):
    """Generated integration configurations"""
    __tablename__ = "configurations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requirement_id = Column(PGUUID(as_uuid=True),
                            ForeignKey("requirements.id"))
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(String(20), default="1.0.0")
    # draft, validated, deployed, archived
    status = Column(String(50), default="draft")
    # List of adapter configurations
    adapters_config = Column(JSON, default=list)
    global_transforms = Column(JSON, default=list)
    error_handling = Column(JSON, default=dict)
    generation_model = Column(String(100))
    generation_tokens = Column(Integer, default=0)
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relationships
    requirement = relationship("Requirement", back_populates="configurations")
    tenant = relationship("Tenant", back_populates="configurations")
    simulations = relationship("Simulation", back_populates="configuration")

    __table_args__ = (
        Index("idx_configurations_tenant", "tenant_id"),
        Index("idx_configurations_status", "status"),
    )


class Simulation(Base):
    """Simulation/test runs"""
    __tablename__ = "simulations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id = Column(PGUUID(as_uuid=True), ForeignKey(
        "configurations.id"), nullable=False)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    # pending, running, completed, failed
    status = Column(String(50), default="pending")
    scenarios_run = Column(Integer, default=0)
    scenarios_passed = Column(Integer, default=0)
    scenarios_failed = Column(Integer, default=0)
    execution_time_ms = Column(Integer, default=0)
    results = Column(JSON, default=list)
    errors = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    executed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    configuration = relationship("Configuration", back_populates="simulations")

    __table_args__ = (
        Index("idx_simulations_config", "config_id"),
        Index("idx_simulations_tenant", "tenant_id"),
    )


class CredentialVault(Base):
    """Mock credential vault for secure credential storage"""
    __tablename__ = "credential_vault"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    adapter_id = Column(String(100), nullable=False)
    credential_name = Column(String(255), nullable=False)
    encrypted_value = Column(Text)  # In production, use proper encryption
    # api_key, oauth_token, username, password
    credential_type = Column(String(50))
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_credentials_tenant", "tenant_id"),
        Index("idx_credentials_adapter", "adapter_id"),
    )


class AuditLog(Base):
    """Audit trail for all configuration changes"""
    __tablename__ = "audit_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    # create, update, delete, simulate, deploy
    action = Column(String(100), nullable=False)
    # document, requirement, configuration
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=False)
    actor = Column(String(255), nullable=False)
    details = Column(JSON, default=dict)
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_tenant", "tenant_id"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
        Index("idx_audit_timestamp", "timestamp"),
    )


class ConfigVersion(Base):
    """Version history for configurations (for rollback)"""
    __tablename__ = "config_versions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id = Column(PGUUID(as_uuid=True), ForeignKey(
        "configurations.id"), nullable=False)
    version = Column(String(20), nullable=False)
    # Full config at this version
    config_snapshot = Column(JSON, nullable=False)
    change_summary = Column(Text)
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_config_versions_config", "config_id"),
    )
