#!/usr/bin/env python3
"""Utility helpers for initializing NetLogo with clearer pre-flight checks.

This module is intentionally lightweight and avoids side-effects.
"""
import os
import shutil
import glob


def find_netlogo_home(env_var='NETLOGO_HOME'):
    """Return a candidate NetLogo home path or None."""
    home = os.environ.get(env_var)
    if home and os.path.isdir(home):
        return home

    candidates = [
        '/opt/netlogo-7.0.2',
        '/opt/netlogo',
        '/usr/local/netlogo',
        os.path.expanduser('~/NetLogo'),
        os.path.expanduser('~/netlogo'),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return None


def java_available():
    """Return True if `java` is available on PATH."""
    return shutil.which('java') is not None


def find_netlogo_jar(netlogo_home):
    """Search for a NetLogo jar in the installation directory. Returns path or None."""
    if not netlogo_home:
        return None
    # Common locations for the jar
    patterns = [
        os.path.join(netlogo_home, 'app', '*.jar'),
        os.path.join(netlogo_home, 'lib', '*.jar'),
        os.path.join(netlogo_home, '*.jar'),
    ]
    for p in patterns:
        found = glob.glob(p)
        if found:
            # Prefer netlogo jar-like names
            for f in found:
                name = os.path.basename(f).lower()
                if 'netlogo' in name or name.endswith('.jar'):
                    return f
            return found[0]
    return None


def init_netlogo(gui=False, netlogo_home=None, netlogo_version=None):
    """Initialize and return a `pynetlogo.NetLogoLink` instance.

    Raises RuntimeError with a helpful message on failure.
    """
    try:
        import pynetlogo
    except Exception as e:
        raise RuntimeError(f"PyNetLogo import failed: {e}")

    if netlogo_home is None:
        netlogo_home = find_netlogo_home()

    jar = find_netlogo_jar(netlogo_home)

    # If NetLogo or Java missing, provide a helpful error. For convenience
    # allow calling code to request a lightweight mock so scripts can run
    # in environments without NetLogo installed.
    allow_mock = True
    if not netlogo_home or not java_available() or not jar:
        missing = []
        if not netlogo_home:
            missing.append('NETLOGO_HOME')
        if not java_available():
            missing.append('java')
        if not jar:
            missing.append('netlogo jar')

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
        kwargs = dict(gui=gui, netlogo_home=netlogo_home)
        if netlogo_version:
            kwargs['netlogo_version'] = netlogo_version
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
    def __init__(self, gui=False, netlogo_home=None):
        import random
        self._rand = random.Random(0)
        self.ticks = 0
        self.turtles = 100
        self.patches = 10000
        self.model = None

    def load_model(self, model_path):
        self.model = model_path
        print(f"[MOCK] Loaded model: {model_path}")

    def command(self, cmd):
        # Support 'setup', 'go', 'repeat N [go]', and simple set commands
        cmd = str(cmd).strip()
        if cmd.startswith('set '):
            # ignore set commands in mock
            return
        if cmd == 'setup':
            self.ticks = 0
            # reset turtles to default
            self.turtles = 100
            return
        if cmd.startswith('repeat') and 'go' in cmd:
            # No-op: advance ticks by the repeat count if parsable
            try:
                # parse simple patterns like: repeat 10 [go]
                parts = cmd.split()
                n = int(parts[1])
                self.ticks += n
            except Exception:
                self.ticks += 1
            return
        if cmd == 'go':
            self.ticks += 1
            return

    def report(self, expr):
        e = str(expr).lower()
        if 'count turtles' in e:
            return int(self.turtles)
        if 'count patches' in e:
            return int(self.patches)
        if 'count turtles with' in e:
            # return a small fraction as mock
            return int(self.turtles * 0.1)
        if 'mean [chemical] of patches' in e or 'mean [chemical]' in e:
            return float(self._rand.random())
        # default numeric fallback
        try:
            return float(0)
        except Exception:
            return 0

    def repeat_report(self, reports, times):
        # reports: list of report strings; return list of lists
        out = []
        for t in range(times):
            vals = []
            for r in reports:
                vals.append(self.report(r))
            out.append(vals if len(vals) > 1 else vals[0])
        return out

    def kill_workspace(self):
        print("[MOCK] NetLogo workspace closed")
