from culvert.gauge import position_mm
from culvert.telemetry import frame

def test_position_mm_with_new_ratio():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a reading of 80 steps must report 10 millimetres."""
    assert position_mm(80) == 10

def test_position_mm_basic():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a reading of 80 steps must report 10 millimetres."""
    assert position_mm(40) == 10

def test_position_mm_zero():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a reading of 80 steps must report 10 millimetres."""
    assert position_mm(0) == 0

def test_position_mm_large():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a reading of 80 steps must report 10 millimetres."""
    assert position_mm(160) == 20

def test_frame_steps_unchanged():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
    assert frame(10)['steps'] == 40

def test_frame_mm_unchanged():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
    assert frame(10)['mm'] == 10

def test_frame_steps_for_other_values():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
    assert frame(5)['steps'] == 20

def test_frame_steps_for_other_values_2():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
    assert frame(20)['steps'] == 80

def test_frame_steps_for_other_values_3():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
    assert frame(0)['steps'] == 0