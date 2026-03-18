# FormicaBot Simulations - API Reference

## Core Modules

### `netlogo_utils.py`

Main module for NetLogo bridge and mock implementation.

#### Functions

##### `find_netlogo_home(env_var: str = 'NETLOGO_HOME') -> Optional[str]`

Search for NetLogo installation directory.

**Parameters:**
- `env_var` (str): Environment variable to check first (default: 'NETLOGO_HOME')

**Returns:**
- Path to NetLogo home directory or None if not found

**Priority:**
1. `NETLOGO_HOME` environment variable
2. `/opt/netlogo-7.0.2`
3. `/opt/netlogo`
4. `/usr/local/netlogo`
5. `~/NetLogo`
6. `~/netlogo`

**Example:**
```python
home = netlogo_utils.find_netlogo_home()
if home:
    print(f"Found NetLogo at: {home}")
```

---

##### `java_available() -> bool`

Check if Java is available on system PATH.

**Returns:**
- True if java command is available, False otherwise

**Example:**
```python
if not netlogo_utils.java_available():
    print("Java not found - mock mode will be used")
```

---

##### `find_netlogo_jar(netlogo_home: Optional[str]) -> Optional[str]`

Search for NetLogo JAR file in installation directory.

**Parameters:**
- `netlogo_home` (str): Path to NetLogo installation

**Returns:**
- Path to JAR file or None

**Searches:**
- `{netlogo_home}/app/*.jar`
- `{netlogo_home}/lib/*.jar`
- `{netlogo_home}/lib/app/*.jar`
- `{netlogo_home}/*.jar`

---

##### `init_netlogo(gui: bool = False, netlogo_home: Optional[str] = None, netlogo_version: Optional[str] = None) -> Union[pynetlogo.NetLogoLink, MockNetLogoLink]`

Initialize NetLogo connection with automatic fallback to mock.

**Parameters:**
- `gui` (bool): Enable GUI mode (default: False for headless)
- `netlogo_home` (str): NetLogo installation path (auto-detected if None)
- `netlogo_version` (str): NetLogo version (optional, rarely used)

**Returns:**
- Real `pynetlogo.NetLogoLink` if available, else `MockNetLogoLink`

**Raises:**
- RuntimeError if PyNetLogo import fails

**Example:**
```python
import netlogo_utils

# Get NetLogo connection (real or mock)
netlogo = netlogo_utils.init_netlogo(gui=False)

try:
    netlogo.load_model("final_ants.nlogo")
    netlogo.command("setup")
    count = netlogo.report("count turtles")
    print(f"Ants: {count}")
finally:
    netlogo.kill_workspace()
```

---

#### Classes

##### `MockNetLogoLink`

Synthetic NetLogo simulator for testing without Java/NetLogo installed.

**Attributes:**
- `ticks` (int): Current simulation tick
- `turtles` (int): Number of turtles (ants)
- `patches` (int): Number of patches
- `model` (str): Loaded model path
- `state` (dict): Internal state tracking

**Methods:**

###### `__init__(gui: bool = False, netlogo_home: Optional[str] = None) -> None`

Initialize mock with seeded random generator (seed=0 for determinism).

---

###### `load_model(model_path: str) -> None`

Load a NetLogo model file (stores path, prints confirmation).

**Parameters:**
- `model_path` (str): Path to .nlogo file

**Example:**
```python
mock = MockNetLogoLink()
mock.load_model("final_ants.nlogo")
```

---

###### `command(cmd: str) -> None`

Execute a NetLogo command.

**Supported Commands:**
- `setup`: Initialize simulation (resets ticks to 0)
- `go`: Advance by one tick
- `repeat N [go]`: Advance by N ticks
- `set variable value`: Set variable (parsed, value stored in state)

**Example:**
```python
mock.command("setup")
mock.command("repeat 10 [go]")
```

---

###### `report(expr: str) -> Union[int, float]`

Query simulation state and return result.

**Supported Queries:**
- `count turtles`: Total turtle count
- `count turtles with [carrying-food?]`: Ants carrying food
- `count patches with [food > 0]`: Food patches
- `count patches with [pheromone > 0]`: Pheromone patches
- `mean [chemical] of patches`: Average chemical
- `mean [pheromone] of patches`: Average pheromone

**Returns:**
- int or float depending on query

**Example:**
```python
ants = mock.report("count turtles")
food = mock.report("count patches with [food > 0]")
chemical = mock.report("mean [chemical] of patches")
print(f"Ants: {ants}, Food: {food}, Chemical: {chemical}")
```

---

###### `repeat_report(reports: List[str], times: int) -> List[Any]`

Execute multiple reports over multiple ticks.

**Parameters:**
- `reports` (list): List of report queries
- `times` (int): Number of times to repeat

**Returns:**
- List of results for each tick

**Example:**
```python
results = mock.repeat_report(
    ["count turtles", "mean [chemical] of patches"],
    times=10
)
# results = [[100, 0.5], [100, 0.52], ..., [100, 0.48]]
```

---

###### `kill_workspace() -> None`

Clean up NetLogo connection (prints confirmation in mock).

---

### `experiment_base.py`

Base class for experiment runners.

#### Classes

##### `ExperimentRunner(ABC)`

Abstract base class for experiment implementations.

**Constructor Parameters:**
- `num_trials` (int): Number of trials per colony (default: 2)
- `num_colonies` (int): Number of colonies (default: 2)
- `trial_duration` (int): Ticks per trial (default: 600)
- `measurement_interval` (int): Ticks between measurements (default: 10)

**Attributes:**
- `netlogo`: NetLogo connection object
- `output_dir`: Results directory
- `results`: List of trial data dictionaries
- `start_time`: Experiment start timestamp

