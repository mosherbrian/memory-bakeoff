# --- IP1-rep1 ---
import pytest
from sluice.units import STEPS_PER_MM, to_steps, to_millimetres
from sluice.gauge import position_mm
from sluice.telemetry import frame


class TestStepsPerMmConstant:
    """Verify the firmware change is reflected in the constant."""

    def test_r1_steps_per_mm_is_eight(self):
        assert STEPS_PER_MM == 8


class TestToMillimetres:
    """Verify conversion from raw steps to millimetres uses the new rate."""

    def test_r1_basic_conversion(self):
        # 8 steps per mm means 80 steps = 10 mm
        assert to_millimetres(80) == 10

    def test_r1_half_mm(self):
        assert to_millimetres(4) == 0  # 4 // 8 = 0

    def test_r1_exact_mm(self):
        assert to_millimetres(16) == 2

    def test_r1_partial_mm_rounds_down(self):
        # 10 steps = 1.25 mm, should floor to 1
        assert to_millimetres(10) == 1

    def test_r1_zero(self):
        assert to_millimetres(0) == 0


class TestToSteps:
    """Verify conversion from millimetres to steps uses the new rate."""

    def test_r1_basic_conversion(self):
        # 8 steps per mm means 10 mm = 80 steps
        assert to_steps(10) == 80

    def test_r1_one_mm(self):
        assert to_steps(1) == 8

    def test_r1_zero_mm(self):
        assert to_steps(0) == 0

    def test_r1_half_mm(self):
        assert to_steps(0) == 0  # 0 mm -> 0 steps

    def test_r1_large_value(self):
        assert to_steps(100) == 800


class TestGaugePosition:
    """Verify position_mm uses the updated conversion."""

    def test_r1_position_mm_with_new_constant(self):
        # With 8 steps/mm, raw 80 should give 10 mm
        assert position_mm(80) == 10

    def test_r1_position_mm_raw_16(self):
        assert position_mm(16) == 2

    def test_r1_position_mm_raw_4(self):
        assert position_mm(4) == 0

    def test_r1_position_mm_raw_0(self):
        assert position_mm(0) == 0


class TestTelemetryFrame:
    """Verify telemetry frames report steps consistent with new rate."""

    def test_r1_frame_steps_for_10_mm(self):
        # 10 mm should report 80 steps (10 * 8)
        result = frame(10)
        assert result["steps"] == 80
        assert result["unit"] == "steps"

    def test_r1_frame_steps_for_1_mm(self):
        result = frame(1)
        assert result["steps"] == 8

    def test_r1_frame_steps_for_0_mm(self):
        result = frame(0)
        assert result["steps"] == 0

    def test_r1_frame_steps_for_5_mm(self):
        result = frame(5)
        assert result["steps"] == 40

    def test_r1_frame_unit_is_steps(self):
        result = frame(10)
        assert result["unit"] == "steps"

    def test_r1_frame_has_required_keys(self):
        result = frame(10)
        assert "steps" in result
        assert "unit" in result


# --- IP1-rep2 ---
import pytest
from sluice.units import STEPS_PER_MM, to_millimetres, to_steps
from sluice.telemetry import frame
from sluice.gauge import position_mm


class TestStepsPerMmConstant:
    """Verify the firmware constant is updated to 8."""

    def test_r2_steps_per_mm_is_eight(self):
        assert STEPS_PER_MM == 8

    def test_r2_steps_per_mm_is_not_four(self):
        # Ensure old value is not present
        assert STEPS_PER_MM != 4


class TestToSteps:
    """Verify to_steps converts mm to steps using the new rate."""

    def test_r2_one_mm_is_eight_steps(self):
        assert to_steps(1) == 8

    def test_r2_zero_mm_is_zero_steps(self):
        assert to_steps(0) == 0

    def test_r2_two_mm_is_sixteen_steps(self):
        assert to_steps(2) == 16

    def test_r2_ten_mm_is_eighty_steps(self):
        assert to_steps(10) == 80

    def test_r2_negative_mm_is_negative_steps(self):
        assert to_steps(-1) == -8


