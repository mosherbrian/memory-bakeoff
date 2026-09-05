import pytest
from sluice.units import STEPS_PER_MM, to_millimetres, to_steps
from sluice.telemetry import frame
from sluice.gauge import position_mm


class TestStepsPerMmConstant:
    """Verify the firmware constant was updated from 4 to 8."""

    def test_steps_per_mm_is_eight(self):
        assert STEPS_PER_MM == 8

    def test_steps_per_mm_is_not_four(self):
        assert STEPS_PER_MM != 4


class TestToStepsConversion:
    """Verify to_steps uses the new 8 steps/mm ratio."""

    def test_zero_mm_to_steps(self):
        assert to_steps(0) == 0

    def test_one_mm_to_steps(self):
        assert to_steps(1) == 8

    def test_two_mm_to_steps(self):
        assert to_steps(2) == 16

    def test_ten_mm_to_steps(self):
        assert to_steps(10) == 80

    def test_negative_mm_to_steps(self):
        assert to_steps(-1) == -8


class TestToMillimetresConversion:
    """Verify to_millimetres correctly converts steps to mm with 8 spm."""

    def test_zero_steps_to_mm(self):
        assert to_millimetres(0) == 0

    def test_eight_steps_to_mm(self):
        assert to_millimetres(8) == 1

    def test_sixteen_steps_to_mm(self):
        assert to_millimetres(16) == 2

    def test_ten_steps_to_mm(self):
        # 10 // 8 = 1
        assert to_millimetres(10) == 1

    def test_seven_steps_to_mm(self):
        # 7 // 8 = 0
        assert to_millimetres(7) == 0

    def test_negative_steps_to_mm(self):
        assert to_millimetres(-8) == -1


class TestGaugePosition:
    """Verify the gauge correctly interprets raw steps as millimetres."""

    def test_position_mm_with_raw_80(self):
        # 80 steps / 8 spm = 10 mm
        assert position_mm(80) == 10

    def test_position_mm_with_raw_16(self):
        # 16 steps / 8 spm = 2 mm
        assert position_mm(16) == 2

    def test_position_mm_with_raw_0(self):
        assert position_mm(0) == 0

    def test_position_mm_with_raw_8(self):
        assert position_mm(8) == 1

    def test_position_mm_with_raw_7(self):
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

    def test_frame_for_raw_40(self):
        """End-to-end: raw 40 steps should still produce frame with 40 steps."""
        mm = position_mm(40)
        f = frame(mm)
        assert f["steps"] == 40

    def test_frame_for_raw_80(self):
        """End-to-end: raw 80 steps should still produce frame with 80 steps."""
        mm = position_mm(80)
        f = frame(mm)
        assert f["steps"] == 80

    def test_frame_for_raw_0(self):
        """End-to-end: raw 0 steps should still produce frame with 0 steps."""
        mm = position_mm(0)
        f = frame(mm)
        assert f["steps"] == 0

    def test_frame_for_raw_8(self):
        """End-to-end: raw 8 steps should still produce frame with 8 steps."""
        mm = position_mm(8)
        f = frame(mm)
        assert f["steps"] == 8

    def test_frame_unit_is_steps(self):
        f = frame(10)
        assert f["unit"] == "steps"

    def test_frame_structure(self):
        f = frame(5)
        assert isinstance(f, dict)
        assert "steps" in f
        assert "unit" in f

    def test_frame_preserves_roundtrip_for_various_values(self):
        """Test multiple raw values to ensure roundtrip consistency."""
        for raw in [0, 8, 16, 24, 32, 40, 48, 56, 64, 100, 1000]:
            mm = position_mm(raw)
            f = frame(mm)
            assert f["steps"] == raw, f"Failed for raw={raw}, got steps={f['steps']}"
