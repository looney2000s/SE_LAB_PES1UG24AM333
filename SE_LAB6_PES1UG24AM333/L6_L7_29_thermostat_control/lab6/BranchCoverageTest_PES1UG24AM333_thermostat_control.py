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

@pytest.mark.parametrize(
    "hour, expected",
    [
        (5, 18),
        (6, 20),
        (21, 20),
        (22, 18),
        (23, 18),
    ],
)
def test_sleep_time_boundaries(hour, expected):
    assert target_temperature("sleep", True, hour) == expected


@pytest.mark.parametrize(
    "hour, expected",
    [
        (5, 20),
        (6, 22),
        (8, 22),
        (9, 20),
        (16, 20),
        (17, 21),
        (21, 21),
        (22, 20),
    ],
)
def test_occupied_time_boundaries(hour, expected):
    assert target_temperature("home", True, hour) == expected


@pytest.mark.parametrize(
    "mode, occupied, hour, expected",
    [
        ("away", False, 7, 16),
        ("sleep", False, 12, 20),
        ("home", False, 7, 18),
        ("home", False, 18, 18),
    ],
)
def test_mode_and_occupancy_priority(mode, occupied, hour, expected):
    assert target_temperature(mode, occupied, hour) == expected


@pytest.mark.parametrize(
    "current, target, outside, expected",
    [
        (19.5, 20, 0, "idle"),
        (20.5, 20, 35, "idle"),
        (19, 20, 4, "heat_boost"),
        (19, 20, 5, "heat"),
        (21, 20, 30, "cool"),
        (21, 20, 31, "cool_boost"),
    ],
)
def test_hvac_boundaries(current, target, outside, expected):
    assert hvac_action(current, target, outside) == expected


@pytest.mark.parametrize(
    "readings, limit, expected",
    [
        ([5, 9], 10, "ok"),
        ([10, 10], 10, "ok"),
        ([11], 10, "critical"),
        ([11, 9, 9], 10, "warning"),
        ([11, 12, 9, 10], 10, "warning"),
        ([11, 12, 13, 10], 10, "critical"),
    ],
)
def test_energy_alert_boundaries(readings, limit, expected):
    assert energy_alert(readings, limit) == expected