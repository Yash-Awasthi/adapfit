"""Early Warning Score System for Health Deterioration.

Extracted from deterioration-prediction (inspiration).
Implements NEWS (National Early Warning Score) and modified CEWS
for detecting patient deterioration from vital signs.

All pure functions — no DB, no async.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VitalSigns:
    """Patient vital signs for EWS calculation."""
    heart_rate: Optional[float] = None  # bpm
    respiratory_rate: Optional[float] = None  # breaths/min
    temperature: Optional[float] = None  # Celsius
    oxygen_saturation: Optional[float] = None  # %
    systolic_bp: Optional[float] = None  # mmHg
    avpu: Optional[int] = None  # 0=A, 1=V, 2=P, 3=U
    supplemental_oxygen: bool = False


@dataclass
class EWSScore:
    """Early Warning Score result."""
    total_score: int = 0
    component_scores: dict = field(default_factory=dict)
    risk_level: str = "low"
    clinical_response: str = ""
    missing_vitals: list = field(default_factory=list)


# NEWS1 Thresholds
# Format: [(min, max, score), ...] for each variable
NEWS_THRESHOLDS = {
    "heart_rate": [
        (-1, 40, 3),
        (41, 50, 1),
        (51, 90, 0),
        (91, 110, 1),
        (111, 130, 2),
        (131, 500, 3),
    ],
    "respiratory_rate": [
        (-1, 8, 3),
        (9, 11, 1),
        (12, 20, 0),
        (21, 24, 2),
        (25, 70, 3),
    ],
    "temperature": [
        (-1, 35.0, 3),
        (35.1, 36.0, 1),
        (36.1, 38.0, 0),
        (38.1, 39.0, 1),
        (39.1, 50.0, 2),
    ],
    "oxygen_saturation": [
        (-1, 91, 3),
        (92, 93, 2),
        (94, 95, 1),
        (96, 101, 0),
    ],
    "systolic_bp": [
        (-1, 90, 3),
        (91, 100, 2),
        (101, 110, 1),
        (111, 219, 0),
        (220, 400, 3),
    ],
    "supplemental_oxygen": [
        (0, 0, 0),  # No oxygen
        (1, 1, 2),  # On oxygen
    ],
    "avpu": [
        (-1, 0, 0),  # Alert
        (1, 1, 0),   # Voice
        (2, 2, 3),   # Pain
        (3, 3, 3),   # Unresponsive
    ],
}


def score_vital(value: float, thresholds: list[tuple]) -> int:
    """Score a single vital sign against thresholds.

    Args:
        value: Vital sign value
        thresholds: List of (min, max, score) tuples

    Returns:
        EWS score for this vital sign
    """
    for min_val, max_val, score in thresholds:
        if min_val < value <= max_val:
            return score
    # Check open-ended ranges
    if value <= thresholds[0][1]:
        return thresholds[0][2]
    if value >= thresholds[-1][0]:
        return thresholds[-1][2]
    return 0


def calculate_news(vitals: VitalSigns) -> EWSScore:
    """Calculate National Early Warning Score (NEWS).

    Based on the Royal College of Physicians NEWS system.

    Args:
        vitals: Patient vital signs

    Returns:
        EWSScore with total score, component scores, and risk level
    """
    component_scores = {}
    missing = []

    # Score each available vital sign
    if vitals.heart_rate is not None:
        component_scores["heart_rate"] = score_vital(
            vitals.heart_rate, NEWS_THRESHOLDS["heart_rate"]
        )
    else:
        missing.append("heart_rate")

    if vitals.respiratory_rate is not None:
        component_scores["respiratory_rate"] = score_vital(
            vitals.respiratory_rate, NEWS_THRESHOLDS["respiratory_rate"]
        )
    else:
        missing.append("respiratory_rate")

    if vitals.temperature is not None:
        component_scores["temperature"] = score_vital(
            vitals.temperature, NEWS_THRESHOLDS["temperature"]
        )
    else:
        missing.append("temperature")

    if vitals.oxygen_saturation is not None:
        component_scores["oxygen_saturation"] = score_vital(
            vitals.oxygen_saturation, NEWS_THRESHOLDS["oxygen_saturation"]
        )
    else:
        missing.append("oxygen_saturation")

    if vitals.systolic_bp is not None:
        component_scores["systolic_bp"] = score_vital(
            vitals.systolic_bp, NEWS_THRESHOLDS["systolic_bp"]
        )
    else:
        missing.append("systolic_bp")

    # Supplemental oxygen
    oxygen_score = 2 if vitals.supplemental_oxygen else 0
    component_scores["supplemental_oxygen"] = oxygen_score

    # AVPU
    if vitals.avpu is not None:
        component_scores["avpu"] = score_vital(
            vitals.avpu, NEWS_THRESHOLDS["avpu"]
        )
    else:
        missing.append("avpu")

    total = sum(component_scores.values())

    # Risk classification and clinical response
    if total == 0:
        risk = "low"
        response = "Continue routine monitoring"
    elif total <= 2:
        risk = "low"
        response = "Assess by competent registered nurse; decide frequency of monitoring"
    elif total <= 4:
        risk = "low-medium"
        response = "Urgent assessment by nurse or clinician with competence in acute illness"
    elif total <= 6:
        risk = "medium"
        response = "Emergency assessment by clinical/outreach team or critical care outreach"
    else:
        risk = "high"
        response = "Emergency assessment by critical care team; consider transfer to higher care"

    # Individual parameter scoring 3 always triggers urgent response
    any_3 = any(v == 3 for v in component_scores.values())
    if any_3 and total < 4:
        risk = "medium"
        response = "Urgent assessment — at least one parameter scored 3"

    return EWSScore(
        total_score=total,
        component_scores=component_scores,
        risk_level=risk,
        clinical_response=response,
        missing_vitals=missing,
    )


def calculate_cews(vitals: VitalSigns) -> EWSScore:
    """Calculate Centile-based Early Warning Score (CEWS).

    Simplified CEWS without supplemental oxygen and AVPU.

    Args:
        vitals: Patient vital signs

    Returns:
        EWSScore with total score and risk level
    """
    component_scores = {}
    missing = []

    if vitals.heart_rate is not None:
        component_scores["heart_rate"] = score_vital(
            vitals.heart_rate, NEWS_THRESHOLDS["heart_rate"]
        )
    else:
        missing.append("heart_rate")

    if vitals.respiratory_rate is not None:
        component_scores["respiratory_rate"] = score_vital(
            vitals.respiratory_rate, NEWS_THRESHOLDS["respiratory_rate"]
        )
    else:
        missing.append("respiratory_rate")

    if vitals.temperature is not None:
        component_scores["temperature"] = score_vital(
            vitals.temperature, NEWS_THRESHOLDS["temperature"]
        )
    else:
        missing.append("temperature")

    if vitals.oxygen_saturation is not None:
        component_scores["oxygen_saturation"] = score_vital(
            vitals.oxygen_saturation, NEWS_THRESHOLDS["oxygen_saturation"]
        )
    else:
        missing.append("oxygen_saturation")

    if vitals.systolic_bp is not None:
        component_scores["systolic_bp"] = score_vital(
            vitals.systolic_bp, NEWS_THRESHOLDS["systolic_bp"]
        )
    else:
        missing.append("systolic_bp")

    total = sum(component_scores.values())

    if total == 0:
        risk = "low"
        response = "Routine monitoring"
    elif total <= 2:
        risk = "low"
        response = "Assess and decide monitoring frequency"
    elif total <= 4:
        risk = "medium"
        response = "Urgent clinical assessment"
    else:
        risk = "high"
        response = "Emergency response; consider ICU admission"

    return EWSScore(
        total_score=total,
        component_scores=component_scores,
        risk_level=risk,
        clinical_response=response,
        missing_vitals=missing,
    )


def calculate_trend_score(
    scores: list[EWSScore],
    window: int = 3,
) -> dict:
    """Analyze EWS trend over time.

    Detects rising, falling, or stable patterns.

    Args:
        scores: Chronological list of EWS scores
        window: Number of recent scores to analyze

    Returns:
        Trend analysis with direction, rate of change, and alert
    """
    if len(scores) < 2:
        return {
            "direction": "insufficient_data",
            "rate_of_change": 0.0,
            "alert": False,
        }

    recent = scores[-window:] if len(scores) >= window else scores
    values = [s.total_score for s in recent]

    # Calculate trend
    if len(values) >= 2:
        changes = [values[i] - values[i - 1] for i in range(1, len(values))]
        avg_change = sum(changes) / len(changes)
    else:
        avg_change = 0.0

    # Direction
    if avg_change > 0.5:
        direction = "rising"
    elif avg_change < -0.5:
        direction = "falling"
    else:
        direction = "stable"

    # Alert if score is rising and crossing threshold
    alert = (
        direction == "rising"
        and values[-1] >= 4
        and avg_change > 1.0
    )

    return {
        "direction": direction,
        "rate_of_change": round(avg_change, 2),
        "alert": alert,
        "latest_score": values[-1],
        "scores_analyzed": len(values),
    }


def calculate_aggregate_risk(
    scores: list[EWSScore],
) -> dict:
    """Calculate aggregate risk from a series of EWS scores.

    Args:
        scores: List of EWS scores over time

    Returns:
        Aggregate risk assessment
    """
    if not scores:
        return {"risk_level": "unknown", "mean_score": 0.0, "max_score": 0}

    values = [s.total_score for s in scores]
    mean_score = sum(values) / len(values)
    max_score = max(values)
    high_risk_count = sum(1 for s in scores if s.risk_level == "high")
    medium_risk_count = sum(1 for s in scores if s.risk_level in ("medium", "low-medium"))

    # Aggregate risk
    if high_risk_count > 0:
        risk = "high"
    elif medium_risk_count > len(scores) * 0.3:
        risk = "medium"
    elif mean_score >= 3:
        risk = "medium"
    else:
        risk = "low"

    return {
        "risk_level": risk,
        "mean_score": round(mean_score, 2),
        "max_score": max_score,
        "total_assessments": len(scores),
        "high_risk_episodes": high_risk_count,
        "medium_risk_episodes": medium_risk_count,
    }


def generate_monitoring_recommendation(score: EWSScore) -> dict:
    """Generate monitoring frequency recommendation based on EWS.

    Args:
        score: Current EWS score

    Returns:
        Monitoring recommendation with frequency and escalation
    """
    if score.total_score == 0:
        return {
            "frequency_hours": 12,
            "escalation": False,
            "nurse_review": False,
            "description": "Routine 12-hourly observations",
        }
    elif score.total_score <= 2:
        return {
            "frequency_hours": 6,
            "escalation": False,
            "nurse_review": True,
            "description": "6-hourly observations; nurse assessment",
        }
    elif score.total_score <= 4:
        return {
            "frequency_hours": 1,
            "escalation": True,
            "nurse_review": True,
            "description": "1-2 hourly observations; urgent clinical review",
        }
    elif score.total_score <= 6:
        return {
            "frequency_hours": 0.5,
            "escalation": True,
            "nurse_review": True,
            "description": "Continuous monitoring; emergency team assessment",
        }
    else:
        return {
            "frequency_hours": 0,
            "escalation": True,
            "nurse_review": True,
            "description": "Immediate critical care response; continuous monitoring",
        }
