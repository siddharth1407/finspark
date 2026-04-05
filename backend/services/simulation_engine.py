"""
Simulation and testing engine for integration configurations
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4
import time

from adapters import get_mock_api
from ai_pipeline import get_ai_pipeline

logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Engine for simulating and testing integration configurations.
    Supports:
    - Test scenario execution
    - Version comparison
    - Rollback testing
    """

    def __init__(self, success_rate: float = 0.9):
        self.mock_api = get_mock_api(success_rate)
        self.ai_pipeline = get_ai_pipeline()
        self.simulation_history: List[Dict] = []

    async def run_simulation(
        self,
        config: Dict[str, Any],
        test_scenarios: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Run simulation against a configuration.

        Args:
            config: Integration configuration to test
            test_scenarios: Optional list of scenarios. If None, auto-generated.

        Returns:
            Simulation results
        """
        simulation_id = uuid4()
        start_time = time.time()

        logger.info(f"Starting simulation {simulation_id}")

        # Auto-generate scenarios if not provided
        if not test_scenarios:
            scenario_result = await self.ai_pipeline.generate_test_scenarios(config)
            test_scenarios = scenario_result.get("test_scenarios", [])

        # Execute each scenario
        results = []
        passed = 0
        failed = 0
        errors = []

        for scenario in test_scenarios:
            adapter_id = scenario.get("adapter", "")

            # Find adapter in config
            adapter_config = None
            for a in config.get("adapters", []):
                if a["adapter_id"] == adapter_id:
                    adapter_config = a
                    break

            # Execute scenario
            actual_response = self.mock_api.execute_scenario(
                adapter_id, scenario)
            expected_status = scenario.get("expected_http_status", 200)
            actual_status = actual_response.get("http_status", 500)

            scenario_passed = actual_status == expected_status

            result = {
                "scenario_id": scenario.get("scenario_id", str(uuid4())[:8]),
                "scenario_name": scenario.get("name", "Unnamed"),
                "adapter": adapter_id,
                "input": scenario.get("input", {}),
                "expected_status": expected_status,
                "actual_status": actual_status,
                "actual_response": actual_response,
                "passed": scenario_passed,
                # Simulated
                "execution_time_ms": int((time.time() - start_time) * 100)
            }

            results.append(result)

            if scenario_passed:
                passed += 1
            else:
                failed += 1
                errors.append({
                    "scenario": scenario.get("scenario_id"),
                    "expected": expected_status,
                    "actual": actual_status,
                    "message": actual_response.get("message", "Unknown error")
                })

        execution_time = int((time.time() - start_time) * 1000)

        # Generate recommendations based on results
        recommendations = self._generate_recommendations(results, errors)

        simulation_result = {
            "simulation_id": str(simulation_id),
            "config_id": config.get("config_id"),
            "status": "completed" if failed == 0 else "completed_with_failures",
            "scenarios_run": len(test_scenarios),
            "scenarios_passed": passed,
            "scenarios_failed": failed,
            "pass_rate": passed / len(test_scenarios) if test_scenarios else 0,
            "execution_time_ms": execution_time,
            "results": results,
            "errors": errors,
            "recommendations": recommendations,
            "executed_at": datetime.utcnow().isoformat()
        }

        # Store in history for rollback comparison
        self.simulation_history.append(simulation_result)

        return simulation_result

    def _generate_recommendations(
        self,
        results: List[Dict],
        errors: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on simulation results."""
        recommendations = []

        # Analyze error patterns
        error_codes = [e.get("actual", 0) for e in errors]

        if 400 in error_codes:
            recommendations.append("Add input validation for request payloads")

        if 401 in error_codes or 403 in error_codes:
            recommendations.append(
                "Verify authentication credentials are correctly configured")

        if 422 in error_codes:
            recommendations.append(
                "Check field mapping transformations for data format issues")

        if 500 in error_codes or 503 in error_codes:
            recommendations.append(
                "Implement circuit breaker pattern for server errors")
            recommendations.append("Add retry logic with exponential backoff")

        if any(r.get("execution_time_ms", 0) > 5000 for r in results):
            recommendations.append(
                "Consider increasing timeout values or implementing async processing")

        # General recommendations
        pass_rate = sum(1 for r in results if r.get(
            "passed")) / len(results) if results else 0

        if pass_rate < 0.9:
            recommendations.append(
                "Review failed scenarios and update field mappings")

        if not recommendations:
            recommendations.append(
                "All tests passed! Configuration is ready for deployment.")

        return recommendations

    async def compare_versions(
        self,
        config_v1: Dict[str, Any],
        config_v2: Dict[str, Any],
        scenarios: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Compare simulation results between two config versions.
        """
        logger.info("Running version comparison simulation")

        # Run simulations for both versions
        result_v1 = await self.run_simulation(config_v1, scenarios)
        result_v2 = await self.run_simulation(config_v2, scenarios)

        comparison = {
            "version_a": {
                "config_version": config_v1.get("version"),
                "pass_rate": result_v1.get("pass_rate"),
                "execution_time_ms": result_v1.get("execution_time_ms")
            },
            "version_b": {
                "config_version": config_v2.get("version"),
                "pass_rate": result_v2.get("pass_rate"),
                "execution_time_ms": result_v2.get("execution_time_ms")
            },
            "regression_detected": result_v2.get("pass_rate", 0) < result_v1.get("pass_rate", 0),
            "performance_change": {
                "time_diff_ms": result_v2.get("execution_time_ms", 0) - result_v1.get("execution_time_ms", 0),
                "is_faster": result_v2.get("execution_time_ms", 0) < result_v1.get("execution_time_ms", 0)
            },
            "recommendation": "safe_to_upgrade" if result_v2.get("pass_rate", 0) >= result_v1.get("pass_rate", 0) else "review_before_upgrade"
        }

        return comparison

    def get_rollback_point(
        self,
        config_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find the last successful simulation for rollback.
        """
        for sim in reversed(self.simulation_history):
            if sim.get("config_id") == config_id and sim.get("status") == "completed":
                return sim
        return None

    def validate_rollback(
        self,
        current_config: Dict[str, Any],
        rollback_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that rollback is safe.
        """
        # Check adapter compatibility
        current_adapters = {a["adapter_id"]
                            for a in current_config.get("adapters", [])}
        rollback_adapters = {a["adapter_id"]
                             for a in rollback_config.get("adapters", [])}

        new_adapters = current_adapters - rollback_adapters

        return {
            "is_safe": len(new_adapters) == 0,
            "warning": f"Rolling back will remove {len(new_adapters)} new adapters" if new_adapters else None,
            "affected_adapters": list(new_adapters),
            "rollback_version": rollback_config.get("version"),
            "current_version": current_config.get("version")
        }


# Singleton
_simulation_engine: Optional[SimulationEngine] = None


def get_simulation_engine() -> SimulationEngine:
    global _simulation_engine
    if _simulation_engine is None:
        _simulation_engine = SimulationEngine()
    return _simulation_engine
