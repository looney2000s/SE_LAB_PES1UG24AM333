"""Validate thermostat inputs; return None for invalid data."""

import math
import re
from statistics import mean


def parse_setpoint(text):
    """Convert a finite C/F setpoint to Celsius, rounded to one decimal.

    Unit letters are case insensitive and surrounding whitespace is allowed.
    Invalid types, missing/unknown units and non-finite numbers return None.
    """
    if not isinstance(text, str):
        return None
    text = text.strip()
    if len(text) < 2 or text[-1].upper() not in ('C', 'F'):
        return None
    try:
        value = float(text[:-1])
    except ValueError:
        return None
    if not math.isfinite(value):
        return None
    if text[-1].upper() == 'F':
        # Divide first so large finite inputs do not overflow during conversion.
        value = (value - 32) / 9 * 5
    return round(value, 1)

def average_temperature(readings_csv):
    """Average nonempty CSV readings, or return None if any field is invalid.

    Every reading must be finite; surrounding field whitespace is allowed.
    Do not silently discard missing or malformed sensor readings.
    """
    if not isinstance(readings_csv, str) or not readings_csv.strip():
        return None
    try:
        values = [float(reading) for reading in readings_csv.split(',')]
    except ValueError:
        return None
    if not all(math.isfinite(value) for value in values):
        return None
    # mean avoids the intermediate overflow/cancellation of sum(values) / n.
    return mean(values)

def schedule_slot(time_text):
    """Label a 24-hour HH:MM time, or return None for invalid input.

    Night covers 00:00-05:59; day covers 06:00-23:59. Minutes always
    contain two digits. Whitespace around the complete time is allowed.
    """
    if not isinstance(time_text, str):
        return None
    time_text = time_text.strip()
    if re.fullmatch(r'[0-9]{2}:[0-9]{2}', time_text) is None:
        return None
    hour, minute = map(int, time_text.split(':'))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    period = 'night' if hour < 6 else 'day'
    return f'{period} {minute:02d}'

def main():
    print("==== Running parse_setpoint ====")
    user_input = input("Enter a setpoint (e.g. 21.5C or 70F): ")
    result = parse_setpoint(user_input)
    if result is None:
        print("Invalid setpoint: enter a finite number followed by C or F.")
    else:
        print("Setpoint in Celsius:", result)

    print("\n==== Running average_temperature ====")
    user_input = input("Enter sensor readings as CSV (e.g. 20.5,21,22.5): ")
    result = average_temperature(user_input)
    if result is None:
        print("Invalid readings: enter finite numbers separated by commas.")
    else:
        print("Average Temperature:", result)

    print("\n==== Running schedule_slot ====")
    user_input = input("Enter a time as HH:MM (e.g. 07:30): ")
    result = schedule_slot(user_input)
    if result is None:
        print("Invalid time: enter HH:MM from 00:00 to 23:59.")
    else:
        print("Schedule Slot:", result)

if __name__ == "__main__":
    main()
