"""
AI Pipeline - LLM Client
Supports HuggingFace Inference API and Mock client for testing
"""
import os
import json
import logging
import re
from typing import Literal
from tenacity import retry, stop_after_attempt, wait_exponential
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients"""

    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 4000) -> str:
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass


class HuggingFaceClient(LLMClient):
    """Hugging Face Inference API client using official huggingface_hub library"""

    def __init__(self, api_key: str, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        from huggingface_hub import InferenceClient
        self.client = InferenceClient(token=api_key)
        self.model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    async def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        import asyncio

        try:
            # Use chat_completion which is more widely supported
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat_completion(
                    messages=[
                        {"role": "system", "content": "You are an enterprise integration AI assistant. Always respond with valid JSON only, no explanations or markdown."},
                        {"role": "user", "content": prompt}
                    ],
                    model=self.model,
                    max_tokens=min(max_tokens, 2000),
                    temperature=0.1
                )
            )
            
            # Extract content from response
            content = response.choices[0].message.content
            return self._extract_json(content)

        except Exception as e:
            logger.error(f"HuggingFace API error: {e}")
            raise

    def _extract_json(self, text: str) -> str:
        """Extract JSON from model response"""
        # Try to find JSON in the response
        text = text.strip()
        
        # Remove markdown code blocks if present
        if "```json" in text:
            match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                text = match.group(1)
        elif "```" in text:
            match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                text = match.group(1)
        
        # Find JSON object or array
        json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if json_match:
            try:
                # Validate it's valid JSON
                json.loads(json_match.group(1))
                return json_match.group(1)
            except:
                pass
        
        return text

    def count_tokens(self, text: str) -> int:
        # Rough estimate
        return len(text) // 4


class MockLLMClient(LLMClient):
    """Mock LLM client for testing without API calls"""

    def __init__(self):
        self.call_count = 0

    async def generate(self, prompt: str, max_tokens: int = 4000) -> str:
        self.call_count += 1

        # Detect prompt type and return appropriate mock response
        if "EXTRACTION TASK" in prompt:
            return self._mock_extraction_response()
        elif "MAPPING RULES" in prompt:
            return self._mock_mapping_response()
        elif "VALIDATION TASK" in prompt:
            return self._mock_validation_response()
        elif "test_scenarios" in prompt.lower():
            return self._mock_simulation_response()
        else:
            return json.dumps({"mock": True, "message": "Mock response"})

    def count_tokens(self, text: str) -> int:
        return len(text) // 4

    def _mock_extraction_response(self) -> str:
        return json.dumps({
            "project_name": "Customer Onboarding Integration",
            "services": [
                {
                    "service_type": "kyc",
                    "service_name": "Aadhaar eKYC Verification",
                    "priority": "mandatory",
                    "description": "Verify customer identity using Aadhaar-based eKYC",
                    "api_endpoints": [
                        {"method": "POST", "path": "/v1/kyc/aadhaar/verify",
                            "description": "Initiate Aadhaar verification"}
                    ],
                    "required_fields": [
                        {"field_name": "aadhaar_number", "data_type": "string",
                            "description": "12-digit Aadhaar number"},
                        {"field_name": "full_name", "data_type": "string",
                            "description": "Full name as on Aadhaar"}
                    ],
                    "optional_fields": [
                        {"field_name": "mobile_number", "data_type": "string",
                            "description": "Mobile for OTP"}
                    ],
                    "constraints": ["Must complete within 30 seconds", "OTP expires in 10 minutes"]
                },
                {
                    "service_type": "payment",
                    "service_name": "Payment Gateway Integration",
                    "priority": "mandatory",
                    "description": "Process payments via multiple channels",
                    "api_endpoints": [
                        {"method": "POST", "path": "/v1/payments/initiate",
                            "description": "Initiate payment"}
                    ],
                    "required_fields": [
                        {"field_name": "amount", "data_type": "number",
                            "description": "Payment amount"},
                        {"field_name": "currency", "data_type": "string",
                            "description": "Currency code"}
                    ],
                    "optional_fields": [],
                    "constraints": ["PCI DSS compliance required"]
                }
            ],
            "integration_points": [
                {"source_system": "CRM", "target_system": "KYC Provider",
                    "data_exchanged": "Customer details", "frequency": "real-time"}
            ],
            "data_flows": [
                {"flow_name": "Customer Onboarding", "steps": [
                    "Collect details", "Verify KYC", "Activate account"], "systems_involved": ["Web App", "KYC", "Core Banking"]}
            ],
            "security_requirements": ["All PII encrypted at rest", "TLS 1.3 for transit"],
            "compliance_requirements": ["RBI KYC guidelines", "PCI DSS for payments"],
            "confidence_score": 0.89
        })

    def _mock_mapping_response(self) -> str:
        return json.dumps({
            "adapter_id": "kyc_aadhaar_v2",
            "adapter_name": "Aadhaar eKYC Adapter",
            "version": "2.0",
            "field_mappings": [
                {"source_field": "aadhaar_number", "target_field": "aadhaarId",
                    "transformation": "trim()", "is_required": True, "validation_rules": ["length:12", "numeric"]},
                {"source_field": "full_name", "target_field": "name", "transformation": "uppercase() | trim()",
                 "is_required": True, "validation_rules": ["max_length:100"]},
                {"source_field": "mobile_number", "target_field": "mobile",
                    "transformation": "trim()", "is_required": False, "validation_rules": ["length:10"]}
            ],
            "unmapped_source_fields": [],
            "unmapped_target_fields": ["consent_timestamp"],
            "mapping_confidence": 0.94,
            "notes": ["All required fields mapped successfully"]
        })

    def _mock_validation_response(self) -> str:
        return json.dumps({
            "is_valid": True,
            "validation_score": 0.92,
            "issues": [
                {"severity": "warning", "field": "adapters[0].timeout", "message": "Consider reducing timeout from 60s to 30s",
                    "suggestion": "Set timeout to 30 seconds for better UX"}
            ],
            "coverage": {"required_fields_mapped": 5, "required_fields_total": 5, "optional_fields_mapped": 2, "optional_fields_total": 3},
            "recommendations": ["Add retry logic for transient failures", "Consider circuit breaker pattern"],
            "security_check": {"pii_fields_identified": ["aadhaar_number"], "encryption_configured": True, "auth_configured": True}
        })

    def _mock_simulation_response(self) -> str:
        return json.dumps({
            "test_scenarios": [
                {"scenario_id": "TC001", "name": "Valid Aadhaar Verification", "adapter": "kyc_aadhaar_v2", "input": {
                    "aadhaar_number": "123456789012"}, "expected_http_status": 200},
                {"scenario_id": "TC002", "name": "Invalid Aadhaar", "adapter": "kyc_aadhaar_v2", "input": {
                    "aadhaar_number": "12345"}, "expected_http_status": 400}
            ],
            "coverage_summary": {"total_scenarios": 2, "happy_path": 1, "error_scenarios": 1}
        })


def get_llm_client(
    provider: Literal["huggingface", "mock"] = None,
    api_key: str = None,
    model: str = None
) -> LLMClient:
    """Factory function to get appropriate LLM client
    
    Providers:
        - huggingface: Hugging Face Inference API (requires HUGGINGFACE_API_KEY)
        - mock: Mock client for testing (no API key needed)
    
    Recommended free models:
        - Qwen/Qwen2.5-72B-Instruct (best quality, slower)
        - mistralai/Mistral-7B-Instruct-v0.2 (good balance)
    """

    # Use environment variables as defaults
    provider = provider or os.getenv("AI_PROVIDER", "huggingface")

    if provider == "huggingface":
        api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        model = model or os.getenv("AI_MODEL", "Qwen/Qwen2.5-72B-Instruct")
        if not api_key:
            logger.warning("No HuggingFace API key, falling back to mock client")
            return MockLLMClient()
        return HuggingFaceClient(api_key, model)
    else:
        return MockLLMClient()
