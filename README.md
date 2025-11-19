# Formicabot Simulations

Small collection of Python scripts that drive NetLogo ant foraging models.

This folder includes a mock-based fallback so you can run and test the Python
experiment harness without installing NetLogo/Java. When NetLogo and Java are
available, the scripts will use the real `pyNetLogo` connection.

## Quick start (smoke test)

Run the lightweight smoke script which exercises the NetLogo bridge (uses the
mock fallback automatically if NetLogo is not installed):

```bash
python3 run_experiment_1.py
```

There is also a `pytest` smoke test that runs the same script:

```bash
pytest -q tests/test_smoke_run.py
```

## Run the experiment harness

`working_experiment.py` is an interactive runner. From the `formicabot_simulations`
directory you can run it non-interactively (answer `y` at the prompt programmatically):

```bash
cd formicabot_simulations
printf 'y\n' | python3 working_experiment.py
```

Outputs (JSON/CSV/PNG) are saved to `experiment_1_results/`.

## Enabling real NetLogo

To run with real NetLogo you must install:

- Java (JDK 8 or 11 is recommended)
- NetLogo (the scripts expect NetLogo 7.x by default)

Place NetLogo under a path and set `NETLOGO_HOME` or pass as argument where
supported. Example (Linux):

```bash
# after downloading and extracting NetLogo
export NETLOGO_HOME=/opt/netlogo-7.0.2
python3 run_experiment_1.py
```

If NetLogo is not on `PATH` or `NETLOGO_HOME` is not set, the code will fall
back to a mock implementation so you can run smoke tests and CI.

## Development

Install development dependencies (recommended in a virtualenv):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run lint and tests:

```bash
flake8 formicabot_simulations --max-line-length=120
pytest -q tests
```

## Limitations

- The mock NetLogo implementation is intentionally simple — it exercises the
  Python-side logic but does not simulate real NetLogo dynamics.
- For production-quality simulation results, install NetLogo + Java and run
  the scripts with a real NetLogo connection.

If you want, I can add a small CI badge and a more detailed developer guide.