class TestToMillimetres:
    """Verify to_millimetres converts steps to mm using the new rate."""

    def test_r2_eight_steps_is_one_mm(self):
        assert to_millimetres(8) == 1

    def test_r2_zero_steps_is_zero_mm(self):
        assert to_millimetres(0) == 0

    def test_r2_sixteen_steps_is_two_mm(self):
        assert to_millimetres(16) == 2

    def test_r2_eighty_steps_is_ten_mm(self):
        assert to_millimetres(80) == 10

    def test_r2_partial_mm_is_rolled_down(self):
        # 9 steps should be 1 mm (integer division)
        assert to_millimetres(9) == 1

    def test_r2_seven_steps_is_zero_mm(self):
        # 7 steps is less than 1 mm, so 0
        assert to_millimetres(7) == 0

    def test_r2_negative_steps_is_negative_mm(self):
        assert to_millimetres(-8) == -1


class TestTelemetryFrame:
    """Verify telemetry frames report steps consistent with the new STEPS_PER_MM."""

    def test_r2_frame_for_one_mm(self):
        result = frame(1)
        assert result["steps"] == 8
        assert result["unit"] == "steps"

    def test_r2_frame_for_zero_mm(self):
        result = frame(0)
        assert result["steps"] == 0
        assert result["unit"] == "steps"

    def test_r2_frame_for_ten_mm(self):
        result = frame(10)
        assert result["steps"] == 80
        assert result["unit"] == "steps"

    def test_r2_frame_returns_dict(self):
        result = frame(5)
        assert isinstance(result, dict)

    def test_r2_frame_has_required_keys(self):
        result = frame(1)
        assert "steps" in result
        assert "unit" in result


class TestGaugePosition:
    """Verify gauge position_mm uses the updated units."""

    def test_r2_position_mm_with_eighty_steps(self):
        # 80 steps / 8 steps/mm = 10 mm
        assert position_mm(80) == 10

    def test_r2_position_mm_with_sixteen_steps(self):
        # 16 steps / 8 steps/mm = 2 mm
        assert position_mm(16) == 2

    def test_r2_position_mm_with_zero_steps(self):
        assert position_mm(0) == 0

    def test_r2_position_mm_with_partial_mm(self):
        # 12 steps / 8 = 1 mm (integer division)
        assert position_mm(12) == 1


class TestRoundTripConsistency:
    """Verify that converting mm->steps->mm is consistent with the new rate."""

    def test_r2_round_trip_one_mm(self):
        mm = 1
        steps = to_steps(mm)
        back = to_millimetres(steps)
        assert back == mm

    def test_r2_round_trip_ten_mm(self):
        mm = 10
        steps = to_steps(mm)
        back = to_millimetres(steps)
        assert back == mm

    def test_r2_round_trip_hundred_mm(self):
        mm = 100
        steps = to_steps(mm)
        back = to_millimetres(steps)
        assert back == mm


# --- IP1-rep3 ---
import pytest
from sluice.units import STEPS_PER_MM, to_millimetres, to_steps
from sluice.telemetry import frame
from sluice.gauge import position_mm


class TestStepsPerMmConstant:
    """Verify the firmware constant was updated from 4 to 8."""

    def test_r3_steps_per_mm_is_eight(self):
        assert STEPS_PER_MM == 8

    def test_r3_steps_per_mm_is_not_four(self):
        assert STEPS_PER_MM != 4


class TestToStepsConversion:
    """Verify to_steps uses the new 8 steps/mm ratio."""

    def test_r3_zero_mm_to_steps(self):
        assert to_steps(0) == 0

    def test_r3_one_mm_to_steps(self):
        assert to_steps(1) == 8

    def test_r3_two_mm_to_steps(self):
        assert to_steps(2) == 16

    def test_r3_ten_mm_to_steps(self):
        assert to_steps(10) == 80

    def test_r3_negative_mm_to_steps(self):
        assert to_steps(-1) == -8


