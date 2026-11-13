# L6_L7_29 — Smart Thermostat Controller

Lab 7: Fuzz Testing

## About

A small Python module that reads temperature setpoints, averages sensor readings and labels schedule slots.

## Files

| File | Description |
|------|-------------|
| `thermostat_control.py` | The code under test |
| `test_thermostat_control.py` | Hypothesis fuzz tests, regression tests and console tests |
| `requirements-dev.txt` | Test dependencies |
| `output/lab7/Lab7_Fuzz_Testing_Report.pdf` | Lab report with captured output panels |
| `output/lab7/evidence/` | Original source/test snapshots and execution logs |

## Run

From this `lab7` folder, with Python 3.8 or newer:

```console
python -m pip install -r requirements-dev.txt
python thermostat_control.py
python -m pytest test_thermostat_control.py
```

The handout's generic `processor.py` / `test_processor.py` names correspond to
`thermostat_control.py` / `test_thermostat_control.py` in this repository.

## Input validation contract

All three functions return `None` for invalid input, including `None` and
non-string types. The console prints an explanatory message and continues to
the next operation. Zero is a valid result.

- `parse_setpoint`: requires a finite number followed by C or F (case
  insensitive); returns Celsius rounded to one decimal place. Surrounding
  whitespace and scientific notation are allowed. Missing or unknown units,
  NaN and infinity are rejected. No physical temperature range is imposed
  because the starter project specifies none.
- `average_temperature`: requires at least one finite CSV reading. Surrounding
  whitespace is allowed. Empty fields or any invalid reading reject the whole
  input. `statistics.mean` prevents intermediate overflow and cancellation
  errors from the original `sum(values) / len(values)` calculation.
- `schedule_slot`: requires a 24-hour `HH:MM` time with ASCII digits; surrounding
  whitespace is allowed. Hours must be 00-23 and minutes 00-59. Night is
  00:00-05:59 and day is 06:00-23:59. The label retains two minute digits, e.g.
  `night 05` and `day 05`.

The starter did not specify error returns or time formatting precisely. These
rules make invalid-input handling and minute formatting consistent.

## Fuzzing and fixes

Before fixing the application, the completed starter fuzz tests failed for all
three functions. Hypothesis reduced failures to inputs such as `None`, `''`
and `':'`. The original source and initial fuzz tests are preserved as text
snapshots in the evidence folder so they do not interfere with test discovery.

The final suite combines Unicode/None fuzzing, wrong-type fuzzing, generated
valid inputs, numerical properties and explicit regressions. It checks that
accepted inputs produce correct results as well as checking for crashes.
Examples include `1,,3`, `NaNC`, `24:00`, the 06:00 boundary and very large
finite readings. The successful run contains **89 passing tests**.

The report reproduces captured execution output in clearly labelled panels;
these are not desktop screenshots. Desktop capture was unavailable in this
session. If literal terminal screenshots are required by the instructor, add
them before submission. The complete raw before/after outputs are included in
the evidence folder.
