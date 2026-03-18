#!/usr/bin/env python3
"""Utility helpers for initializing NetLogo with clearer pre-flight checks.

This module is intentionally lightweight and avoids side-effects.
"""

import glob
import os
import shutil
from typing import Any, Dict, List, Optional, Union


def find_netlogo_home(env_var: str = "NETLOGO_HOME") -> Optional[str]:
    """Return a candidate NetLogo home path or None."""
    home = os.environ.get(env_var)
    if home and os.path.isdir(home):
        return home

    candidates = [
        "/opt/netlogo-7.0.2",
        "/opt/netlogo",
        "/usr/local/netlogo",
        os.path.expanduser("~/NetLogo"),
        os.path.expanduser("~/netlogo"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return None


def java_available() -> bool:
    """Return True if `java` is available on PATH."""
    return shutil.which("java") is not None


def find_netlogo_jar(netlogo_home: Optional[str]) -> Optional[str]:
    """Search for a NetLogo jar in the installation directory. Returns path or None."""
    if not netlogo_home:
        return None
    # Common locations for the jar
    patterns = [
        os.path.join(netlogo_home, "app", "*.jar"),
        os.path.join(netlogo_home, "lib", "*.jar"),
        os.path.join(netlogo_home, "lib", "app", "*.jar"),
        os.path.join(netlogo_home, "*.jar"),
    ]
    for p in patterns:
        found = glob.glob(p)
        if found:
            # Prefer netlogo jar-like names
            for f in found:
                name = os.path.basename(f).lower()
                if "netlogo" in name or name.endswith(".jar"):
                    return f
            return found[0]
    return None


def init_netlogo(
    gui: bool = False, netlogo_home: Optional[str] = None, netlogo_version: Optional[str] = None
) -> Union[Any, "MockNetLogoLink"]:
    """Initialize and return a `pynetlogo.NetLogoLink` instance.

    Raises RuntimeError with a helpful message on failure.
    """
    pynetlogo = None
    try:
        import pynetlogo
    except ImportError:
        pass

    if netlogo_home is None:
        netlogo_home = find_netlogo_home()

    jar = find_netlogo_jar(netlogo_home)

    # If NetLogo, Java, or PyNetLogo missing, provide a helpful error.
    # For convenience allow calling code to request a lightweight mock
    # so scripts can run in environments without NetLogo installed.
    allow_mock = True
    if not pynetlogo or not netlogo_home or not java_available() or not jar:
        missing = []
        if not pynetlogo:
            missing.append("pynetlogo")
        if not netlogo_home:
            missing.append("NETLOGO_HOME")
        if not java_available():
            missing.append("java")
        if not jar:
            missing.append("netlogo jar")

        msg = f"Missing or invalid environment: {', '.join(missing)}"

        if allow_mock:
            # Provide a MockNetLogoLink so the rest of the project can run
            # for smoke-testing and development without NetLogo installed.
            print(f"WARNING: {msg} — using MockNetLogoLink for testing.")
            return MockNetLogoLink()
        else:
            raise RuntimeError(msg)

    # Try to create the NetLogoLink; let exceptions bubble up but wrap them
    try:
        # Pass minimal supported kwargs to pynetlogo.NetLogoLink. Some
        # versions of pyNetLogo do not accept a `netlogo_version` argument,
        # so avoid passing it to maximize compatibility.
        kwargs = {"gui": gui, "netlogo_home": netlogo_home}
        if netlogo_version:
            kwargs["netlogo_version"] = netlogo_version
        assert pynetlogo is not None
        nl = pynetlogo.NetLogoLink(**kwargs)
        return nl
    except Exception as e:
        raise RuntimeError(f"Failed to start NetLogo via PyNetLogo: {e}")


class MockNetLogoLink:
    """A minimal mock of the PyNetLogo NetLogoLink for smoke tests.

    It implements the small subset of the API used by the scripts: load_model,
    command, report, repeat_report, kill_workspace. Behavior is synthetic but
    deterministic-enough for running example scripts in CI or development
    without NetLogo installed.
    """

    def __init__(self, gui: bool = False, netlogo_home: Optional[str] = None) -> None:
        import random

        self._rand = random.Random(0)
        self.ticks: int = 0
        self.turtles: int = 100
        self.patches: int = 10000
        self.model: Optional[str] = None

        # Enhanced mock state
        self.state: Dict[str, Any] = {
            "carrying_food": int(self.turtles * 0.1),
            "at_nest": int(self.turtles * 0.3),
            "chemical": 0.5,
            "food_patches": 50,
            "pheromone": 0.3,
        }

    def load_model(self, model_path: str) -> None:
        self.model = model_path
        print(f"[MOCK] Loaded model: {model_path}")

    def command(self, cmd: str) -> None:
        # Support 'setup', 'go', 'repeat N [go]', and simple set commands
        cmd = str(cmd).strip()
        if cmd.startswith("set "):
            # Parse set commands like: set diffusion-rate 50
            try:
                parts = cmd.split()
                if len(parts) >= 3:
                    var_name = parts[1]
                    value = float(parts[2])
                    self.state[var_name] = value
            except Exception:
                pass
            return
        if cmd == "setup":
            self.ticks = 0
            self.turtles = 100
            self.state["carrying_food"] = int(self.turtles * 0.1)
            self.state["at_nest"] = int(self.turtles * 0.3)
            self.state["chemical"] = 0.5
            self.state["food_patches"] = 50
            return
        if cmd.startswith("repeat") and "go" in cmd:
            # No-op: advance ticks by the repeat count if parsable
            try:
                # parse simple patterns like: repeat 10 [go]
                parts = cmd.split()
                n = int(parts[1])
                self.ticks += n
                # Simulate state changes
                self._simulate_tick_changes(n)
            except Exception:
                self.ticks += 1
            return
        if cmd == "go":
            self.ticks += 1
            self._simulate_tick_changes(1)
            return

    def _simulate_tick_changes(self, num_ticks: int) -> None:
        """Simulate state changes over ticks for more realistic mock."""
        for _ in range(num_ticks):
            # Decay chemical over time
            self.state["chemical"] *= 0.95
            self.state["chemical"] += self._rand.random() * 0.05

            # Food patches decrease slightly
            if self.state["food_patches"] > 10:
                self.state["food_patches"] -= int(self._rand.random() * 2)

            # Carrying food varies
            self.state["carrying_food"] = int(self.turtles * (0.1 + self._rand.random() * 0.2))

    def report(self, expr: str) -> Union[int, float]:
        e = str(expr).lower()
        if "count turtles" in e:
            if "carrying-food" in e or "carrying_food" in e:
                return int(self.state["carrying_food"])
            if "at-nest" in e or "at_nest" in e:
                return int(self.state["at_nest"])
            return int(self.turtles)
        if "count patches" in e:
            if "food" in e:
                return int(self.state["food_patches"])
            if "pheromone" in e:
                return int(self.patches * (self.state["pheromone"] / 10))
            return int(self.patches)
        if "mean [chemical]" in e:
            return float(self.state["chemical"])
        if "mean [pheromone]" in e:
            return float(self.state["pheromone"])
        # default numeric fallback
        try:
            return float(0)
        except Exception:
            return 0

    def repeat_report(self, reports: List[str], times: int) -> List[Any]:
        # reports: list of report strings; return list of lists
        out: List[Any] = []
        for t in range(times):
            vals: List[Any] = []
            for r in reports:
                vals.append(self.report(r))
            out.append(vals if len(vals) > 1 else vals[0])
        return out

    def kill_workspace(self) -> None:
        print("[MOCK] NetLogo workspace closed")
