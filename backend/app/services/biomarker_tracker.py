"""Biomarker Tracker — Bloodwork Analysis and Trend Detection.

Extracted from biomarkerdash (inspiration).
Parses bloodwork data, tracks biomarker trends over time,
analyzes reference ranges, and detects abnormal values.

All pure functions — no DB, no async, no pandas dependency.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Biomarker:
    """A single biomarker with metadata and history."""
    name: str
    description: str = ""
    unit: str = ""
    ref_range_min: Optional[float] = None
    ref_range_max: Optional[float] = None
    history: list = field(default_factory=list)  # list of (date_str, value)


@dataclass
class BiomarkerAnalysis:
    """Analysis result for a biomarker."""
    name: str
    latest_value: Optional[float] = None
    latest_date: str = ""
    status: str = "unknown"  # normal, low, high, critical_low, critical_high
    deviation_pct: float = 0.0  # percentage from reference midpoint
    trend: str = "stable"  # rising, falling, stable, insufficient_data
    trend_slope: float = 0.0  # rate of change per month
    data_points: int = 0
    min_value: float = 0.0
    max_value: float = 0.0
    mean_value: float = 0.0


# Common biomarker reference ranges (adult, general population)
REFERENCE_RANGES = {
    # Cardiovascular
    "Total Cholesterol": (0, 200, "mg/dL"),
    "HDL Cholesterol": (40, 60, "mg/dL"),
    "LDL Cholesterol": (0, 100, "mg/dL"),
    "Triglycerides": (0, 150, "mg/dL"),
    "hs-CRP": (0, 3.0, "mg/L"),

    # Blood Sugar
    "Fasting Glucose": (70, 100, "mg/dL"),
    "HbA1c": (4.0, 5.7, "%"),

    # Thyroid
    "TSH": (0.4, 4.0, "mIU/L"),
    "Free T3": (2.3, 4.2, "pg/mL"),
    "Free T4": (0.8, 1.8, "ng/dL"),

    # Blood Count
    "Hemoglobin Male": (13.5, 17.5, "g/dL"),
    "Hemoglobin Female": (12.0, 16.0, "g/dL"),
    "WBC": (4.5, 11.0, "K/uL"),
    "Platelets": (150, 400, "K/uL"),

    # Metabolic
    "Creatinine": (0.6, 1.2, "mg/dL"),
    "BUN": (7, 20, "mg/dL"),
    "eGFR": (60, 120, "mL/min"),
    "Uric Acid": (3.4, 7.0, "mg/dL"),

    # Vitamins & Minerals
    "Vitamin D": (30, 100, "ng/mL"),
    "Vitamin B12": (200, 900, "pg/mL"),
    "Iron": (60, 170, "ug/dL"),
    "Ferritin Male": (20, 250, "ng/mL"),
    "Ferritin Female": (10, 120, "ng/mL"),

    # Liver
    "ALT": (7, 56, "U/L"),
    "AST": (10, 40, "U/L"),
    "Alkaline Phosphatase": (44, 147, "U/L"),

    # Hormones
    "Testosterone Male": (264, 916, "ng/dL"),
    "Testosterone Female": (15, 70, "ng/dL"),
    "Estradiol Male": (10, 40, "pg/mL"),
    "Cortisol": (6, 23, "ug/dL"),

    # Inflammation
    "ESR Male": (0, 15, "mm/hr"),
    "ESR Female": (0, 20, "mm/hr"),
}


def parse_reference_range(range_str: str) -> tuple[Optional[float], Optional[float]]:
    """Parse a reference range string.

    Supports formats: "70-100", "0-3.0", ">60", "<4.0", "60-120"

    Args:
        range_str: Reference range string

    Returns:
        Tuple of (min, max) or (None, value) for open-ended ranges
    """
    range_str = range_str.strip()

    if not range_str:
        return None, None

    # Handle > and < prefixes
    if range_str.startswith(">"):
        try:
            val = float(range_str[1:].strip())
            return val, None
        except ValueError:
            return None, None

    if range_str.startswith("<"):
        try:
            val = float(range_str[1:].strip())
            return None, val
        except ValueError:
            return None, None

    # Handle dash separator
    for sep in ["-", "–", "—"]:
        if sep in range_str:
            parts = range_str.split(sep, 1)
            try:
                low = float(parts[0].strip())
                high = float(parts[1].strip())
                return low, high
            except ValueError:
                continue

    return None, None


def classify_value(
    value: float,
    ref_min: Optional[float] = None,
    ref_max: Optional[float] = None,
) -> str:
    """Classify a biomarker value against reference range.

    Args:
        value: Biomarker value
        ref_min: Reference range minimum
        ref_max: Reference range maximum

    Returns:
        Classification: normal, low, high, critical_low, critical_high, unknown
    """
    if ref_min is None and ref_max is None:
        return "unknown"

    if ref_min is not None and ref_max is not None:
        midpoint = (ref_min + ref_max) / 2.0
        range_width = ref_max - ref_min

        if value < ref_min:
            deviation = (ref_min - value) / range_width if range_width > 0 else 0
            return "critical_low" if deviation > 0.5 else "low"
        elif value > ref_max:
            deviation = (value - ref_max) / range_width if range_width > 0 else 0
            return "critical_high" if deviation > 0.5 else "high"
        else:
            return "normal"

    if ref_min is not None:
        return "normal" if value >= ref_min else "low"

    if ref_max is not None:
        return "normal" if value <= ref_max else "high"

    return "unknown"


def compute_deviation_pct(
    value: float,
    ref_min: Optional[float] = None,
    ref_max: Optional[float] = None,
) -> float:
    """Compute percentage deviation from reference midpoint.

    Args:
        value: Biomarker value
        ref_min: Reference minimum
        ref_max: Reference maximum

    Returns:
        Percentage deviation (positive = above range, negative = below)
    """
    if ref_min is None or ref_max is None:
        return 0.0

    midpoint = (ref_min + ref_max) / 2.0
    range_width = ref_max - ref_min

    if range_width == 0:
        return 0.0

    return ((value - midpoint) / range_width) * 100.0


def detect_trend(
    values: list[float],
    window: int = 3,
) -> tuple[str, float]:
    """Detect trend direction from a series of values.

    Uses linear regression slope over the most recent window.

    Args:
        values: Chronological list of values
        window: Number of recent values to analyze

    Returns:
        Tuple of (direction, slope_per_month)
    """
    if len(values) < 2:
        return "insufficient_data", 0.0

    recent = values[-window:] if len(values) >= window else values
    n = len(recent)

    # Linear regression
    x_mean = (n - 1) / 2.0
    y_mean = sum(recent) / n

    numerator = sum((i - x_mean) * (recent[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return "stable", 0.0

    slope = numerator / denominator

    # Classify direction
    if slope > 0.5:
        direction = "rising"
    elif slope < -0.5:
        direction = "falling"
    else:
        direction = "stable"

    return direction, round(slope, 3)


def analyze_biomarker(
    biomarker: Biomarker,
) -> BiomarkerAnalysis:
    """Perform complete analysis of a biomarker.

    Args:
        biomarker: Biomarker with history data

    Returns:
        BiomarkerAnalysis with all computed metrics
    """
    if not biomarker.history:
        return BiomarkerAnalysis(name=biomarker.name)

    values = [v for _, v in biomarker.history]
    latest_val = values[-1]
    latest_date = biomarker.history[-1][0]

    # Classification
    status = classify_value(latest_val, biomarker.ref_range_min, biomarker.ref_range_max)
    deviation = compute_deviation_pct(latest_val, biomarker.ref_range_min, biomarker.ref_range_max)

    # Trend
    direction, slope = detect_trend(values)

    # Statistics
    n = len(values)
    mean_val = sum(values) / n

    return BiomarkerAnalysis(
        name=biomarker.name,
        latest_value=latest_val,
        latest_date=latest_date,
        status=status,
        deviation_pct=round(deviation, 1),
        trend=direction,
        trend_slope=slope,
        data_points=n,
        min_value=min(values),
        max_value=max(values),
        mean_value=round(mean_val, 2),
    )


def analyze_panel(
    biomarkers: list[Biomarker],
) -> dict:
    """Analyze a complete bloodwork panel.

    Args:
        biomarkers: List of biomarkers to analyze

    Returns:
        Panel analysis with per-marker results and summary
    """
    analyses = []
    abnormal_count = 0
    critical_count = 0

    for marker in biomarkers:
        analysis = analyze_biomarker(marker)
        analyses.append(analysis)

        if analysis.status in ("low", "high"):
            abnormal_count += 1
        elif analysis.status in ("critical_low", "critical_high"):
            critical_count += 1

    # Overall health score
    total = len(analyses)
    if total == 0:
        health_score = 0.0
    else:
        normal_count = sum(1 for a in analyses if a.status == "normal")
        health_score = (normal_count / total) * 100.0

    return {
        "total_markers": total,
        "normal_count": sum(1 for a in analyses if a.status == "normal"),
        "abnormal_count": abnormal_count,
        "critical_count": critical_count,
        "health_score": round(health_score, 1),
        "analyses": analyses,
    }


def track_longitudinal_changes(
    biomarkers: list[Biomarker],
    months_threshold: int = 6,
) -> list[dict]:
    """Identify biomarkers with significant longitudinal changes.

    Args:
        biomarkers: List of biomarkers with history
        months_threshold: Minimum months of data for significance

    Returns:
        List of significant changes with direction and magnitude
    """
    significant = []

    for marker in biomarkers:
        if len(marker.history) < 2:
            continue

        values = [v for _, v in marker.history]
        direction, slope = detect_trend(values, window=len(values))

        # Compute overall change
        first_val = values[0]
        last_val = values[-1]
        if first_val != 0:
            pct_change = ((last_val - first_val) / abs(first_val)) * 100.0
        else:
            pct_change = 0.0

        if abs(pct_change) > 10:  # >10% change is significant
            significant.append({
                "name": marker.name,
                "first_value": first_val,
                "latest_value": last_val,
                "pct_change": round(pct_change, 1),
                "direction": direction,
                "slope": slope,
                "data_points": len(marker.history),
            })

    return sorted(significant, key=lambda x: abs(x["pct_change"]), reverse=True)


def generate_clinical_summary(
    analyses: list[BiomarkerAnalysis],
) -> str:
    """Generate a human-readable clinical summary.

    Args:
        analyses: List of biomarker analyses

    Returns:
        Summary string
    """
    if not analyses:
        return "No biomarker data available."

    critical = [a for a in analyses if a.status in ("critical_low", "critical_high")]
    abnormal = [a for a in analyses if a.status in ("low", "high")]
    rising = [a for a in analyses if a.trend == "rising"]
    falling = [a for a in analyses if a.trend == "falling"]

    lines = []

    if critical:
        lines.append(f"CRITICAL: {len(critical)} marker(s) outside safe range:")
        for a in critical:
            lines.append(f"  - {a.name}: {a.latest_value} ({a.status})")

    if abnormal:
        lines.append(f"ABNORMAL: {len(abnormal)} marker(s) outside reference range:")
        for a in abnormal:
            lines.append(f"  - {a.name}: {a.latest_value} ({a.status})")

    if rising:
        lines.append(f"RISING: {len(rising)} marker(s) trending upward:")
        for a in rising[:5]:
            lines.append(f"  - {a.name}: slope {a.trend_slope}/month")

    if falling:
        lines.append(f"FALLING: {len(falling)} marker(s) trending downward:")
        for a in falling[:5]:
            lines.append(f"  - {a.name}: slope {a.trend_slope}/month")

    if not lines:
        lines.append("All markers within normal range with stable trends.")

    return "\n".join(lines)
