"""Blood pressure analysis endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class BPReadingInput(BaseModel):
    systolic: float
    diastolic: float
    timestamp: Optional[str] = None


class BPRiskInput(BaseModel):
    readings: list[BPReadingInput]
    age: int = 40
    has_diabetes: bool = False
    has_ckd: bool = False
    has_cardiovascular_history: bool = False


@router.get("/blood-pressure/classify")
def classify_bp(systolic: float, diastolic: float):
    from app.services.blood_pressure import classify_reading, BPReading
    reading = BPReading(systolic=systolic, diastolic=diastolic)
    result = classify_reading(reading)
    return {
        "classification": result.classification.value,
        "systolic": result.systolic,
        "diastolic": result.diastolic,
        "pulse_pressure": result.pulse_pressure,
        "mean_arterial_pressure": result.mean_arterial_pressure,
        "description": result.description,
    }


@router.get("/blood-pressure/pulse-pressure")
def get_pulse_pressure(systolic: float, diastolic: float):
    from app.services.blood_pressure import calculate_pulse_pressure, interpret_pulse_pressure
    pp = calculate_pulse_pressure(systolic, diastolic)
    return {
        "pulse_pressure": pp,
        "interpretation": interpret_pulse_pressure(pp),
    }


@router.get("/blood-pressure/map")
def get_map(systolic: float, diastolic: float):
    from app.services.blood_pressure import calculate_map, interpret_map
    map_val = calculate_map(systolic, diastolic)
    return {
        "mean_arterial_pressure": map_val,
        "interpretation": interpret_map(map_val),
    }


@router.get("/blood-pressure/trends")
def bp_trends(readings_json: str):
    """Analyze BP trends. Pass readings as JSON-encoded list of {systolic, diastolic, timestamp?}."""
    import json
    from app.services.blood_pressure import analyze_trends, BPReading
    try:
        raw = json.loads(readings_json)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}
    readings = [BPReading(**r) for r in raw]
    result = analyze_trends(readings)
    if result is None:
        return {"error": "Need at least 3 readings for trend analysis"}
    return {
        "mean_systolic": result.mean_systolic,
        "mean_diastolic": result.mean_diastolic,
        "systolic_trend": result.systolic_trend,
        "diastolic_trend": result.diastolic_trend,
        "variability_systolic": result.variability_systolic,
        "variability_diastolic": result.variability_diastolic,
        "reading_count": result.reading_count,
        "classification_distribution": result.classification_distribution,
    }


@router.post("/blood-pressure/risk")
def assess_risk(body: BPRiskInput):
    from app.services.blood_pressure import assess_risk, BPReading
    readings = [BPReading(systolic=r.systolic, diastolic=r.diastolic, timestamp=r.timestamp) for r in body.readings]
    result = assess_risk(
        readings,
        age=body.age,
        has_diabetes=body.has_diabetes,
        has_ckd=body.has_ckd,
        has_cardiovascular_history=body.has_cardiovascular_history,
    )
    return {
        "overall_risk": result.overall_risk,
        "risk_score": result.risk_score,
        "factors": result.factors,
        "recommendation": result.recommendation,
    }
