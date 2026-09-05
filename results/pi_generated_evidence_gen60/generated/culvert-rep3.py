from culvert.units import STEPS_PER_MM, to_millimetres, to_steps
from culvert.gauge import position_mm
from culvert.telemetry import frame


class TestFirmwareRatio:
    """Verify the STEPS_PER_MM constant was updated to 8."""

    def test_steps_per_mm_is_8(self):
        assert STEPS_PER_MM == 8

    def test_position_80_steps_is_10_mm(self):
        # 80 steps / 8 steps_per_mm = 10 mm
        assert position_mm(80) == 10

    def test_position_40_steps_is_5_mm(self):
        # 40 steps / 8 steps_per_mm = 5 mm
        assert position_mm(40) == 5

    def test_position_0_steps_is_0_mm(self):
        assert position_mm(0) == 0

    def test_position_100_steps_is_12_mm(self):
        # 100 // 8 = 12 (integer division)
        assert position_mm(100) == 12

    def test_position_79_steps_is_9_mm(self):
        # 79 // 8 = 9
        assert position_mm(79) == 9


class TestTelemetryStepsUnchanged:
    """Verify telemetry frames still report the SAME number of steps as before.
    
    Before the firmware change, STEPS_PER_MM was 4, so to_steps(mm) = mm * 4.
    The instruction says telemetry must keep reporting the same number of steps.
    So to_steps should still use the old ratio of 4, not the new 8.
    
    A telemetry frame for 10 mm must still say 40 steps (10 * 4).
    """

    def test_frame_10_mm_reports_40_steps(self):
        # 10 mm * 4 (old ratio) = 40 steps
        assert frame(10) == {"mm": 10, "steps": 40}

    def test_frame_1_mm_reports_4_steps(self):
        assert frame(1) == {"mm": 1, "steps": 4}

    def test_frame_0_mm_reports_0_steps(self):
        assert frame(0) == {"mm": 0, "steps": 0}

    def test_frame_5_mm_reports_20_steps(self):
        assert frame(5) == {"mm": 5, "steps": 20}

    def test_frame_25_mm_reports_100_steps(self):
        assert frame(25) == {"mm": 25, "steps": 100}

    def test_to_steps_uses_old_ratio(self):
        # to_steps should still multiply by 4, not 8
        assert to_steps(1) == 4
        assert to_steps(10) == 40
        assert to_steps(100) == 400


class TestToMillimetresUsesNewRatio:
    """Verify to_millimetres uses the new ratio of 8."""

    def test_to_millimetres_80_steps(self):
        assert to_millimetres(80) == 10

    def test_to_millimetres_16_steps(self):
        assert to_millimetres(16) == 2

    def test_to_millimetres_24_steps(self):
        assert to_millimetres(24) == 3

    def test_to_millimetres_7_steps(self):
        # 7 // 8 = 0
        assert to_millimetres(7) == 0

    def test_to_millimetres_8_steps(self):
        assert to_millimetres(8) == 1
