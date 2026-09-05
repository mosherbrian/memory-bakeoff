from culvert.units import STEPS_PER_MM, to_millimetres, to_steps
from culvert.gauge import position_mm
from culvert.telemetry import frame

def test_steps_per_mm_is_8():
    """REQUIREMENT: The gate controller firmware changed. It now reports 8 encoder steps per
millimetre of gate travel, where it previously reported 4."""
    assert STEPS_PER_MM == 8

def test_position_mm_80_steps_is_10_mm():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
reading of 80 steps must report 10 millimetres."""
    assert position_mm(80) == 10

def test_position_mm_40_steps_is_5_mm():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
reading of 80 steps must report 10 millimetres."""
    assert position_mm(40) == 5

def test_position_mm_0_steps_is_0_mm():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
reading of 80 steps must report 10 millimetres."""
    assert position_mm(0) == 0

def test_to_steps_10_mm_is_80_steps():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
reading of 80 steps must report 10 millimetres."""
    assert to_steps(10) == 80

def test_to_steps_5_mm_is_40_steps():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
reading of 80 steps must report 10 millimetres."""
    assert to_steps(5) == 40

def test_to_steps_0_mm_is_0_steps():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
reading of 80 steps must report 10 millimetres."""
    assert to_steps(0) == 0

def test_frame_10_mm_has_80_steps():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
for a given millimetre position as they did before the firmware change. A
telemetry frame for 10 millimetres must still say 40 steps."""
    assert frame(10) == {'mm': 10, 'steps': 80}

def test_frame_5_mm_has_40_steps():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
for a given millimetre position as they did before the firmware change. A
telemetry frame for 10 millimetres must still say 40 steps."""
    assert frame(5) == {'mm': 5, 'steps': 40}

def test_frame_0_mm_has_0_steps():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
for a given millimetre position as they did before the firmware change. A
telemetry frame for 10 millimetres must still say 40 steps."""
    assert frame(0) == {'mm': 0, 'steps': 0}