import pytest
from sluice.units import STEPS_PER_MM, to_steps, to_millimetres
from sluice.gauge import position_mm
from sluice.telemetry import frame


class TestStepsPerMmConstant:
    """Verify the firmware change is reflected in the constant."""

    def test_steps_per_mm_is_eight(self):
        assert STEPS_PER_MM == 8


class TestToMillimetres:
    """Verify conversion from raw steps to millimetres uses the new rate."""

    def test_basic_conversion(self):
        # 8 steps per mm means 80 steps = 10 mm
        assert to_millimetres(80) == 10

    def test_half_mm(self):
        assert to_millimetres(4) == 0  # 4 // 8 = 0

    def test_exact_mm(self):
        assert to_millimetres(16) == 2

    def test_partial_mm_rounds_down(self):
        # 10 steps = 1.25 mm, should floor to 1
        assert to_millimetres(10) == 1

    def test_zero(self):
        assert to_millimetres(0) == 0


class TestToSteps:
    """Verify conversion from millimetres to steps uses the new rate."""

    def test_basic_conversion(self):
        # 8 steps per mm means 10 mm = 80 steps
        assert to_steps(10) == 80

    def test_one_mm(self):
        assert to_steps(1) == 8

    def test_zero_mm(self):
        assert to_steps(0) == 0

    def test_half_mm(self):
        assert to_steps(0) == 0  # 0 mm -> 0 steps

    def test_large_value(self):
        assert to_steps(100) == 800


class TestGaugePosition:
    """Verify position_mm uses the updated conversion."""

    def test_position_mm_with_new_constant(self):
        # With 8 steps/mm, raw 80 should give 10 mm
        assert position_mm(80) == 10

    def test_position_mm_raw_16(self):
        assert position_mm(16) == 2

    def test_position_mm_raw_4(self):
        assert position_mm(4) == 0

    def test_position_mm_raw_0(self):
        assert position_mm(0) == 0


class TestTelemetryFrame:
    """Verify telemetry frames report steps consistent with new rate."""

    def test_frame_steps_for_10_mm(self):
        # 10 mm should report 80 steps (10 * 8)
        result = frame(10)
        assert result["steps"] == 80
        assert result["unit"] == "steps"

    def test_frame_steps_for_1_mm(self):
        result = frame(1)
        assert result["steps"] == 8

    def test_frame_steps_for_0_mm(self):
        result = frame(0)
        assert result["steps"] == 0

    def test_frame_steps_for_5_mm(self):
        result = frame(5)
        assert result["steps"] == 40

    def test_frame_unit_is_steps(self):
        result = frame(10)
        assert result["unit"] == "steps"

    def test_frame_has_required_keys(self):
        result = frame(10)
        assert "steps" in result
        assert "unit" in result