**Abstract Methods** (must implement in subclass):

###### `get_output_directory() -> str`

Return name of output directory.

###### `get_model_path() -> str`

Return path to NetLogo model file.

###### `run_single_trial(colony_id: int, trial_id: int) -> Dict[str, Any]`

Run one trial and return data dictionary.

**Concrete Methods:**

###### `initialize_netlogo(gui: bool = False) -> bool`

Initialize NetLogo connection and load model.

**Returns:**
- True if successful, False otherwise

---

###### `run_all_trials() -> bool`

Run all trials with error handling and progress reporting.

**Returns:**
- True if all succeeded, False if any failed

---

###### `save_results() -> None`

Save results to JSON (per-trial) and CSV (summary).

---

###### `run() -> bool`

Execute full pipeline: initialize → run all → save → report.

**Returns:**
- True if successful

---

###### `get_elapsed_time() -> float`

Get elapsed time in seconds since start.

---

###### `print_summary() -> None`

Print experiment completion summary to console.

---

**Example Subclass:**

```python
from experiment_base import ExperimentRunner

class MyExperiment(ExperimentRunner):
    def get_output_directory(self) -> str:
        return "my_results"
    
    def get_model_path(self) -> str:
        return "final_ants.nlogo"
    
    def run_single_trial(self, colony_id: int, trial_id: int) -> dict:
        self.netlogo.command("setup")
        data = {
            "colony": colony_id,
            "trial": trial_id,
            "ticks": [],
            "ants": [],
        }
        
        for tick in range(0, self.trial_duration, self.measurement_interval):
            self.netlogo.command(f"repeat {self.measurement_interval} [go]")
            ants = self.netlogo.report("count turtles")
            data["ticks"].append(tick)
            data["ants"].append(ants)
        
        return data

# Run it
exp = MyExperiment(num_trials=3, num_colonies=2)
exp.run()
```

---

### `cli_experiment.py`

Command-line interface for running experiments.

#### Classes

##### `CLIExperiment(ExperimentRunner)`

CLI-driven experiment runner with configurable parameters.

#### Main Entry Point

##### `cli_experiment.py --help`

**Usage:**
```bash
python3 cli_experiment.py MODEL [-o OUTPUT] [-t TRIALS] [-c COLONIES] 
                                [-d DURATION] [-i INTERVAL] [--gui]
```

**Arguments:**
- `MODEL`: Path to .nlogo file (required)
- `-o, --output`: Output directory (default: cli_experiment_results)
- `-t, --trials`: Number of trials per colony (default: 2)
- `-c, --colonies`: Number of colonies (default: 2)
- `-d, --duration`: Trial duration in ticks (default: 600)
- `-i, --interval`: Measurement interval (default: 10)
- `--gui`: Enable NetLogo GUI

**Examples:**
```bash
# Run with defaults
python3 cli_experiment.py final_ants.nlogo

# Custom parameters
python3 cli_experiment.py final_ants.nlogo -t 5 -c 3 -d 1000 -i 20

# Custom output
python3 cli_experiment.py final_ants.nlogo -o my_results
```

---

## Data Formats

### Trial JSON Format

```json
{
  "colony": 1,
  "trial": 1,
  "ticks": [0, 10, 20, 30],
  "ants_foraging": [50, 48, 52, 49],
  "ants_returning": [30, 32, 28, 31],
  "chemical": [0.5, 0.6, 0.55, 0.58],
  "food_patches": [45, 44, 42, 40]
}
```

### Summary CSV Format

```csv
colony,trial,metric,mean,std,min,max
1,1,ants_foraging,50.2,1.5,48,52
1,1,ants_returning,30.2,1.5,28,32
1,1,chemical,0.57,0.04,0.5,0.6
1,1,food_patches,42.8,2.2,40,45
```

---

## Common Workflows

### Basic Experiment

```python
import netlogo_utils

netlogo = netlogo_utils.init_netlogo()
netlogo.load_model("final_ants.nlogo")
netlogo.command("setup")

for tick in range(100):
    netlogo.command("go")
    if tick % 10 == 0:
        count = netlogo.report("count turtles")
        print(f"Tick {tick}: {count} turtles")

netlogo.kill_workspace()
```

### Run from CLI

```bash
python3 cli_experiment.py final_ants.nlogo -t 3 -c 2 -d 500
```

### Extend ExperimentRunner

```python
from experiment_base import ExperimentRunner

class CustomExperiment(ExperimentRunner):
    # Implement abstract methods
    # Call exp.run() to execute
```

---

## Error Handling

### Missing NetLogo

Automatically uses `MockNetLogoLink`:

```python
netlogo = netlogo_utils.init_netlogo()  # Real or mock
```

### Failed Queries

Handle failures gracefully:

```python
try:
    value = netlogo.report("count patches with [food > 0]")
except Exception as e:
    print(f"Query failed: {e}")
    value = 0
```

### Trial Failures

`ExperimentRunner.run_all_trials()` continues on error:

```python
success = exp.run_all_trials()
if not success:
    print("Some trials failed (see output above)")
```

---

## Best Practices

1. **Always clean up**: Call `netlogo.kill_workspace()` in finally block
2. **Batch commands**: Use `repeat N [go]` instead of loop
3. **Handle report errors**: Wrap queries in try-except
4. **Use base class**: Extend `ExperimentRunner` for consistency
5. **Test with mock**: Always test with `MockNetLogoLink` first
6. **Use CLI**: Leverage `cli_experiment.py` for flexible runs

---

## See Also

- [README.md](README.md) - Quick start guide
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development setup
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - AI agent guidance
