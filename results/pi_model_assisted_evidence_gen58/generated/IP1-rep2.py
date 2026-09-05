import pytest
from sluice.units import STEPS_PER_MM, to_millimetres, to_steps
from sluice.telemetry import frame
from sluice.gauge import position_mm


class TestStepsPerMmConstant:
    """Verify the firmware constant is updated to 8."""

    def test_steps_per_mm_is_eight(self):
        assert STEPS_PER_MM == 8

    def test_steps_per_mm_is_not_four(self):
        # Ensure old value is not present
        assert STEPS_PER_MM != 4


class TestToSteps:
    """Verify to_steps converts mm to steps using the new rate."""

    def test_one_mm_is_eight_steps(self):
        assert to_steps(1) == 8

    def test_zero_mm_is_zero_steps(self):
        assert to_steps(0) == 0

    def test_two_mm_is_sixteen_steps(self):
        assert to_steps(2) == 16

    def test_ten_mm_is_eighty_steps(self):
        assert to_steps(10) == 80

    def test_negative_mm_is_negative_steps(self):
        assert to_steps(-1) == -8


class TestToMillimetres:
    """Verify to_millimetres converts steps to mm using the new rate."""

    def test_eight_steps_is_one_mm(self):
        assert to_millimetres(8) == 1

    def test_zero_steps_is_zero_mm(self):
        assert to_millimetres(0) == 0

    def test_sixteen_steps_is_two_mm(self):
        assert to_millimetres(16) == 2

    def test_eighty_steps_is_ten_mm(self):
        assert to_millimetres(80) == 10

    def test_partial_mm_is_rolled_down(self):
        # 9 steps should be 1 mm (integer division)
        assert to_millimetres(9) == 1

    def test_seven_steps_is_zero_mm(self):
        # 7 steps is less than 1 mm, so 0
        assert to_millimetres(7) == 0

    def test_negative_steps_is_negative_mm(self):
        assert to_millimetres(-8) == -1


class TestTelemetryFrame:
    """Verify telemetry frames report steps consistent with the new STEPS_PER_MM."""

    def test_frame_for_one_mm(self):
        result = frame(1)
        assert result["steps"] == 8
        assert result["unit"] == "steps"

    def test_frame_for_zero_mm(self):
        result = frame(0)
        assert result["steps"] == 0
        assert result["unit"] == "steps"

    def test_frame_for_ten_mm(self):
        result = frame(10)
        assert result["steps"] == 80
        assert result["unit"] == "steps"

    def test_frame_returns_dict(self):
        result = frame(5)
        assert isinstance(result, dict)

    def test_frame_has_required_keys(self):
        result = frame(1)
        assert "steps" in result
        assert "unit" in result


class TestGaugePosition:
    """Verify gauge position_mm uses the updated units."""

    def test_position_mm_with_eighty_steps(self):
        # 80 steps / 8 steps/mm = 10 mm
        assert position_mm(80) == 10

    def test_position_mm_with_sixteen_steps(self):
        # 16 steps / 8 steps/mm = 2 mm
        assert position_mm(16) == 2

    def test_position_mm_with_zero_steps(self):
        assert position_mm(0) == 0

    def test_position_mm_with_partial_mm(self):
        # 12 steps / 8 = 1 mm (integer division)
        assert position_mm(12) == 1


class TestRoundTripConsistency:
    """Verify that converting mm->steps->mm is consistent with the new rate."""

    def test_round_trip_one_mm(self):
        mm = 1
        steps = to_steps(mm)
        back = to_millimetres(steps)
        assert back == mm

    def test_round_trip_ten_mm(self):
        mm = 10
        steps = to_steps(mm)
        back = to_millimetres(steps)
        assert back == mm

    def test_round_trip_hundred_mm(self):
        mm = 100
        steps = to_steps(mm)
        back = to_millimetres(steps)
        assert back == mm
