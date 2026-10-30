import pytest

from thermostat_control import (
    target_temperature,
    hvac_action,
    energy_alert,
)


@pytest.mark.parametrize(
    "mode, occupied, hour, expected",
    [
        ("away", True, 12, 16),
        ("sleep", True, 2, 18),
        ("sleep", True, 12, 20),
        ("home", False, 12, 18),
        ("home", True, 7, 22),
        ("home", True, 18, 21),
        ("home", True, 12, 20),
    ],
)
def test_target_temperature(mode, occupied, hour, expected):
    assert target_temperature(mode, occupied, hour) == expected


@pytest.mark.parametrize(
    "current, target, outside, expected",
    [
        (20, 20, 15, "idle"),
        (18, 20, 0, "heat_boost"),
        (18, 20, 10, "heat"),
        (24, 20, 35, "cool_boost"),
        (24, 20, 25, "cool"),
    ],
)
def test_hvac_action(current, target, outside, expected):
    assert hvac_action(current, target, outside) == expected


@pytest.mark.parametrize(
    "readings, limit, expected",
    [
        ([], 10, "ok"),
        ([11, 12, 9], 10, "critical"),
        ([11, 9], 10, "warning"),
    ],
)
def test_energy_alert(readings, limit, expected):
    assert energy_alert(readings, limit) == expected