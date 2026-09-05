import pytest
from culvert.units import STEPS_PER_MM, to_millimetres, to_steps
from culvert.gauge import position_mm
from culvert.telemetry import frame


class TestFirmwareRatioUpdate:
    """Tests for the firmware change: 4 steps/mm -> 8 steps/mm"""

    def test_steps_per_mm_is_eight(self):
        """STEPS_PER_MM constant must be updated to 8"""
        assert STEPS_PER_MM == 8

    def test_position_mm_80_steps(self):
        """A reading of 80 steps must report 10 millimetres"""
        assert position_mm(80) == 10

    def test_position_mm_40_steps(self):
        """A reading of 40 steps must report 5 millimetres (40 / 8)"""
        assert position_mm(40) == 5

    def test_position_mm_0_steps(self):
        """Zero steps should yield zero millimetres"""
        assert position_mm(0) == 0

    def test_position_mm_16_steps(self):
        """16 steps / 8 = 2 millimetres"""
        assert position_mm(16) == 2

    def test_position_mm_7_steps(self):
        """7 steps // 8 = 0 millimetres (integer division)"""
        assert position_mm(7) == 0

    def test_position_mm_8_steps(self):
        """8 steps // 8 = 1 millimetre"""
        assert position_mm(8) == 1


class TestTelemetryBackwardsCompatibility:
    """Tests ensuring telemetry frames still report the same number of steps
    for a given millimetre position as before (4 steps/mm)."""

    def test_frame_10_mm_steps(self):
        """A telemetry frame for 10 millimetres must still say 40 steps"""
        result = frame(10)
        assert result["mm"] == 10
        assert result["steps"] == 40

    def test_frame_1_mm_steps(self):
        """1 millimetre should still report 4 steps"""
        result = frame(1)
        assert result["steps"] == 4

    def test_frame_0_mm_steps(self):
        """0 millimetres should report 0 steps"""
        result = frame(0)
        assert result["steps"] == 0

    def test_frame_5_mm_steps(self):
        """5 millimetres should still report 20 steps"""
        result = frame(5)
        assert result["steps"] == 20

    def test_frame_20_mm_steps(self):
        """20 millimetres should still report 80 steps"""
        result = frame(20)
        assert result["steps"] == 80

    def test_frame_returns_dict(self):
        """frame() must return a dictionary"""
        assert isinstance(frame(1), dict)

    def test_frame_has_mm_key(self):
        """frame() result must have 'mm' key"""
        assert "mm" in frame(1)

    def test_frame_has_steps_key(self):
        """frame() result must have 'steps' key"""
        assert "steps" in frame(1)


class TestToStepsBackwardsCompatibility:
    """Direct tests on to_steps to ensure it uses 4 steps/mm for telemetry"""

    def test_to_steps_10_mm(self):
        assert to_steps(10) == 40

    def test_to_steps_1_mm(self):
        assert to_steps(1) == 4

    def test_to_steps_0_mm(self):
        assert to_steps(0) == 0


class TestToMillimetresNewRatio:
    """Direct tests on to_millimetres to ensure it uses 8 steps/mm"""

    def test_to_millimetres_80_steps(self):
        assert to_millimetres(80) == 10

    def test_to_millimetres_40_steps(self):
        assert to_millimetres(40) == 5

    def test_to_millimetres_16_steps(self):
        assert to_millimetres(16) == 2

    def test_to_millimetres_7_steps(self):
        assert to_millimetres(7) == 0

    def test_to_millimetres_8_steps(self):
        assert to_millimetres(8) == 1
