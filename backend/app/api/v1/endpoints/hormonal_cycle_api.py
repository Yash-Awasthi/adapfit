"""Hormonal cycle tracking endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class SymptomInput(BaseModel):
    date: str
    symptom: str
    severity: int = 3


@router.get("/cycle/average-length")
def get_average_cycle_length(period_starts_json: str):
    """Calculate average cycle length. Pass period starts as JSON array of ISO dates."""
    import json
    from app.services.hormonal_cycle import average_cycle_length, calculate_cycle_lengths
    try:
        starts = json.loads(period_starts_json)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}
    lengths = calculate_cycle_lengths(starts)
    avg = average_cycle_length(starts)
    return {
        "average_cycle_length": avg,
        "individual_lengths": lengths,
        "data_points": len(lengths),
    }


@router.get("/cycle/predict")
def predict_cycle(period_starts_json: str):
    """Predict next cycle from historical period start dates."""
    import json
    from app.services.hormonal_cycle import predict_next_cycle
    try:
        starts = json.loads(period_starts_json)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}
    result = predict_next_cycle(starts)
    if result is None:
        return {"error": "Need at least 1 period start date"}
    return {
        "predicted_start": result.predicted_start,
        "predicted_end": result.predicted_end,
        "predicted_ovulation": result.predicted_ovulation,
        "fertile_window_start": result.fertile_window_start,
        "fertile_window_end": result.fertile_window_end,
        "predicted_cycle_length": result.predicted_cycle_length,
        "confidence": result.confidence,
        "based_on_cycles": result.based_on_cycles,
    }


@router.get("/cycle/phase")
def get_phase(cycle_start: str, cycle_length: int, current_date: str):
    """Detect current cycle phase."""
    from app.services.hormonal_cycle import detect_phase, get_phase_info
    phase = detect_phase(cycle_start, cycle_length, current_date)
    info = get_phase_info(phase)
    return {
        "phase": info.phase,
        "day_in_phase": info.day_in_phase,
        "days_remaining": info.days_remaining,
        "description": info.phase_description,
        "recommendations": info.recommendations,
    }


@router.get("/cycle/fertility")
def check_fertility(cycle_start: str, cycle_length: int, check_date: str):
    """Check if a date is in the fertile window."""
    from app.services.hormonal_cycle import is_fertile, is_peak_fertility
    fertile = is_fertile(cycle_start, cycle_length, check_date)
    peak = is_peak_fertility(cycle_start, cycle_length, check_date)
    return {
        "date": check_date,
        "is_fertile": fertile,
        "is_peak_fertility": peak,
    }


@router.post("/cycle/symptoms")
def analyze_symptoms(symptoms: list[SymptomInput], period_starts_json: str):
    """Analyze symptom patterns across cycle phases."""
    import json
    from app.services.hormonal_cycle import correlate_symptoms, SymptomEntry
    try:
        starts = json.loads(period_starts_json)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}

    entries = [SymptomEntry(date=s.date, symptom=s.symptom, severity=s.severity) for s in symptoms]
    correlations = correlate_symptoms(entries, starts)
    return {
        "correlations": [
            {
                "symptom": c.symptom,
                "most_common_phase": c.most_common_phase,
                "average_severity_by_phase": c.average_severity_by_phase,
                "correlation_strength": c.correlation_strength,
            }
            for c in correlations
        ],
    }
