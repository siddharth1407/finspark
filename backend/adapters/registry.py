"""
Integration Adapter Registry - Prebuilt Adapters
Contains mock adapters for KYC, Payment, and GST services
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


# =====================================================
# ADAPTER DEFINITIONS
# =====================================================

ADAPTERS_REGISTRY: Dict[str, Dict[str, Any]] = {
    # -------------------- KYC ADAPTERS --------------------
    "kyc_aadhaar_v1": {
        "adapter_id": "kyc_aadhaar_v1",
        "name": "Aadhaar eKYC Adapter",
        "service_type": "kyc",
        "version": "1.0",
        "supported_versions": ["1.0"],
        "description": "UIDAI Aadhaar-based eKYC verification (Legacy)",
        "base_url_template": "https://api.uidai.gov.in/v1",
        "auth_types": ["api_key", "oauth2"],
        "endpoints": [
            {
                "name": "verify",
                "method": "POST",
                "path": "/kyc/verify",
                "description": "Verify Aadhaar with OTP"
            },
            {
                "name": "generate_otp",
                "method": "POST",
                "path": "/kyc/otp/generate",
                "description": "Generate OTP for Aadhaar"
            }
        ],
        "field_schema": {
            "required": {
                "aadhaarId": {"type": "string", "length": 12, "description": "12-digit Aadhaar number"},
                "name": {"type": "string", "max_length": 100, "description": "Full name as on Aadhaar"},
                "consent": {"type": "boolean", "description": "User consent for verification"}
            },
            "optional": {
                "mobile": {"type": "string", "length": 10, "description": "Mobile number for OTP"},
                "email": {"type": "string", "description": "Email for notifications"}
            },
            "response": {
                "status": {"type": "string", "enum": ["success", "failed", "pending"]},
                "verification_id": {"type": "string"},
                "match_score": {"type": "number", "min": 0, "max": 100},
                "verified_fields": {"type": "array"}
            }
        },
        "rate_limits": {"requests_per_minute": 100, "requests_per_day": 10000},
        "is_active": True
    },

    "kyc_aadhaar_v2": {
        "adapter_id": "kyc_aadhaar_v2",
        "name": "Aadhaar eKYC Adapter v2",
        "service_type": "kyc",
        "version": "2.0",
        "supported_versions": ["1.0", "2.0"],
        "description": "Enhanced UIDAI Aadhaar eKYC with biometric support",
        "base_url_template": "https://api.uidai.gov.in/v2",
        "auth_types": ["oauth2", "mutual_tls"],
        "endpoints": [
            {
                "name": "verify_otp",
                "method": "POST",
                "path": "/kyc/verify/otp",
                "description": "OTP-based verification"
            },
            {
                "name": "verify_biometric",
                "method": "POST",
                "path": "/kyc/verify/biometric",
                "description": "Biometric verification"
            },
            {
                "name": "generate_otp",
                "method": "POST",
                "path": "/otp/generate",
                "description": "Generate OTP"
            },
            {
                "name": "get_status",
                "method": "GET",
                "path": "/kyc/status/{verification_id}",
                "description": "Check verification status"
            }
        ],
        "field_schema": {
            "required": {
                "aadhaarId": {"type": "string", "pattern": "^[0-9]{12}$", "description": "12-digit Aadhaar"},
                "name": {"type": "string", "max_length": 100},
                "consent": {"type": "boolean"},
                "consent_timestamp": {"type": "datetime", "description": "When consent was given"}
            },
            "optional": {
                "mobile": {"type": "string", "pattern": "^[6-9][0-9]{9}$"},
                "email": {"type": "string", "format": "email"},
                "dob": {"type": "date", "description": "Date of birth"},
                "address": {"type": "object", "properties": ["line1", "line2", "city", "state", "pincode"]}
            },
            "response": {
                "status": {"type": "string", "enum": ["verified", "failed", "pending", "expired"]},
                "verification_id": {"type": "string", "format": "uuid"},
                "match_score": {"type": "number", "min": 0, "max": 1},
                "verified_at": {"type": "datetime"},
                "masked_aadhaar": {"type": "string", "description": "XXXX-XXXX-1234 format"}
            }
        },
        "rate_limits": {"requests_per_minute": 200, "requests_per_day": 50000},
        "is_active": True
    },

    "kyc_pan_v1": {
        "adapter_id": "kyc_pan_v1",
        "name": "PAN Verification Adapter",
        "service_type": "kyc",
        "version": "1.0",
        "supported_versions": ["1.0"],
        "description": "Income Tax PAN verification via NSDL",
        "base_url_template": "https://api.nsdl.co.in/pan/v1",
        "auth_types": ["api_key"],
        "endpoints": [
            {
                "name": "verify",
                "method": "POST",
                "path": "/verify",
                "description": "Verify PAN details"
            },
            {
                "name": "fetch_details",
                "method": "GET",
                "path": "/details/{pan}",
                "description": "Fetch PAN holder details"
            }
        ],
        "field_schema": {
            "required": {
                "panNumber": {"type": "string", "pattern": "^[A-Z]{5}[0-9]{4}[A-Z]$"},
                "name": {"type": "string"},
                "dob": {"type": "date", "description": "Date of birth for validation"}
            },
            "optional": {
                "fatherName": {"type": "string"}
            },
            "response": {
                "status": {"type": "string"},
                "name_match": {"type": "boolean"},
                "dob_match": {"type": "boolean"},
                "pan_status": {"type": "string", "enum": ["active", "inactive", "deactivated"]}
            }
        },
        "rate_limits": {"requests_per_minute": 60},
        "is_active": True
    },

    # -------------------- PAYMENT ADAPTERS --------------------
    "payment_razorpay_v1": {
        "adapter_id": "payment_razorpay_v1",
        "name": "Razorpay Payment Gateway",
        "service_type": "payment",
        "version": "1.0",
        "supported_versions": ["1.0"],
        "description": "Razorpay payment processing",
        "base_url_template": "https://api.razorpay.com/v1",
        "auth_types": ["basic_auth"],
        "endpoints": [
            {
                "name": "create_order",
                "method": "POST",
                "path": "/orders",
                "description": "Create payment order"
            },
            {
                "name": "capture_payment",
                "method": "POST",
                "path": "/payments/{payment_id}/capture",
                "description": "Capture authorized payment"
            },
            {
                "name": "refund",
                "method": "POST",
                "path": "/payments/{payment_id}/refund",
                "description": "Initiate refund"
            }
        ],
        "field_schema": {
            "required": {
                "amount": {"type": "integer", "description": "Amount in smallest unit (paise)"},
                "currency": {"type": "string", "enum": ["INR", "USD"], "default": "INR"},
                "receipt": {"type": "string", "description": "Unique receipt ID"}
            },
            "optional": {
                "notes": {"type": "object", "description": "Custom key-value pairs"},
                "customer_id": {"type": "string"}
            },
            "response": {
                "id": {"type": "string", "description": "Order/Payment ID"},
                "status": {"type": "string", "enum": ["created", "authorized", "captured", "refunded", "failed"]},
                "amount": {"type": "integer"},
                "amount_paid": {"type": "integer"}
            }
        },
        "rate_limits": {"requests_per_second": 25},
        "is_active": True
    },

    "payment_upi_v1": {
        "adapter_id": "payment_upi_v1",
        "name": "UPI Payment Adapter",
        "service_type": "payment",
        "version": "1.0",
        "supported_versions": ["1.0"],
        "description": "Unified Payments Interface integration",
        "base_url_template": "https://api.npci.org.in/upi/v1",
        "auth_types": ["oauth2", "digital_signature"],
        "endpoints": [
            {
                "name": "collect",
                "method": "POST",
                "path": "/collect",
                "description": "Initiate UPI collect request"
            },
            {
                "name": "pay",
                "method": "POST",
                "path": "/pay",
                "description": "Initiate UPI payment"
            },
            {
                "name": "status",
                "method": "GET",
                "path": "/status/{txn_id}",
                "description": "Check transaction status"
            }
        ],
        "field_schema": {
            "required": {
                "vpa": {"type": "string", "pattern": "^[a-zA-Z0-9._-]+@[a-zA-Z]+$", "description": "UPI ID"},
                "amount": {"type": "number", "min": 1, "max": 100000},
                "txnNote": {"type": "string", "max_length": 50}
            },
            "optional": {
                "expiry": {"type": "integer", "description": "Validity in minutes"},
                "merchantId": {"type": "string"}
            },
            "response": {
                "txnId": {"type": "string"},
                "status": {"type": "string", "enum": ["PENDING", "SUCCESS", "FAILED", "EXPIRED"]},
                "rrn": {"type": "string", "description": "Bank reference number"}
            }
        },
        "rate_limits": {"requests_per_minute": 1000},
        "is_active": True
    },

    # -------------------- GST ADAPTERS --------------------
    "gst_verification_v1": {
        "adapter_id": "gst_verification_v1",
        "name": "GST Verification Adapter",
        "service_type": "gst",
        "version": "1.0",
        "supported_versions": ["1.0"],
        "description": "GSTN verification and filing",
        "base_url_template": "https://api.gst.gov.in/v1",
        "auth_types": ["api_key", "oauth2"],
        "endpoints": [
            {
                "name": "verify_gstin",
                "method": "GET",
                "path": "/gstin/{gstin}",
                "description": "Verify GSTIN details"
            },
            {
                "name": "file_return",
                "method": "POST",
                "path": "/returns/file",
                "description": "File GST return"
            },
            {
                "name": "get_return_status",
                "method": "GET",
                "path": "/returns/status/{reference_id}",
                "description": "Check filing status"
            }
        ],
        "field_schema": {
            "required": {
                "gstin": {"type": "string", "pattern": "^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"},
                "financialYear": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}$"}
            },
            "optional": {
                "returnType": {"type": "string", "enum": ["GSTR1", "GSTR3B", "GSTR9"]},
                "period": {"type": "string"}
            },
            "response": {
                "gstin": {"type": "string"},
                "legal_name": {"type": "string"},
                "trade_name": {"type": "string"},
                "status": {"type": "string", "enum": ["Active", "Inactive", "Cancelled"]},
                "registration_date": {"type": "date"}
            }
        },
        "rate_limits": {"requests_per_minute": 30},
        "is_active": True
    },

    # -------------------- BANKING ADAPTERS --------------------
    "banking_account_v1": {
        "adapter_id": "banking_account_v1",
        "name": "Bank Account Verification",
        "service_type": "banking",
        "version": "1.0",
        "supported_versions": ["1.0"],
        "description": "Penny drop and account verification",
        "base_url_template": "https://api.bankverify.in/v1",
        "auth_types": ["api_key"],
        "endpoints": [
            {
                "name": "verify_account",
                "method": "POST",
                "path": "/account/verify",
                "description": "Verify bank account via penny drop"
            },
            {
                "name": "get_ifsc",
                "method": "GET",
                "path": "/ifsc/{code}",
                "description": "Get bank details from IFSC"
            }
        ],
        "field_schema": {
            "required": {
                "accountNumber": {"type": "string", "min_length": 9, "max_length": 18},
                "ifscCode": {"type": "string", "pattern": "^[A-Z]{4}0[A-Z0-9]{6}$"},
                "accountHolderName": {"type": "string"}
            },
            "optional": {
                "accountType": {"type": "string", "enum": ["savings", "current"]}
            },
            "response": {
                "verified": {"type": "boolean"},
                "name_match_score": {"type": "number"},
                "bank_name": {"type": "string"},
                "branch": {"type": "string"}
            }
        },
        "rate_limits": {"requests_per_minute": 50},
        "is_active": True
    }
}


class AdapterRegistry:
    """
    Integration Adapter Registry with version management.
    """

    def __init__(self):
        self.adapters = ADAPTERS_REGISTRY.copy()

    def get_adapter(self, adapter_id: str) -> Optional[Dict[str, Any]]:
        """Get adapter by ID."""
        return self.adapters.get(adapter_id)

    def get_adapters_by_type(self, service_type: str) -> List[Dict[str, Any]]:
        """Get all adapters for a service type."""
        return [a for a in self.adapters.values() if a["service_type"] == service_type]

    def get_latest_adapter(self, service_type: str) -> Optional[Dict[str, Any]]:
        """Get the latest version adapter for a service type."""
        adapters = self.get_adapters_by_type(service_type)
        if not adapters:
            return None
        return max(adapters, key=lambda a: a["version"])

    def list_all_adapters(self) -> List[Dict[str, Any]]:
        """List all available adapters."""
        return list(self.adapters.values())

    def get_field_schema(self, adapter_id: str) -> Optional[Dict[str, Any]]:
        """Get field schema for an adapter."""
        adapter = self.get_adapter(adapter_id)
        return adapter.get("field_schema") if adapter else None

    def check_version_compatibility(
        self,
        adapter_id: str,
        required_version: str
    ) -> Dict[str, Any]:
        """Check if adapter supports required version."""
        adapter = self.get_adapter(adapter_id)
        if not adapter:
            return {"compatible": False, "reason": "Adapter not found"}

        supported = adapter.get("supported_versions", [])
        if required_version in supported:
            return {
                "compatible": True,
                "adapter_version": adapter["version"],
                "required_version": required_version
            }

        return {
            "compatible": False,
            "reason": f"Version {required_version} not supported",
            "supported_versions": supported
        }

    def get_migration_path(
        self,
        from_adapter: str,
        to_adapter: str
    ) -> Dict[str, Any]:
        """Get migration path between adapter versions."""
        source = self.get_adapter(from_adapter)
        target = self.get_adapter(to_adapter)

        if not source or not target:
            return {"possible": False, "reason": "Adapter not found"}

        if source["service_type"] != target["service_type"]:
            return {"possible": False, "reason": "Different service types"}

        # Simple migration analysis
        source_fields = set(source["field_schema"].get("required", {}).keys())
        target_fields = set(target["field_schema"].get("required", {}).keys())

        return {
            "possible": True,
            "from_version": source["version"],
            "to_version": target["version"],
            "new_required_fields": list(target_fields - source_fields),
            "removed_fields": list(source_fields - target_fields),
            "breaking_changes": len(target_fields - source_fields) > 0
        }


# Global registry instance
_registry: Optional[AdapterRegistry] = None


def get_adapter_registry() -> AdapterRegistry:
    """Get or create adapter registry singleton."""
    global _registry
    if _registry is None:
        _registry = AdapterRegistry()
    return _registry
