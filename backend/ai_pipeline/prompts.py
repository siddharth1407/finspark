"""
AI Pipeline - Prompt Templates for LLM-based Processing
These prompts are designed for maximum extraction accuracy and structured output.
"""

# =====================================================
# REQUIREMENT EXTRACTION PROMPT
# =====================================================
REQUIREMENT_EXTRACTION_PROMPT = """You are an enterprise integration analyst AI. Your task is to analyze business requirement documents and extract structured information about integration requirements.

## INPUT DOCUMENT
```
{document_text}
```

## EXTRACTION TASK
Analyze the document and extract ALL integration-related information. Be thorough and precise.

## OUTPUT FORMAT (JSON)
Respond ONLY with valid JSON in this exact structure:

```json
{{
    "project_name": "Name of the project or integration initiative",
    "services": [
        {{
            "service_type": "kyc|payment|gst|banking|insurance|custom",
            "service_name": "Human readable name (e.g., Aadhaar KYC Verification)",
            "priority": "mandatory|optional|conditional",
            "description": "What this service does",
            "api_endpoints": [
                {{
                    "method": "GET|POST|PUT|DELETE",
                    "path": "/api/v1/example",
                    "description": "What this endpoint does"
                }}
            ],
            "required_fields": [
                {{"field_name": "aadhaar_number", "data_type": "string", "description": "12-digit Aadhaar"}}
            ],
            "optional_fields": [
                {{"field_name": "mobile", "data_type": "string", "description": "Mobile for OTP"}}
            ],
            "constraints": ["Must complete within 30 seconds", "Requires OTP verification"]
        }}
    ],
    "integration_points": [
        {{
            "source_system": "System A",
            "target_system": "System B", 
            "data_exchanged": "Customer PAN details",
            "frequency": "real-time|batch|on-demand"
        }}
    ],
    "data_flows": [
        {{
            "flow_name": "Customer Onboarding",
            "steps": ["Collect details", "Verify KYC", "Create account"],
            "systems_involved": ["CRM", "KYC Provider", "Core Banking"]
        }}
    ],
    "security_requirements": [
        "All PII must be encrypted at rest",
        "OAuth 2.0 for API authentication"
    ],
    "compliance_requirements": [
        "GDPR compliant data handling",
        "RBI guidelines for KYC"
    ],
    "confidence_score": 0.85
}}
```

## EXTRACTION RULES
1. Extract ALL services mentioned, even implicitly
2. Infer service_type from context (e.g., "Aadhaar verification" → "kyc")
3. Mark services as "mandatory" if words like "must", "required", "essential" are used
4. Mark as "optional" if words like "may", "optional", "nice to have" are used
5. Extract API details if mentioned, otherwise leave empty
6. confidence_score: 0.9+ if explicit, 0.7-0.9 if inferred, <0.7 if uncertain

## IMPORTANT
- Return ONLY the JSON, no explanations
- Ensure valid JSON syntax
- If no services found, return empty services array
- Extract maximum possible information
"""

# =====================================================
# FIELD MAPPING GENERATION PROMPT
# =====================================================
FIELD_MAPPING_PROMPT = """You are an integration configuration AI. Your task is to generate field mappings between source requirements and target adapter schemas.

## SOURCE REQUIREMENTS
```json
{requirements_json}
```

## TARGET ADAPTER SCHEMA
```json
{adapter_schema}
```

## TASK
Generate precise field mappings from source to target. Include transformations where needed.

## OUTPUT FORMAT (JSON)
Respond ONLY with valid JSON:

```json
{{
    "adapter_id": "{adapter_id}",
    "adapter_name": "Human readable name",
    "version": "{adapter_version}",
    "field_mappings": [
        {{
            "source_field": "customer.aadhaar_number",
            "target_field": "aadhaarId",
            "transformation": "trim() | validate_aadhaar()",
            "default_value": null,
            "is_required": true,
            "validation_rules": ["length:12", "numeric_only"]
        }},
        {{
            "source_field": "customer.full_name",
            "target_field": "name",
            "transformation": "uppercase() | truncate(100)",
            "default_value": null,
            "is_required": true,
            "validation_rules": ["min_length:1", "max_length:100"]
        }}
    ],
    "unmapped_source_fields": ["field1", "field2"],
    "unmapped_target_fields": ["targetField1"],
    "mapping_confidence": 0.92,
    "notes": ["Auto-mapped 8/10 fields", "Review: mobile_number mapping"]
}}
```

## MAPPING RULES
1. Match fields by semantic similarity, not just exact name match
2. Common mappings:
   - aadhaar/aadhar/aadhaar_number → aadhaarId
   - phone/mobile/contact → mobileNumber
   - name/full_name/customer_name → name
   - pan/pan_number → panNumber
3. Add appropriate transformations:
   - trim() for strings
   - uppercase()/lowercase() for normalization
   - format_date(from, to) for dates
   - validate_X() for validation
4. Mark is_required based on source requirement priority
5. List unmapped fields for manual review

## IMPORTANT
- Return ONLY valid JSON
- Be thorough in mapping attempts
- Prefer semantic matching over giving up
"""

