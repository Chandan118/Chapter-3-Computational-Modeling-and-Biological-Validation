# Overview

FormicaBot is a Python-based experimental harness for running NetLogo ant foraging simulations. The codebase coordinates Python experiment orchestration with NetLogo models, providing a graceful fallback to mock simulations when NetLogo/Java are unavailable.

## Architecture & Key Components

### Core Layers

1. **NetLogo Bridge** (`netlogo_utils.py`): 
   - Centralizes environment detection (Java, NetLogo paths)
   - Exports `init_netlogo()` which returns either real `pynetlogo.NetLogoLink` or `MockNetLogoLink`
   - **Key pattern**: Graceful fallback to mock for CI/development without losing functionality
   - See `find_netlogo_home()` for path priority: `NETLOGO_HOME` env var → `/opt/netlogo-*` → home directories

2. **Mock Implementation** (`MockNetLogoLink` in `netlogo_utils.py`):
   - Synthetic but deterministic NetLogo simulator (seeded with `Random(0)`)
   - Supports minimal API: `load_model()`, `command()`, `report()`, `repeat_report()`, `kill_workspace()`
   - Used automatically when NetLogo unavailable; **intentionally simple** to exercise Python logic, not NetLogo dynamics

3. **Experiment Classes** (e.g., `WorkingExperiment` in `working_experiment.py`):
   - Initialize NetLogo connection, load `.nlogo` model files
   - Run multi-trial/multi-colony loops with configurable parameters
   - Collect measurements at intervals, export to JSON/CSV/PNG

### Data Flow

```
experiment_*.py (user entry point)
    → init_netlogo() [real or mock]
    → load_model() [.nlogo file]
    → setup() → repeat [go] → report()
    → save to experiment_*_results/*.json, *.csv
```

## Project Structure

- **Models**: `*.nlogo` files (NetLogo 7.x format)
  - `final_ants.nlogo`: Primary working model
  - `working_ants.nlogo`, `pheidole_working.nlogo`: Variants
- **Runners**: `working_experiment.py`, `run_complete_experiment.py` (primary)
- **Results**: `experiment_1_results/`, `experiment_results/`, `results/` directories for output

## Developer Workflows

### Running Experiments Without NetLogo (Smoke Test)

```bash
python3 run_experiment_1.py
# Uses MockNetLogoLink automatically if NetLogo unavailable
```

### Running with Real NetLogo (if installed)

```bash
export NETLOGO_HOME=/opt/netlogo-7.0.2
python3 working_experiment.py
```

### Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Lint
flake8 . --max-line-length=120

