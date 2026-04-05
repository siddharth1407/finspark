"""
Mock API responses for simulation engine
"""
import random
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class MockAPIResponses:
    """
    Mock API responses for testing integrations.
    Simulates real API behavior with configurable success rates.
    """

    def __init__(self, success_rate: float = 0.9):
        self.success_rate = success_rate
        self.call_count = 0
        self.responses = []

    def _should_succeed(self) -> bool:
        return random.random() < self.success_rate

    def _record_response(self, adapter: str, response: Dict) -> Dict:
        self.call_count += 1
        record = {
            "call_number": self.call_count,
            "adapter": adapter,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.responses.append(record)
        return response

    def kyc_aadhaar_verify(self, aadhaar: str, name: str) -> Dict[str, Any]:
        """Mock Aadhaar KYC verification."""
        if not aadhaar or len(aadhaar) != 12:
            return self._record_response("kyc_aadhaar", {
                "status": "error",
                "error_code": "INVALID_AADHAAR",
                "message": "Aadhaar must be 12 digits",
                "http_status": 400
            })

        if self._should_succeed():
            return self._record_response("kyc_aadhaar", {
                "status": "verified",
                "verification_id": str(uuid.uuid4()),
                "match_score": round(random.uniform(0.85, 0.99), 2),
                "verified_at": datetime.utcnow().isoformat(),
                "masked_aadhaar": f"XXXX-XXXX-{aadhaar[-4:]}",
                "verified_fields": ["name", "dob", "address"],
                "http_status": 200
            })
        else:
            return self._record_response("kyc_aadhaar", {
                "status": "failed",
                "error_code": "VERIFICATION_FAILED",
                "message": "Name mismatch or invalid details",
                "http_status": 422
            })

    def kyc_pan_verify(self, pan: str, name: str, dob: str) -> Dict[str, Any]:
        """Mock PAN verification."""
        import re
        if not pan or not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan):
            return self._record_response("kyc_pan", {
                "status": "error",
                "error_code": "INVALID_PAN",
                "message": "Invalid PAN format",
                "http_status": 400
            })

        if self._should_succeed():
            return self._record_response("kyc_pan", {
                "status": "verified",
                "pan_status": "active",
                "name_match": True,
                "dob_match": True,
                "http_status": 200
            })
        else:
            return self._record_response("kyc_pan", {
                "status": "failed",
                "pan_status": "inactive",
                "name_match": False,
                "http_status": 422
            })

    def payment_create_order(self, amount: int, currency: str = "INR") -> Dict[str, Any]:
        """Mock payment order creation."""
        if amount <= 0:
            return self._record_response("payment", {
                "status": "error",
                "error_code": "INVALID_AMOUNT",
                "message": "Amount must be positive",
                "http_status": 400
            })

        if self._should_succeed():
            return self._record_response("payment", {
                "id": f"order_{uuid.uuid4().hex[:16]}",
                "status": "created",
                "amount": amount,
                "amount_paid": 0,
                "currency": currency,
                "created_at": datetime.utcnow().isoformat(),
                "http_status": 200
            })
        else:
            return self._record_response("payment", {
                "status": "error",
                "error_code": "GATEWAY_ERROR",
                "message": "Payment gateway temporarily unavailable",
                "http_status": 503
            })

    def payment_capture(self, payment_id: str, amount: int) -> Dict[str, Any]:
        """Mock payment capture."""
        if self._should_succeed():
            return self._record_response("payment", {
                "id": payment_id,
                "status": "captured",
                "amount": amount,
                "captured_at": datetime.utcnow().isoformat(),
                "http_status": 200
            })
        else:
            return self._record_response("payment", {
                "status": "error",
                "error_code": "CAPTURE_FAILED",
                "message": "Payment capture failed",
                "http_status": 422
            })

    def gst_verify(self, gstin: str) -> Dict[str, Any]:
        """Mock GST verification."""
        import re
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not gstin or not re.match(pattern, gstin):
            return self._record_response("gst", {
                "status": "error",
                "error_code": "INVALID_GSTIN",
                "message": "Invalid GSTIN format",
                "http_status": 400
            })

        if self._should_succeed():
            return self._record_response("gst", {
                "gstin": gstin,
                "legal_name": "ACME CORP PRIVATE LIMITED",
                "trade_name": "ACME CORP",
                "status": "Active",
                "registration_date": "2018-07-01",
                "state": gstin[:2],
                "http_status": 200
            })
        else:
            return self._record_response("gst", {
                "status": "error",
                "error_code": "GSTIN_NOT_FOUND",
                "message": "GSTIN not found in records",
                "http_status": 404
            })

    def bank_verify(self, account: str, ifsc: str, name: str) -> Dict[str, Any]:
        """Mock bank account verification."""
        if not account or len(account) < 9:
            return self._record_response("banking", {
                "status": "error",
                "error_code": "INVALID_ACCOUNT",
                "message": "Invalid account number",
                "http_status": 400
            })

        if self._should_succeed():
            return self._record_response("banking", {
                "verified": True,
                "name_match_score": round(random.uniform(0.8, 1.0), 2),
                "bank_name": "STATE BANK OF INDIA",
                "branch": "MAIN BRANCH",
                "http_status": 200
            })
        else:
            return self._record_response("banking", {
                "verified": False,
                "error_code": "VERIFICATION_FAILED",
                "message": "Account verification failed",
                "http_status": 422
            })

    def execute_scenario(
        self,
        adapter_id: str,
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a test scenario against mock API."""
        input_data = scenario.get("input", {})

        # Route to appropriate mock
        if "aadhaar" in adapter_id:
            return self.kyc_aadhaar_verify(
                input_data.get("aadhaar_number", ""),
                input_data.get("name", "")
            )
        elif "pan" in adapter_id:
            return self.kyc_pan_verify(
                input_data.get("pan_number", ""),
                input_data.get("name", ""),
                input_data.get("dob", "")
            )
        elif "payment" in adapter_id or "razorpay" in adapter_id:
            return self.payment_create_order(
                input_data.get("amount", 0),
                input_data.get("currency", "INR")
            )
        elif "gst" in adapter_id:
            return self.gst_verify(input_data.get("gstin", ""))
        elif "bank" in adapter_id:
            return self.bank_verify(
                input_data.get("account_number", ""),
                input_data.get("ifsc", ""),
                input_data.get("name", "")
            )
        else:
            return {
                "status": "error",
                "error_code": "UNKNOWN_ADAPTER",
                "message": f"No mock configured for {adapter_id}",
                "http_status": 501
            }


# Global mock instance
_mock_api: Optional[MockAPIResponses] = None


def get_mock_api(success_rate: float = 0.9) -> MockAPIResponses:
    """Get or create mock API instance."""
    global _mock_api
    if _mock_api is None:
        _mock_api = MockAPIResponses(success_rate)
    return _mock_api
