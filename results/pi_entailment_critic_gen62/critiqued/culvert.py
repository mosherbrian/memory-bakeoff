from culvert.units import STEPS_PER_MM, to_millimetres, to_steps
from culvert.gauge import position_mm
from culvert.telemetry import frame

def test_steps_per_mm_is_8():
    """REQUIREMENT: The gate controller firmware changed. It now reports 8 encoder steps per
millimetre of gate travel, where it previously reported 4."""
    assert STEPS_PER_MM == 8
from culvert.gauge import position_mm
from culvert.telemetry import frame

def test_position_mm_with_new_ratio():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a reading of 80 steps must report 10 millimetres."""
    assert position_mm(80) == 10
from culvert.units import to_millimetres, to_steps, STEPS_PER_MM
from culvert.gauge import position_mm
from culvert.telemetry import frame

class TestNewRatio:
    """REQUIREMENT: The gate controller firmware changed. It now reports 8 encoder steps per millimetre of gate travel, where it previously reported 4."""

    def test_position_80_steps_is_10_mm(self):
        """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a reading of 80 steps must report 10 millimetres."""
        assert position_mm(80) == 10

class TestTelemetryBackwardsCompatibility:
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""