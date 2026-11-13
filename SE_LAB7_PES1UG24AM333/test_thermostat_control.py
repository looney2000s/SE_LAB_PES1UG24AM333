"""Fuzz malformed inputs and verify meaningful thermostat properties."""

import math
import sys
from decimal import Decimal, localcontext

import pytest
from hypothesis import example, given, settings, strategies as st
from thermostat_control import parse_setpoint, average_temperature, schedule_slot

@given(st.text() | st.none())
@settings(max_examples=200)
@example(None)
@example('')
def test_parse_setpoint_no_crash(s):
    result = parse_setpoint(s)
    assert result is None or (isinstance(result, float) and math.isfinite(result))

@given(st.text() | st.none())
@settings(max_examples=200)
@example(None)
@example('')
def test_average_temperature_no_crash(s):
    result = average_temperature(s)
    assert result is None or (isinstance(result, float) and math.isfinite(result))

@given(st.text() | st.none())
@settings(max_examples=200)
@example(None)
@example('')
@example(':')
def test_schedule_slot_no_crash(s):
    result = schedule_slot(s)
    assert result is None or (
        result.startswith(('day ', 'night '))
        and len(result.split()[1]) == 2
        and 0 <= int(result.split()[1]) <= 59
    )


@pytest.mark.parametrize('function', [parse_setpoint, average_temperature, schedule_slot])
@given(st.one_of(st.integers(), st.floats(), st.booleans(), st.binary(),
                 st.lists(st.integers()), st.dictionaries(st.text(), st.integers())))
def test_non_string_inputs_are_rejected(function, value):
    assert function(value) is None


@pytest.mark.parametrize('text, expected', [
    ('21.5C', 21.5), ('70F', 21.1), ('32F', 0.0), ('212F', 100.0),
    ('-40f', -40.0), ('  21.5c  ', 21.5), ('0C', 0.0), ('1e2C', 100.0),
])
def test_setpoint_examples(text, expected):
    assert parse_setpoint(text) == expected


@pytest.mark.parametrize('text', [
    None, '', ' ', 'C', 'F', '21', '21K', '21X', '21CC', 'bad',
    'NaNC', 'infC', '-InfinityF', '1e309C', '1e309F', '2\x00C',
])
def test_invalid_setpoints(text):
    assert parse_setpoint(text) is None


@given(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
def test_celsius_rounding(value):
    assert parse_setpoint(f'{value!r}C') == round(value, 1)


@given(st.integers(min_value=-10000, max_value=10000))
def test_fahrenheit_conversion_matches_decimal(tenths):
    # Independent decimal oracle avoids repeating the implementation's formula.
    value = Decimal(tenths) / 10
    expected = float(round((value - Decimal(32)) * Decimal(5) / Decimal(9), 1))
    assert parse_setpoint(f'{value}F') == expected


@pytest.mark.parametrize('unit', ['C', 'F'])
@given(st.floats(allow_nan=False, allow_infinity=False))
def test_finite_setpoints_remain_finite(unit, value):
    result = parse_setpoint(f'{value!r}{unit}')
    assert result is not None and math.isfinite(result)


@pytest.mark.parametrize('text, expected', [
    ('20.5,21,22.5', 64 / 3), (' 20 , 22 ', 21.0), ('-10,0,10', 0.0),
    ('0', 0.0), ('21.5', 21.5), ('1e308,1e308', 1e308),
    ('1e308,1,-1e308', 1 / 3),
])
def test_average_examples(text, expected):
    assert average_temperature(text) == pytest.approx(expected)


@pytest.mark.parametrize('text', [
    None, '', ' ', ',', '1,,3', '1,', ',1', 'one,two', '20, ,21',
    'nan', '20,nan', 'inf', '-inf,1', '1e309,2', '20;21', '2\x00',
])
def test_invalid_readings(text):
    assert average_temperature(text) is None


@given(st.lists(st.integers(min_value=-100000, max_value=100000), min_size=1, max_size=50))
def test_average_matches_integer_oracle_and_is_order_independent(values):
    csv = ','.join(map(str, values))
    result = average_temperature(csv)
    assert result == pytest.approx(sum(values) / len(values))
    assert min(values) <= result <= max(values)
    assert average_temperature(','.join(map(str, reversed(values)))) == result


@given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=30))
@example([sys.float_info.max, sys.float_info.max])
@example([1e308, 1.0, -1e308])
def test_average_extreme_finite_values(values):
    result = average_temperature(','.join(map(repr, values)))
    # Enough precision to retain even subnormal floats when mixed with 1e308.
    with localcontext() as context:
        context.prec = 1100
        expected = float(sum(map(Decimal.from_float, values)) / len(values))
    assert result is not None and math.isfinite(result)
    assert result == expected
    assert min(values) <= result <= max(values)


@given(st.lists(st.integers(), min_size=2, max_size=20), st.data())
def test_missing_csv_field_is_rejected(values, data):
    fields = list(map(str, values))
    fields[data.draw(st.integers(min_value=0, max_value=len(fields) - 1))] = ''
    assert average_temperature(','.join(fields)) is None


@pytest.mark.parametrize('text, expected', [
    ('00:00', 'night 00'), ('05:59', 'night 59'), ('06:00', 'day 00'),
    ('07:05', 'day 05'), ('23:59', 'day 59'), (' 07:30 ', 'day 30'),
])
def test_schedule_examples(text, expected):
    assert schedule_slot(text) == expected


@pytest.mark.parametrize('text', [
    None, '', ':', '24:00', '23:60', '-1:00', '12:-1', '12:xx',
    '00:xx', '6:30', '06:3', '12:30:00', '12:30extra', '+1:00',
    '12 :30', '\u0660\u0666:\u0663\u0660', '12:3\x00',
])
def test_invalid_times(text):
    assert schedule_slot(text) is None


@given(st.integers(min_value=0, max_value=23), st.integers(min_value=0, max_value=59))
def test_valid_schedule_times(hour, minute):
    expected = f"{'night' if hour < 6 else 'day'} {minute:02d}"
    assert schedule_slot(f'{hour:02d}:{minute:02d}') == expected


@given(st.integers(min_value=24, max_value=99), st.integers(min_value=0, max_value=59))
def test_out_of_range_hours(hour, minute):
    assert schedule_slot(f'{hour:02d}:{minute:02d}') is None


@given(st.integers(min_value=0, max_value=23), st.integers(min_value=60, max_value=99))
def test_out_of_range_minutes(hour, minute):
    assert schedule_slot(f'{hour:02d}:{minute:02d}') is None


@pytest.mark.parametrize('answers, expected', [
    (['70F', '20.5,21,22.5', '07:05'],
     ['Setpoint in Celsius: 21.1', 'Average Temperature:', 'Schedule Slot: day 05']),
    (['bad', '1,,3', '24:00'], ['Invalid setpoint:', 'Invalid readings:', 'Invalid time:']),
    (['0C', '0', '00:00'],
     ['Setpoint in Celsius: 0.0', 'Average Temperature: 0.0', 'Schedule Slot: night 00']),
])
def test_interactive_app(monkeypatch, capsys, answers, expected):
    from thermostat_control import main

    inputs = iter(answers)
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    main()
    output = capsys.readouterr().out
    for message in expected:
        assert message in output
