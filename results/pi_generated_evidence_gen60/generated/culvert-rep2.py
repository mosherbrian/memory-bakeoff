import pytest
from culvert.units import STEPS_PER_MM, to_millimetres, to_steps
from culvert.gauge import position_mm
from culvert.telemetry import frame


class TestFirmwareRatio:
    """Tests for the updated STEPS_PER_MM ratio (8 steps/mm)."""

    def test_steps_per_mm_is_eight(self):
        """STEPS_PER_MM constant must be 8 after the firmware change."""
        assert STEPS_PER_MM == 8

    def test_position_mm_80_steps_is_10_mm(self):
        """A reading of 80 steps must report 10 millimetres."""
        assert position_mm(80) == 10

    def test_position_mm_160_steps_is_20_mm(self):
        """A reading of 160 steps must report 20 millimetres."""
        assert position_mm(160) == 20

    def test_position_mm_0_steps_is_0_mm(self):
        """Zero steps should yield zero millimetres."""
        assert position_mm(0) == 0

    def test_position_mm_divides_evenly(self):
        """For multiples of 8, division should be exact."""
        assert to_millimetres(8) == 1
        assert to_millimetres(24) == 3
        assert to_millimetres(40) == 5


class TestTelemetryBackwardsCompatibility:
    """Tests ensuring telemetry frames report the SAME number of steps as before."""

    def test_10_mm_reports_40_steps(self):
        """A telemetry frame for 10 millimetres must still say 40 steps."""
        result = frame(10)
        assert result["mm"] == 10
        assert result["steps"] == 40

    def test_1_mm_reports_4_steps(self):
        """A telemetry frame for 1 millimetre must still say 4 steps."""
        result = frame(1)
        assert result["steps"] == 4

    def test_5_mm_reports_20_steps(self):
        """A telemetry frame for 5 millimetres must still say 20 steps."""
        result = frame(5)
        assert result["steps"] == 20

    def test_0_mm_reports_0_steps(self):
        """A telemetry frame for 0 millimetres must still say 0 steps."""
        result = frame(0)
        assert result["steps"] == 0

    def test_frame_structure(self):
        """The frame must contain 'mm' and 'steps' keys."""
        result = frame(10)
        assert "mm" in result
        assert "steps" in result
        assert isinstance(result["mm"], int)
        assert isinstance(result["steps"], int)


class TestToStepsBackwardsCompatibility:
    """Direct tests on to_steps to ensure backwards compatibility."""

    def test_to_steps_10_mm(self):
        assert to_steps(10) == 40

    def test_to_steps_1_mm(self):
        assert to_steps(1) == 4

    def test_to_steps_5_mm(self):
        assert to_steps(5) == 20

    def test_to_steps_0_mm(self):
        assert to_steps(0) == 0
