"""
Advanced Breathing Pacer
Extracted from OpenHRV's sinusoidal breathing pattern algorithm

Provides multiple breathing patterns:
- Coherent breathing (0.1 Hz)
- Box breathing (4-4-4-4)
- 4-7-8 relaxation
- Custom patterns

Pure functions for generating breathing animations and pacer data.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math
import time


@dataclass
class BreathingPattern:
    """Configuration for a breathing pattern"""
    name: str
    inhale: float      # seconds
    hold_in: float     # seconds
    exhale: float      # seconds
    hold_out: float    # seconds
    description: str


# Pre-defined breathing patterns
PATTERNS = {
    'coherent': BreathingPattern(
        name='coherent',
        inhale=4.0,
        hold_in=0.0,
        exhale=4.0,
        hold_out=0.0,
        description='Coherent breathing at 0.1 Hz (6 breaths/min)'
    ),
    'box': BreathingPattern(
        name='box',
        inhale=4.0,
        hold_in=4.0,
        exhale=4.0,
        hold_out=4.0,
        description='Box breathing (4-4-4-4)'
    ),
    'relaxation': BreathingPattern(
        name='relaxation',
        inhale=4.0,
        hold_in=7.0,
        exhale=8.0,
        hold_out=0.0,
        description='4-7-8 relaxation breathing'
    ),
    'energizing': BreathingPattern(
        name='energizing',
        inhale=2.0,
        hold_in=0.0,
        exhale=2.0,
        hold_out=0.0,
        description='Fast energizing breathing (15 breaths/min)'
    ),
    'sleep': BreathingPattern(
        name='sleep',
        inhale=6.0,
        hold_in=2.0,
        exhale=8.0,
        hold_out=2.0,
        description='Slow sleep preparation breathing'
    )
}


def get_pattern(name: str) -> BreathingPattern:
    """
    Get a breathing pattern by name
    
    Args:
        name: Pattern name (coherent, box, relaxation, energizing, sleep)
    
    Returns:
        BreathingPattern configuration
    """
    if name not in PATTERNS:
        raise ValueError(f"Unknown pattern: {name}. Available: {list(PATTERNS.keys())}")
    return PATTERNS[name]


def calculate_cycle_duration(pattern: BreathingPattern) -> float:
    """
    Calculate total cycle duration for a pattern
    
    Args:
        pattern: Breathing pattern
    
    Returns:
        Total cycle duration in seconds
    """
    return pattern.inhale + pattern.hold_in + pattern.exhale + pattern.hold_out


def calculate_breaths_per_minute(pattern: BreathingPattern) -> float:
    """
    Calculate breathing rate in breaths per minute
    
    Args:
        pattern: Breathing pattern
    
    Returns:
        Breaths per minute
    """
    cycle_duration = calculate_cycle_duration(pattern)
    return 60.0 / cycle_duration if cycle_duration > 0 else 0


def generate_breathing_curve(
    pattern: BreathingPattern,
    duration: float,
    sample_rate: float = 30.0
) -> List[Tuple[float, float]]:
    """
    Generate a breathing curve using OpenHRV's sinusoidal approach
    
    The curve is generated using a sinusoidal function that smoothly
    transitions between inhale and exhale phases, matching OpenHRV's
    pacer implementation.
    
    Args:
        pattern: Breathing pattern
        duration: Duration in seconds
        sample_rate: Samples per second
    
    Returns:
        List of (time, amplitude) tuples where amplitude is 0-1
    """
    samples = []
    num_samples = int(duration * sample_rate)
    cycle_duration = calculate_cycle_duration(pattern)
    
    if cycle_duration <= 0:
        return samples
    
    for i in range(num_samples):
        t = i / sample_rate
        
        # Calculate position within cycle
        cycle_pos = t % cycle_duration
        
        # Determine phase and calculate amplitude
        if cycle_pos < pattern.inhale:
            # Inhale phase: 0 -> 1
            phase_progress = cycle_pos / pattern.inhale
            amplitude = math.sin(phase_progress * math.pi / 2)  # Sinusoidal ease
            
        elif cycle_pos < pattern.inhale + pattern.hold_in:
            # Hold in phase: 1
            amplitude = 1.0
            
        elif cycle_pos < pattern.inhale + pattern.hold_in + pattern.exhale:
            # Exhale phase: 1 -> 0
            exhale_pos = cycle_pos - pattern.inhale - pattern.hold_in
            phase_progress = exhale_pos / pattern.exhale
            amplitude = math.cos(phase_progress * math.pi / 2)  # Sinusoidal ease
            
        else:
            # Hold out phase: 0
            amplitude = 0.0
        
        samples.append((t, amplitude))
    
    return samples


def generate_pacer_visualization(
    pattern: BreathingPattern,
    duration: float,
    sample_rate: float = 60.0,
    visualization_type: str = 'circle'
) -> List[dict]:
    """
    Generate pacer visualization data
    
    Args:
        pattern: Breathing pattern
        duration: Duration in seconds
        sample_rate: Samples per second
        visualization_type: 'circle' or 'wave'
    
    Returns:
        List of visualization data points
    """
    samples = []
    num_samples = int(duration * sample_rate)
    cycle_duration = calculate_cycle_duration(pattern)
    
    for i in range(num_samples):
        t = i / sample_rate
        cycle_pos = t % cycle_duration
        
        # Get amplitude using OpenHRV's sinusoidal method
        if cycle_pos < pattern.inhale:
            phase_progress = cycle_pos / pattern.inhale
            amplitude = math.sin(phase_progress * math.pi / 2)
        elif cycle_pos < pattern.inhale + pattern.hold_in:
            amplitude = 1.0
        elif cycle_pos < pattern.inhale + pattern.hold_in + pattern.exhale:
            exhale_pos = cycle_pos - pattern.inhale - pattern.hold_in
            phase_progress = exhale_pos / pattern.exhale
            amplitude = math.cos(phase_progress * math.pi / 2)
        else:
            amplitude = 0.0
        
        if visualization_type == 'circle':
            # Circle visualization (like OpenHRV)
            angle = 2 * math.pi * (cycle_pos / cycle_duration)
            radius = 0.5 + 0.5 * amplitude
            
            samples.append({
                'time': t,
                'amplitude': amplitude,
                'x': radius * math.cos(angle),
                'y': radius * math.sin(angle),
                'radius': radius
            })
        else:
            # Wave visualization
            samples.append({
                'time': t,
                'amplitude': amplitude,
                'x': t,
                'y': amplitude
            })
    
    return samples


def calculate_adaptive_pace(
    current_hr: float,
    target_hr: float,
    current_pattern: BreathingPattern,
    adjustment_rate: float = 0.1
) -> BreathingPattern:
    """
    Calculate adaptive breathing pace based on heart rate
    
    Adjusts breathing rate to help reach target heart rate.
    Slower breathing generally lowers heart rate.
    
    Args:
        current_hr: Current heart rate (bpm)
        target_hr: Target heart rate (bpm)
        current_pattern: Current breathing pattern
        adjustment_rate: How aggressively to adjust (0-1)
    
    Returns:
        Adjusted BreathingPattern
    """
    # Calculate target breathing rate
    # Slower breathing = lower heart rate
    hr_diff = current_hr - target_hr
    
    if hr_diff > 0:
        # Need to slow down breathing
        target_bpm = calculate_breaths_per_minute(current_pattern) * (1 - adjustment_rate)
    elif hr_diff < 0:
        # Need to speed up breathing
        target_bpm = calculate_breaths_per_minute(current_pattern) * (1 + adjustment_rate)
    else:
        # At target
        return current_pattern
    
    # Clamp to reasonable range (4-20 breaths/min)
    target_bpm = max(4.0, min(20.0, target_bpm))
    
    # Calculate new cycle duration
    new_cycle_duration = 60.0 / target_bpm
    
    # Scale pattern phases proportionally
    old_cycle = calculate_cycle_duration(current_pattern)
    scale_factor = new_cycle_duration / old_cycle if old_cycle > 0 else 1.0
    
    return BreathingPattern(
        name=f"adaptive_{current_pattern.name}",
        inhale=current_pattern.inhale * scale_factor,
        hold_in=current_pattern.hold_in * scale_factor,
        exhale=current_pattern.exhale * scale_factor,
        hold_out=current_pattern.hold_out * scale_factor,
        description=f"Adaptive {current_pattern.description}"
    )


def get_realtime_pacer_state(pattern: BreathingPattern) -> dict:
    """
    Get current pacer state based on real time
    
    This is the core function used for real-time pacer display,
    matching OpenHRV's approach of using actual time rather than
    pre-computed sequences.
    
    Args:
        pattern: Breathing pattern
    
    Returns:
        Dictionary with current state information
    """
    cycle_duration = calculate_cycle_duration(pattern)
    current_time = time.time()
    cycle_pos = current_time % cycle_duration
    
    # Calculate phase and amplitude
    if cycle_pos < pattern.inhale:
        phase = 'inhale'
        phase_progress = cycle_pos / pattern.inhale
        amplitude = math.sin(phase_progress * math.pi / 2)
        
    elif cycle_pos < pattern.inhale + pattern.hold_in:
        phase = 'hold_in'
        phase_progress = (cycle_pos - pattern.inhale) / pattern.hold_in if pattern.hold_in > 0 else 1
        amplitude = 1.0
        
    elif cycle_pos < pattern.inhale + pattern.hold_in + pattern.exhale:
        phase = 'exhale'
        exhale_pos = cycle_pos - pattern.inhale - pattern.hold_in
        phase_progress = exhale_pos / pattern.exhale
        amplitude = math.cos(phase_progress * math.pi / 2)
        
    else:
        phase = 'hold_out'
        hold_out_pos = cycle_pos - pattern.inhale - pattern.hold_in - pattern.exhale
        phase_progress = hold_out_pos / pattern.hold_out if pattern.hold_out > 0 else 1
        amplitude = 0.0
    
    return {
        'phase': phase,
        'amplitude': amplitude,
        'phase_progress': phase_progress,
        'cycle_position': cycle_pos,
        'cycle_duration': cycle_duration,
        'breaths_per_minute': calculate_breaths_per_minute(pattern),
        'timestamp': current_time
    }


def validate_pattern(pattern: BreathingPattern) -> List[str]:
    """
    Validate a breathing pattern
    
    Args:
        pattern: Breathing pattern to validate
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if pattern.inhale <= 0:
        errors.append("Inhale duration must be positive")
    
    if pattern.exhale <= 0:
        errors.append("Exhale duration must be positive")
    
    if pattern.hold_in < 0:
        errors.append("Hold in duration cannot be negative")
    
    if pattern.hold_out < 0:
        errors.append("Hold out duration cannot be negative")
    
    total = calculate_cycle_duration(pattern)
    if total < 2.0:
        errors.append("Total cycle duration should be at least 2 seconds")
    
    if total > 30.0:
        errors.append("Total cycle duration should not exceed 30 seconds")
    
    bpm = calculate_breaths_per_minute(pattern)
    if bpm < 4.0:
        errors.append("Breathing rate too slow (minimum 4 breaths/min)")
    
    if bpm > 20.0:
        errors.append("Breathing rate too fast (maximum 20 breaths/min)")
    
    return errors