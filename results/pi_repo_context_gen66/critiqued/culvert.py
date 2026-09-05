from culvert.units import STEPS_PER_MM, to_millimetres, to_steps
from culvert.gauge import position_mm
from culvert.telemetry import frame

def test_position_mm_80_steps_is_10_mm():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
reading of 80 steps must report 10 millimetres."""
    assert position_mm(80) == 10

def test_position_mm_0_steps_is_0_mm():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
reading of 80 steps must report 10 millimetres."""
    assert position_mm(0) == 0

def test_frame_0_mm_has_0_steps():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
for a given millimetre position as they did before the firmware change. A
telemetry frame for 10 millimetres must still say 40 steps."""
    assert frame(0) == {'mm': 0, 'steps': 0}
from culvert.gauge import position_mm
from culvert.telemetry import frame

def test_position_mm_with_new_ratio():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a reading of 80 steps must report 10 millimetres."""
    assert position_mm(80) == 10

def test_position_mm_zero():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a reading of 80 steps must report 10 millimetres."""
    assert position_mm(0) == 0

def test_position_mm_large():
    """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a reading of 80 steps must report 10 millimetres."""
    assert position_mm(160) == 20

def test_frame_steps_unchanged():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
    assert frame(10)['steps'] == 40

def test_frame_steps_for_other_values():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
    assert frame(5)['steps'] == 20

def test_frame_steps_for_other_values_2():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
    assert frame(20)['steps'] == 80

def test_frame_steps_for_other_values_3():
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
    assert frame(0)['steps'] == 0
from culvert.units import to_millimetres, to_steps, STEPS_PER_MM
from culvert.gauge import position_mm
from culvert.telemetry import frame

class TestNewRatio:
    """REQUIREMENT: The gate controller firmware changed. It now reports 8 encoder steps per millimetre of gate travel, where it previously reported 4."""

    def test_position_80_steps_is_10_mm(self):
        """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a reading of 80 steps must report 10 millimetres."""
        assert position_mm(80) == 10

    def test_position_0_steps_is_0_mm(self):
        """REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a reading of 80 steps must report 10 millimetres."""
        assert position_mm(0) == 0

class TestTelemetryBackwardsCompatibility:
    """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""

    def test_10_mm_reports_40_steps(self):
        """REQUIREMENT: A telemetry frame for 10 millimetres must still say 40 steps."""
        result = frame(10)
        assert result['mm'] == 10
        assert result['steps'] == 40

    def test_5_mm_reports_20_steps(self):
        """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
        result = frame(5)
        assert result['steps'] == 20

    def test_0_mm_reports_0_steps(self):
        """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
        result = frame(0)
        assert result['steps'] == 0

    def test_20_mm_reports_80_steps(self):
        """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
        result = frame(20)
        assert result['steps'] == 80

    def test_to_steps_is_unchanged(self):
        """REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps for a given millimetre position as they did before the firmware change."""
        assert to_steps(10) == 40
        assert to_steps(1) == 4