# Run smoke tests (if tests/ directory exists)
pytest -q tests/
```

## Project-Specific Conventions & Patterns

1. **Environment Detection First**:
   - Always call `netlogo_utils.init_netlogo()` rather than direct `pynetlogo.NetLogoLink()` instantiation
   - This ensures fallback works transparently

2. **NetLogo Command Patterns**:
   - `setup`: Initialize model state
   - `go`: Single tick advance
   - `repeat N [go]`: Batch ticks for efficiency
   - `report <expr>`: Query model state (returns Python scalar)
   - Examples: `count turtles`, `count patches with [food > 0]`, `mean [chemical] of patches`

3. **Experiment Structure**:
   - Parameters at `__init__`: `num_trials`, `num_colonies`, `trial_duration`, `measurement_interval`
   - Trial loop: `for trial in range(num_trials): for colony in range(num_colonies): run_single_trial()`
   - Save per-trial JSON, aggregate to CSV

4. **Output Organization**:
   - Create timestamped result dirs (`experiment_1_results/`)
   - Per-trial JSON format: `{colony, trial, tick_list, metric_lists}`
   - Summary CSV per directory with aggregated stats

5. **Error Handling**:
   - Wrap NetLogo report calls in try-except (queries may fail in mock or edge cases)
   - Always call `netlogo.kill_workspace()` in finally blocks
   - Provide user-friendly error messages with context

## Critical Integration Points

- **PyNetLogo API** (`pynetlogo.NetLogoLink`): Used if Java/NetLogo available; see `pynetlogo` docs for all methods
- **pandas/numpy**: Data aggregation and analysis
- **seaborn/matplotlib**: Visualization (use `matplotlib.use('Agg')` for headless environments)
- **pathlib.Path**: Output directory management

## When Modifying Core Behavior

- Changes to `netlogo_utils.py` affect **all** experiment runners
- `MockNetLogoLink` changes must preserve the minimal API contract (commands above)
- Test both real and mock paths if modifying environment detection

## NetLogo Model Structure

Key model variables commonly queried in experiments:
- **Turtles**: `count turtles`, `count turtles with [carrying-food?]`, `mean [chemical] of turtles`
- **Patches**: `count patches with [food > 0]`, `mean [chemical] of patches`, `count patches with [pheromone > 0]`
- **Global state**: `ticks` (current simulation tick)

Example report queries from `run_complete_experiment.py`:
```python
ants_food = self.netlogo.report('count turtles with [carrying-food?]')
chemical = self.netlogo.report('mean [chemical] of patches')
food_patches = self.netlogo.report('count patches with [food > 0]')
```

## Experiment Output Formats

### Per-Trial JSON Structure
```json
{
  "colony": 1,
  "trial": 1,
  "ticks": [0, 10, 20, 30],
  "ants_foraging": [50, 48, 52, 49],
  "ants_returning": [30, 32, 28, 31],
  "chemical": [0.5, 0.6, 0.55, 0.58]
}
```

### Summary CSV Format
Aggregate across trials:
```
colony,trial,metric,mean,std,max,min
1,1,ants_foraging,50.2,1.5,52,48
1,1,chemical,0.57,0.04,0.6,0.5
1,2,ants_foraging,51.0,1.2,53,49
```

Files saved with timestamps: `experiment_1_results/colony{id}_trial{id}.json` and `summary_all_trials.csv`

## Common Patterns & Examples

### Multi-Trial Loop with Error Handling
```python
for trial in range(self.num_trials):
    for colony in range(self.num_colonies):
        try:
            data = self.run_single_trial(colony, trial)
            results.append(data)
        except Exception as e:
            print(f"Trial {trial}, Colony {colony} failed: {e}")
            continue
```

### Batch Ticks for Efficiency
```python
# Good: batch 10 ticks in one command
self.netlogo.command('repeat 10 [go]')

# Avoid: calling go individually (10x slower)
for _ in range(10):
    self.netlogo.command('go')
```

### Safe Report Wrapping
```python
try:
    value = self.netlogo.report('count patches with [food > 0]')
except Exception:
    # Fallback: query may fail in mock or edge cases
    value = 0
```

### Cleanup Pattern
```python
try:
    self.netlogo = netlogo_utils.init_netlogo(gui=False)
    self.netlogo.load_model(self.model_path)
    # ... experiment logic ...
finally:
    if self.netlogo:
        try:
            self.netlogo.kill_workspace()
        except Exception:
            pass
```

## Debugging & Troubleshooting

### Test Mock Implementation
```bash
python3 run_experiment_1.py  # Automatically uses MockNetLogoLink if NetLogo unavailable
```

### Verify NetLogo Environment
```bash
export NETLOGO_HOME=/opt/netlogo-7.0.2
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
python3 -c "import netlogo_utils; print(netlogo_utils.find_netlogo_home())"
```

### Check Dependencies
```bash
flake8 . --max-line-length=120  # Lint all Python files
pip list | grep -E "pyNetLogo|pandas|seaborn"  # Verify key packages
```

## CI/Testing Strategy

When adding new experiments:
1. **Start with mock** (`init_netlogo()` auto-detects; no setup needed)
2. **Test locally** with reduced trials/duration (e.g., 2 trials, 100 ticks)
3. **CI should use mock** (no NetLogo/Java in typical CI environments)
4. **Real validation** runs locally or in dev environment with NetLogo installed

Smoke test entry point: `run_experiment_1.py` (works with or without NetLogo)