class TestToMillimetresConversion:
    """Verify to_millimetres correctly converts steps to mm with 8 spm."""

    def test_r3_zero_steps_to_mm(self):
        assert to_millimetres(0) == 0

    def test_r3_eight_steps_to_mm(self):
        assert to_millimetres(8) == 1

    def test_r3_sixteen_steps_to_mm(self):
        assert to_millimetres(16) == 2

    def test_r3_ten_steps_to_mm(self):
        # 10 // 8 = 1
        assert to_millimetres(10) == 1

    def test_r3_seven_steps_to_mm(self):
        # 7 // 8 = 0
        assert to_millimetres(7) == 0

    def test_r3_negative_steps_to_mm(self):
        assert to_millimetres(-8) == -1


class TestGaugePosition:
    """Verify the gauge correctly interprets raw steps as millimetres."""

    def test_r3_position_mm_with_raw_80(self):
        # 80 steps / 8 spm = 10 mm
        assert position_mm(80) == 10

    def test_r3_position_mm_with_raw_16(self):
        # 16 steps / 8 spm = 2 mm
        assert position_mm(16) == 2

    def test_r3_position_mm_with_raw_0(self):
        assert position_mm(0) == 0

    def test_r3_position_mm_with_raw_8(self):
        assert position_mm(8) == 1

    def test_r3_position_mm_with_raw_7(self):
        # 7 // 8 = 0
        assert position_mm(7) == 0


class TestTelemetryFrame:
    """Verify telemetry frames report the correct steps for a given mm position.
    
    The instruction says: "The control room's telemetry frames must keep reporting
    the same steps value for a given millimetre position as they do today."
    
    Before the change: STEPS_PER_MM = 4, so to_steps(mm) = mm * 4.
    After the change: STEPS_PER_MM = 8, so to_steps(mm) = mm * 8.
    
    But wait - the gauge now divides by 8 instead of 4. So for the SAME raw steps,
    we get HALF the mm position. Then to_steps on that mm position gives mm * 8.
    
    Let's trace:
    Before: raw=40 -> position_mm = 40//4 = 10 -> frame steps = 10*4 = 40
    After:  raw=40 -> position_mm = 40//8 = 5  -> frame steps = 5*8 = 40
    
    So the frame should still report 40 for raw input 40. The key insight is that
    the end-to-end roundtrip should preserve the original raw steps value.
    """

    def test_r3_frame_for_raw_40(self):
        """End-to-end: raw 40 steps should still produce frame with 40 steps."""
        mm = position_mm(40)
        f = frame(mm)
        assert f["steps"] == 40

    def test_r3_frame_for_raw_80(self):
        """End-to-end: raw 80 steps should still produce frame with 80 steps."""
        mm = position_mm(80)
        f = frame(mm)
        assert f["steps"] == 80

    def test_r3_frame_for_raw_0(self):
        """End-to-end: raw 0 steps should still produce frame with 0 steps."""
        mm = position_mm(0)
        f = frame(mm)
        assert f["steps"] == 0

    def test_r3_frame_for_raw_8(self):
        """End-to-end: raw 8 steps should still produce frame with 8 steps."""
        mm = position_mm(8)
        f = frame(mm)
        assert f["steps"] == 8

    def test_r3_frame_unit_is_steps(self):
        f = frame(10)
        assert f["unit"] == "steps"

    def test_r3_frame_structure(self):
        f = frame(5)
        assert isinstance(f, dict)
        assert "steps" in f
        assert "unit" in f

    def test_r3_frame_preserves_roundtrip_for_various_values(self):
        """Test multiple raw values to ensure roundtrip consistency."""
        for raw in [0, 8, 16, 24, 32, 40, 48, 56, 64, 100, 1000]:
            mm = position_mm(raw)
            f = frame(mm)
            assert f["steps"] == raw, f"Failed for raw={raw}, got steps={f['steps']}"