# =====================================================
# CONFIGURATION VALIDATION PROMPT
# =====================================================
CONFIG_VALIDATION_PROMPT = """You are an integration configuration validator. Review the generated configuration for completeness and correctness.

## CONFIGURATION TO VALIDATE
```json
{config_json}
```

## ORIGINAL REQUIREMENTS
```json
{requirements_json}
```

## VALIDATION TASK
Check the configuration against requirements and best practices.

## OUTPUT FORMAT (JSON)
```json
{{
    "is_valid": true,
    "validation_score": 0.95,
    "issues": [
        {{
            "severity": "error|warning|info",
            "field": "adapters[0].field_mappings[2]",
            "message": "Required field 'pan_number' is not mapped",
            "suggestion": "Map to 'panId' in target schema"
        }}
    ],
    "coverage": {{
        "required_fields_mapped": 8,
        "required_fields_total": 10,
        "optional_fields_mapped": 3,
        "optional_fields_total": 5
    }},
    "recommendations": [
        "Add retry logic for KYC endpoint (recommended 3 retries)",
        "Consider adding fallback adapter for payment gateway"
    ],
    "security_check": {{
        "pii_fields_identified": ["aadhaar_number", "pan_number"],
        "encryption_configured": true,
        "auth_configured": true
    }}
}}
```

## VALIDATION RULES
1. All mandatory service fields must be mapped
2. Required fields must have is_required: true
3. PII fields must have encryption or masking
4. Auth configuration must be present
5. Timeout and retry configs recommended
"""

# =====================================================
# SIMULATION SCENARIO GENERATION PROMPT
# =====================================================
SIMULATION_SCENARIO_PROMPT = """You are a QA engineer AI. Generate test scenarios for the integration configuration.

## CONFIGURATION
```json
{config_json}
```

## TASK
Generate comprehensive test scenarios covering happy path, edge cases, and error scenarios.

## OUTPUT FORMAT (JSON)
```json
{{
    "test_scenarios": [
        {{
            "scenario_id": "TC001",
            "name": "Happy Path - Valid Aadhaar Verification",
            "description": "Test successful KYC verification with valid Aadhaar",
            "adapter": "kyc_aadhaar_v2",
            "input": {{
                "aadhaar_number": "123456789012",
                "name": "JOHN DOE",
                "mobile": "9876543210"
            }},
            "expected_output": {{
                "status": "success",
                "verification_status": "verified",
                "match_score": 0.95
            }},
            "expected_http_status": 200
        }},
        {{
            "scenario_id": "TC002",
            "name": "Error - Invalid Aadhaar Format",
            "description": "Test error handling for invalid Aadhaar format",
            "adapter": "kyc_aadhaar_v2",
            "input": {{
                "aadhaar_number": "12345",
                "name": "JOHN DOE"
            }},
            "expected_output": {{
                "status": "error",
                "error_code": "INVALID_AADHAAR"
            }},
            "expected_http_status": 400
        }}
    ],
    "coverage_summary": {{
        "total_scenarios": 10,
        "happy_path": 3,
        "edge_cases": 4,
        "error_scenarios": 3
    }}
}}
```
"""

# =====================================================
# CONFIG DIFF ANALYSIS PROMPT
# =====================================================
CONFIG_DIFF_PROMPT = """You are a configuration analyst. Compare two configuration versions and identify differences.

## CONFIGURATION A (Version: {version_a})
```json
{config_a}
```

## CONFIGURATION B (Version: {version_b})
```json
{config_b}
```

## TASK
Analyze differences and assess backward compatibility.

## OUTPUT FORMAT (JSON)
```json
{{
    "added_fields": [
        {{"adapter": "payment_v2", "field": "upi_id", "details": "New UPI support added"}}
    ],
    "removed_fields": [
        {{"adapter": "kyc_v1", "field": "photo_url", "impact": "Photo verification no longer supported"}}
    ],
    "modified_fields": [
        {{
            "adapter": "kyc_v2",
            "field": "aadhaar_number",
            "old_value": {{"validation": "length:12"}},
            "new_value": {{"validation": "length:12", "format": "masked"}},
            "impact": "Aadhaar will now be masked in responses"
        }}
    ],
    "added_adapters": ["payment_upi_v1"],
    "removed_adapters": [],
    "compatibility_score": 0.85,
    "is_backward_compatible": true,
    "migration_notes": [
        "New UPI adapter requires additional credential setup",
        "Photo verification removal may affect existing workflows"
    ],
    "recommended_action": "safe_to_upgrade"
}}
```
"""


def get_extraction_prompt(document_text: str) -> str:
    """Get the formatted extraction prompt"""
    return REQUIREMENT_EXTRACTION_PROMPT.format(document_text=document_text)


def get_mapping_prompt(requirements_json: str, adapter_schema: str, adapter_id: str, adapter_version: str) -> str:
    """Get the formatted mapping prompt"""
    return FIELD_MAPPING_PROMPT.format(
        requirements_json=requirements_json,
        adapter_schema=adapter_schema,
        adapter_id=adapter_id,
        adapter_version=adapter_version
    )


def get_validation_prompt(config_json: str, requirements_json: str) -> str:
    """Get the formatted validation prompt"""
    return CONFIG_VALIDATION_PROMPT.format(
        config_json=config_json,
        requirements_json=requirements_json
    )


def get_simulation_prompt(config_json: str) -> str:
    """Get the formatted simulation scenario prompt"""
    return SIMULATION_SCENARIO_PROMPT.format(config_json=config_json)


def get_diff_prompt(config_a: str, config_b: str, version_a: str, version_b: str) -> str:
    """Get the formatted diff prompt"""
    return CONFIG_DIFF_PROMPT.format(
        config_a=config_a,
        config_b=config_b,
        version_a=version_a,
        version_b=version_b
    )
