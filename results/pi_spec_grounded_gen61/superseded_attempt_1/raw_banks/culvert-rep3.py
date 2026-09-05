from culvert.units import STEPS_PER_MM, to_millimetres, to_steps
from culvert.gauge import position_mm
from culvert.telemetry import frame


# REQUIREMENT: The gate controller firmware changed. It now reports 8 encoder steps per
# millimetre of gate travel, where it previously reported 4.
def test_steps_per_mm_is_eight():
    assert STEPS_PER_MM == 8


# REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
# reading of 80 steps must report 10 millimetres.
def test_position_mm_80_steps_is_10_mm():
    assert position_mm(80) == 10


# REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
# reading of 80 steps must report 10 millimetres.
def test_to_millimetres_80_steps_is_10_mm():
    assert to_millimetres(80) == 10


# REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
# for a given millimetre position as they did before the firmware change.
def test_frame_10_mm_reports_40_steps():
    result = frame(10)
    assert result["steps"] == 40


# REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
# for a given millimetre position as they did before the firmware change.
def test_frame_10_mm_reports_10_mm():
    result = frame(10)
    assert result["mm"] == 10


# REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
# for a given millimetre position as they did before the firmware change.
def test_to_steps_10_mm_is_40_steps():
    assert to_steps(10) == 40


# REQUIREMENT: The control room's telemetry frames must keep reporting the SAME number of steps
# for a given millimetre position as they did before the firmware change.
def test_frame_other_position_5_mm_reports_20_steps():
    result = frame(5)
    assert result["steps"] == 20


# REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
# reading of 80 steps must report 10 millimetres.
def test_position_mm_40_steps_is_5_mm():
    assert position_mm(40) == 5


# REQUIREMENT: Update the package so that gate positions are computed from the new ratio: a
# reading of 80 steps must report 10 millimetres.
def test_to_millimetres_40_steps_is_5_mm():
    assert to_millimetres(40) == 5
