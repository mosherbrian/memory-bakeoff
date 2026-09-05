from culvert.gauge import position_mm
from culvert.telemetry import frame

class TestFirmwareChangePosition:
    """Tests for the new firmware reporting 8 steps per mm."""

    def test_position_80_steps_reports_10_mm(self):
        """REQUIREMENT: a reading of 80 steps must report 10 millimetres."""
        assert position_mm(80) == 10

    def test_position_40_steps_reports_5_mm(self):
        """REQUIREMENT: a reading of 80 steps must report 10 millimetres."""
        assert position_mm(40) == 5

    def test_position_0_steps_reports_0_mm(self):
        """REQUIREMENT: a reading of 80 steps must report 10 millimetres."""
        assert position_mm(0) == 0

    def test_position_16_steps_reports_2_mm(self):
        """REQUIREMENT: a reading of 80 steps must report 10 millimetres."""
        assert position_mm(16) == 2

    def test_position_7_steps_reports_0_mm_integer_division(self):
        """REQUIREMENT: a reading of 80 steps must report 10 millimetres."""
        assert position_mm(7) == 0

class TestTelemetryBackwardCompatibility:
    """Tests for telemetry frames keeping the same number of steps."""

    def test_frame_10_mm_reports_40_steps(self):
        """REQUIREMENT: A telemetry frame for 10 millimetres must still say 40 steps."""
        result = frame(10)
        assert result['mm'] == 10
        assert result['steps'] == 40

    def test_frame_0_mm_reports_0_steps(self):
        """REQUIREMENT: A telemetry frame for 10 millimetres must still say 40 steps."""
        result = frame(0)
        assert result['mm'] == 0
        assert result['steps'] == 0

    def test_frame_5_mm_reports_20_steps(self):
        """REQUIREMENT: A telemetry frame for 10 millimetres must still say 40 steps."""
        result = frame(5)
        assert result['mm'] == 5
        assert result['steps'] == 20

    def test_frame_1_mm_reports_4_steps(self):
        """REQUIREMENT: A telemetry frame for 10 millimetres must still say 40 steps."""
        result = frame(1)
        assert result['mm'] == 1
        assert result['steps'] == 4

    def test_frame_returns_dict_with_mm_and_steps_keys(self):
        """REQUIREMENT: A telemetry frame for 10 millimetres must still say 40 steps."""
        result = frame(10)
        assert isinstance(result, dict)
        assert 'mm' in result
        assert 'steps' in result

    def test_frame_mm_value_matches_input(self):
        """REQUIREMENT: A telemetry frame for 10 millimetres must still say 40 steps."""
        for mm_val in [1, 5, 10, 100]:
            result = frame(mm_val)
            assert result['mm'] == mm_val