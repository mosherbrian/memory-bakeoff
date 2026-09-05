from culvert.units import STEPS_PER_MM, to_millimetres, to_steps
from culvert.gauge import position_mm
from culvert.telemetry import frame


# REQUIREMENT: The gate controller firmware changed. It now reports 8 encoder steps per
# millimetre of gate travel, where it previously reported 4.
def test_steps_per_mm_is_8():
    assert STEPS_PER_MM == 8


# REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
# reading of 80 steps must report 10 millimetres.
def test_position_80_steps_is_10_mm():
    assert position_mm(80) == 10


# REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
# reading of 80 steps must report 10 millimetres.
def test_to_millimetres_80_is_10():
    assert to_millimetres(80) == 10


# REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
# for a given millimetre position as they did before the firmware change.
def test_frame_steps_unchanged_for_10_mm():
    # Before: 10 mm * 4 steps/mm = 40 steps
    # After: telemetry must still report 40 steps for 10 mm
    result = frame(10)
    assert result["steps"] == 40


# REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
# for a given millimetre position as they did before the firmware change. A
# telemetry frame for 10 millimetres must still say 40 steps.
def test_frame_10_mm_has_40_steps():
    result = frame(10)
    assert result["steps"] == 40


# REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
# for a given millimetre position as they did before the firmware change. A
# telemetry frame for 10 millimetres must still say 40 steps.
def test_frame_10_mm_has_correct_mm():
    result = frame(10)
    assert result["mm"] == 10


# REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
# for a given millimetre position as they did before the firmware change.
def test_frame_5_mm_has_20_steps():
    # Before: 5 mm * 4 steps/mm = 20 steps
    result = frame(5)
    assert result["steps"] == 20


# REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
# for a given millimetre position as they did before the firmware change.
def test_frame_1_mm_has_4_steps():
    # Before: 1 mm * 4 steps/mm = 4 steps
    result = frame(1)
    assert result["steps"] == 4


# REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
# reading of 80 steps must report 10 millimetres.
def test_position_40_steps_is_5_mm():
    # 40 steps / 8 steps/mm = 5 mm
    assert position_mm(40) == 5


# REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
# reading of 80 steps must report 10 millimetres.
def test_position_0_steps_is_0_mm():
    assert position_mm(0) == 0
