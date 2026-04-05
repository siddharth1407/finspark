"""
Simulations API - Run tests and compare versions
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from services import get_simulation_engine, get_audit_logger, get_tenant_manager
from api.configurations import configurations_store

router = APIRouter()

# In-memory storage
simulations_store = {}


class RunSimulationRequest(BaseModel):
    config_id: str
    tenant_id: str = "tenant_demo"
    test_scenarios: Optional[List[dict]] = None


class CompareVersionsRequest(BaseModel):
    config_id_v1: str
    config_id_v2: str
    tenant_id: str = "tenant_demo"
    scenarios: Optional[List[dict]] = None


@router.post("/simulations/run")
async def run_simulation(request: RunSimulationRequest):
    """
    Run simulation tests against a configuration.

    Features:
    - Auto-generates test scenarios if not provided
    - Tests against mock APIs
    - Provides pass/fail rates and recommendations
    """
    # Validate tenant
    tenant_manager = get_tenant_manager()
    if not tenant_manager.validate_tenant(request.tenant_id):
        raise HTTPException(
            status_code=403, detail="Invalid or inactive tenant")

    # Get configuration
    config = configurations_store.get(request.config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    if config["tenant_id"] != request.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Run simulation
    simulation_engine = get_simulation_engine()

    try:
        result = await simulation_engine.run_simulation(
            config=config,
            test_scenarios=request.test_scenarios
        )

        # Store simulation
        sim_id = result["simulation_id"]
        result["tenant_id"] = request.tenant_id
        simulations_store[sim_id] = result

        # Audit log
        audit = get_audit_logger()
        audit.log(
            tenant_id=request.tenant_id,
            action="simulate",
            resource_type="simulation",
            resource_id=sim_id,
            actor="api_user",
            details={
                "config_id": request.config_id,
                "scenarios_run": result["scenarios_run"],
                "pass_rate": result["pass_rate"]
            }
        )

        return {
            "success": True,
            "simulation_id": sim_id,
            "status": result["status"],
            "summary": {
                "scenarios_run": result["scenarios_run"],
                "passed": result["scenarios_passed"],
                "failed": result["scenarios_failed"],
                "pass_rate": round(result["pass_rate"] * 100, 1)
            },
            "execution_time_ms": result["execution_time_ms"],
            "results": result["results"],
            "errors": result["errors"],
            "recommendations": result["recommendations"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Simulation failed: {str(e)}")


@router.get("/simulations/{simulation_id}")
async def get_simulation(simulation_id: str, tenant_id: str = "tenant_demo"):
    """Get simulation results by ID."""
    simulation = simulations_store.get(simulation_id)

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if simulation.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return simulation


@router.get("/simulations")
async def list_simulations(tenant_id: str = "tenant_demo", config_id: Optional[str] = None):
    """List all simulations for a tenant."""
    sims = [
        {
            "simulation_id": s["simulation_id"],
            "config_id": s["config_id"],
            "status": s["status"],
            "pass_rate": round(s["pass_rate"] * 100, 1),
            "scenarios_run": s["scenarios_run"],
            "executed_at": s["executed_at"]
        }
        for s in simulations_store.values()
        if s.get("tenant_id") == tenant_id and (config_id is None or s["config_id"] == config_id)
    ]
    return {"simulations": sims, "count": len(sims)}


@router.post("/simulations/compare-versions")
async def compare_versions(request: CompareVersionsRequest):
    """
    Compare simulation results between two configuration versions.
    Helps identify regressions before deployment.
    """
    config_v1 = configurations_store.get(request.config_id_v1)
    config_v2 = configurations_store.get(request.config_id_v2)

    if not config_v1 or not config_v2:
        raise HTTPException(
            status_code=404, detail="One or both configurations not found")

    if config_v1["tenant_id"] != request.tenant_id or config_v2["tenant_id"] != request.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    simulation_engine = get_simulation_engine()

    try:
        comparison = await simulation_engine.compare_versions(
            config_v1=config_v1,
            config_v2=config_v2,
            scenarios=request.scenarios
        )

        return {
            "success": True,
            "comparison": comparison,
            "recommendation": comparison["recommendation"],
            "regression_detected": comparison["regression_detected"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/simulations/{config_id}/validate-rollback/{target_config_id}")
async def validate_rollback(config_id: str, target_config_id: str, tenant_id: str = "tenant_demo"):
    """Validate if rollback is safe."""
    current = configurations_store.get(config_id)
    target = configurations_store.get(target_config_id)

    if not current or not target:
        raise HTTPException(status_code=404, detail="Configuration not found")

    simulation_engine = get_simulation_engine()
    validation = simulation_engine.validate_rollback(current, target)

    return validation
