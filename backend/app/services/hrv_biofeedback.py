"""
HRV Biofeedback Training Service
Inspired by OpenHRV - real-time HRV display, breathing pacer, Polar sensor integration

Pure functions for HRV biofeedback training sessions:
- Breathing pacer generation (coherent breathing at 0.1 Hz)
- Real-time HRV metrics calculation (RMSSD, SDNN, LF/HF ratio)
- Session analytics and progress tracking
- Polar H7/H9/H10 sensor data processing
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import math
import time


@dataclass
class BreathingPacer:
    """Breathing pacer configuration for coherent breathing"""
    inhale_duration: float  # seconds
    hold_duration: float    # seconds (optional)
    exhale_duration: float  # seconds
    cycle_duration: float   # total cycle duration
    frequency: float        # Hz (0.1 Hz = 6 breaths/min for coherence)


@dataclass
class HRVSample:
    """Single HRV measurement sample"""
    timestamp: float
    rr_interval: float      # ms (R-R interval from ECG)
    heart_rate: float       # bpm
    quality: float          # 0-1 signal quality


@dataclass
class HRVMetrics:
    """Calculated HRV metrics"""
    rmssd: float            # Root mean square of successive differences (ms)
    sdnn: float             # Standard deviation of NN intervals (ms)
    lf_power: float         # Low frequency power (ms²)
    hf_power: float         # High frequency power (ms²)
    lf_hf_ratio: float      # LF/HF ratio
    hr: float               # Average heart rate (bpm)
    rr_mean: float          # Mean R-R interval (ms)
    sample_count: int       # Number of samples used


@dataclass
class BiofeedbackSession:
    """HRV biofeedback training session"""
    session_id: str
    start_time: float
    duration: float         # seconds
    target_coherence: float # target coherence score (0-1)
    actual_coherence: float # achieved coherence score
    pacer: BreathingPacer
    samples: List[HRVSample]
    metrics: HRVMetrics
    progress_score: float   # 0-100 progress toward mastery


def create_coherent_pacer(target_frequency: float = 0.1) -> BreathingPacer:
    """
    Create a breathing pacer for coherent breathing
    
    Coherent breathing at 0.1 Hz (6 breaths/min) maximizes HRV
    and promotes parasympathetic nervous system activation.
    
    Args:
        target_frequency: Target breathing frequency in Hz (default 0.1 Hz)
    
    Returns:
        BreathingPacer configuration
    """
    cycle_duration = 1.0 / target_frequency
    
    # Standard coherent breathing: 4s inhale, 4s exhale, 2s hold
    inhale_duration = cycle_duration * 0.4
    hold_duration = cycle_duration * 0.2
    exhale_duration = cycle_duration * 0.4
    
    return BreathingPacer(
        inhale_duration=inhale_duration,
        hold_duration=hold_duration,
        exhale_duration=exhale_duration,
        cycle_duration=cycle_duration,
        frequency=target_frequency
    )


def calculate_hrv_metrics(samples: List[HRVSample], window_size: int = 30) -> HRVMetrics:
    """
    Calculate HRV metrics from RR interval samples
    
    Args:
        samples: List of HRV samples with RR intervals
        window_size: Window size in seconds for metrics calculation
    
    Returns:
        HRVMetrics with calculated values
    """
    if len(samples) < 2:
        return HRVMetrics(
            rmssd=0.0, sdnn=0.0, lf_power=0.0, hf_power=0.0,
            lf_hf_ratio=0.0, hr=0.0, rr_mean=0.0, sample_count=0
        )
    
    # Extract RR intervals (in ms)
    rr_intervals = [s.rr_interval for s in samples]
    
    # Calculate RMSSD (Root Mean Square of Successive Differences)
    successive_diffs = [rr_intervals[i+1] - rr_intervals[i] for i in range(len(rr_intervals)-1)]
    rmssd = math.sqrt(sum(d**2 for d in successive_diffs) / len(successive_diffs))
    
    # Calculate SDNN (Standard Deviation of NN intervals)
    rr_mean = sum(rr_intervals) / len(rr_intervals)
    sdnn = math.sqrt(sum((rr - rr_mean)**2 for rr in rr_intervals) / len(rr_intervals))
    
    # Calculate frequency domain metrics (simplified)
    # LF: 0.04-0.15 Hz, HF: 0.15-0.4 Hz
    lf_power = calculate_lf_power(rr_intervals)
    hf_power = calculate_hf_power(rr_intervals)
    lf_hf_ratio = lf_power / hf_power if hf_power > 0 else 0.0
    
    # Average heart rate
    hr = sum(s.heart_rate for s in samples) / len(samples)
    
    return HRVMetrics(
        rmssd=rmssd,
        sdnn=sdnn,
        lf_power=lf_power,
        hf_power=hf_power,
        lf_hf_ratio=lf_hf_ratio,
        hr=hr,
        rr_mean=rr_mean,
        sample_count=len(samples)
    )


def calculate_coherence_score(metrics: HRVMetrics, window_size: int = 30) -> float:
    """
    Calculate coherence score (0-1) based on HRV metrics
    
    High coherence indicates:
    - Stable breathing at ~0.1 Hz
    - High LF power (respiratory sinus arrhythmia)
    - Low HF power (reduced parasympathetic tone)
    - RMSSD > 20ms (healthy vagal tone)
    
    Args:
        metrics: Calculated HRV metrics
        window_size: Window size for coherence calculation
    
    Returns:
        Coherence score between 0 and 1
    """
    # RMSSD score (0-1, optimal > 30ms)
    rmssd_score = min(metrics.rmssd / 30.0, 1.0)
    
    # LF/HF ratio score (0-1, optimal 1.5-2.5)
    if metrics.lf_hf_ratio >= 1.5 and metrics.lf_hf_ratio <= 2.5:
        lf_hf_score = 1.0
    elif metrics.lf_hf_ratio < 1.5:
        lf_hf_score = metrics.lf_hf_ratio / 1.5
    else:
        lf_hf_score = 2.5 / metrics.lf_hf_ratio
    
    # HR stability score (0-1, optimal 60-80 bpm)
    if metrics.hr >= 60 and metrics.hr <= 80:
        hr_score = 1.0
    elif metrics.hr < 60:
        hr_score = metrics.hr / 60.0
    else:
        hr_score = 80.0 / metrics.hr
    
    # Weighted combination
    coherence = (rmssd_score * 0.4 + lf_hf_score * 0.3 + hr_score * 0.3)
    
    return min(max(coherence, 0.0), 1.0)


def process_polar_data(raw_data: dict) -> Optional[HRVSample]:
    """
    Process raw data from Polar H7/H9/H10 chest strap
    
    Args:
        raw_data: Raw sensor data dictionary
    
    Returns:
        HRVSample if valid, None otherwise
    """
    try:
        # Extract timestamp
        timestamp = raw_data.get('timestamp', time.time())
        
        # Extract RR interval (in ms)
        rr_interval = raw_data.get('rr_interval')
        if rr_interval is None or rr_interval <= 0:
            return None
        
        # Extract heart rate
        heart_rate = raw_data.get('heart_rate')
        if heart_rate is None or heart_rate <= 0:
            # Calculate from RR interval
            heart_rate = 60000.0 / rr_interval  # Convert ms to bpm
        
        # Calculate signal quality
        quality = raw_data.get('quality', 0.8)  # Default to 0.8 if not provided
        
        return HRVSample(
            timestamp=timestamp,
            rr_interval=rr_interval,
            heart_rate=heart_rate,
            quality=quality
        )
    except Exception as e:
        print(f"[HRV Biofeedback] Error processing polar data: {e}")
        return None


def calculate_session_progress(sessions: List[BiofeedbackSession]) -> float:
    """
    Calculate overall progress score across multiple sessions
    
    Args:
        sessions: List of completed biofeedback sessions
    
    Returns:
        Progress score 0-100
    """
    if not sessions:
        return 0.0
    
    # Calculate average coherence across sessions
    avg_coherence = sum(s.actual_coherence for s in sessions) / len(sessions)
    
    # Calculate improvement trend
    if len(sessions) >= 2:
        first_half = sessions[:len(sessions)//2]
        second_half = sessions[len(sessions)//2:]
        
        first_avg = sum(s.actual_coherence for s in first_half) / len(first_half)
        second_avg = sum(s.actual_coherence for s in second_half) / len(second_half)
        
        improvement = second_avg - first_avg
    else:
        improvement = 0.0
    
    # Calculate consistency (standard deviation of coherence)
    coherence_values = [s.actual_coherence for s in sessions]
    mean_coherence = sum(coherence_values) / len(coherence_values)
    variance = sum((c - mean_coherence)**2 for c in coherence_values) / len(coherence_values)
    consistency = 1.0 / (1.0 + math.sqrt(variance))
    
    # Weighted progress score
    progress = (avg_coherence * 60 + improvement * 30 + consistency * 10) * 100
    
    return min(max(progress, 0.0), 100.0)


def generate_pacer_visualization(pacer: BreathingPacer, duration: float, sample_rate: float = 30.0) -> List[Tuple[float, float]]:
    """
    Generate breathing pacer visualization data
    
    Args:
        pacer: Breathing pacer configuration
        duration: Duration in seconds
        sample_rate: Samples per second
    
    Returns:
        List of (time, amplitude) tuples for visualization
    """
    visualization = []
    num_samples = int(duration * sample_rate)
    
    for i in range(num_samples):
        t = i / sample_rate
        cycle_pos = t % pacer.cycle_duration
        
        # Determine phase (inhale, hold, exhale)
        if cycle_pos < pacer.inhale_duration:
            # Inhale phase (0 to 1)
            amplitude = cycle_pos / pacer.inhale_duration
        elif cycle_pos < pacer.inhale_duration + pacer.hold_duration:
            # Hold phase (1)
            amplitude = 1.0
        else:
            # Exhale phase (1 to 0)
            exhale_pos = cycle_pos - pacer.inhale_duration - pacer.hold_duration
            amplitude = 1.0 - (exhale_pos / pacer.exhale_duration)
        
        visualization.append((t, amplitude))
    
    return visualization


# Helper functions for frequency domain analysis
def calculate_lf_power(rr_intervals: List[float]) -> float:
    """Calculate low frequency power (0.04-0.15 Hz)"""
    # Simplified LF power calculation
    # In production, use FFT or autoregressive methods
    if len(rr_intervals) < 10:
        return 0.0
    
    # Calculate successive differences
    diffs = [rr_intervals[i+1] - rr_intervals[i] for i in range(len(rr_intervals)-1)]
    
    # Simple variance-based approximation
    mean_diff = sum(diffs) / len(diffs)
    variance = sum((d - mean_diff)**2 for d in diffs) / len(diffs)
    
    return variance * 0.5  # Simplified scaling


def calculate_hf_power(rr_intervals: List[float]) -> float:
    """Calculate high frequency power (0.15-0.4 Hz)"""
    # Simplified HF power calculation
    if len(rr_intervals) < 10:
        return 0.0
    
    # Calculate successive differences
    diffs = [rr_intervals[i+1] - rr_intervals[i] for i in range(len(rr_intervals)-1)]
    
    # Simple variance-based approximation
    mean_diff = sum(diffs) / len(diffs)
    variance = sum((d - mean_diff)**2 for d in diffs) / len(diffs)
    
    return variance * 0.3  # Simplified scaling