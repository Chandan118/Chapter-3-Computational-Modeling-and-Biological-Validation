#!/usr/bin/env python3
"""
FormicaBot Baseline Foraging Experiments
Complete working version with all error handling
"""

import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd

import netlogo_utils

# Configuration
NETLOGO_HOME = os.environ.get("NETLOGO_HOME", "/home/chandan/netlogo/netlogo-7.0.2")
MODEL_FILE = "final_ants.nlogo"


class FormicaBotExperiment:
    """Complete ant foraging experiment system"""

    def __init__(self):
        self.netlogo_home = NETLOGO_HOME
        self.model_path = MODEL_FILE
        self.output_dir = Path("formicabot_results")
        self.output_dir.mkdir(exist_ok=True)

        # Experiment parameters
        self.num_trials = 3
        self.num_colonies = 2
        self.trial_duration = 500
        self.measure_interval = 10

        self.netlogo = None

    def test_setup(self):
        """Verify everything is ready"""
        print("\n" + "=" * 70)
        print("VERIFYING SETUP")
        print("=" * 70)

        # Check model exists
        if not os.path.exists(self.model_path):
            print(f"✗ Model not found: {self.model_path}")
            return False
        print(f"✓ Model found: {self.model_path}")

        # Test NetLogo
        try:
            print("  Testing NetLogo connection...")
            self.netlogo = netlogo_utils.init_netlogo(gui=False, netlogo_home=self.netlogo_home)
            self.netlogo.load_model(self.model_path)
            self.netlogo.command("setup")
            count = self.netlogo.report("count turtles")
            self.netlogo.kill_workspace()
            print(f"✓ NetLogo works ({count} ants created)")
            return True
        except Exception as e:
            print(f"✗ NetLogo test failed: {e}")
            return False

    def run_trial(self, colony_id, trial_id):
        """Run a single trial"""
        print(f"\n▶ Colony {colony_id}, Trial {trial_id}")

        # Setup
        self.netlogo.command("setup")

        # Colony-specific parameters
        diffusion = 50 + colony_id * 5
        evaporation = 10 + colony_id * 2

        try:
            self.netlogo.command(f"set diffusion-rate {diffusion}")
            self.netlogo.command(f"set evaporation-rate {evaporation}")
        except Exception:
            pass  # Some models may not have these parameters

        # Data collection
        data = {"colony": colony_id, "trial": trial_id, "ticks": [], "ants_with_food": [], "chemical_level": []}

        # Run simulation
        start = time.time()
        for tick in range(0, self.trial_duration, self.measure_interval):
            self.netlogo.command(f"repeat {self.measure_interval} [go]")

            try:
                # Try to get ants carrying food
                ants_food = self.netlogo.report("count turtles with [color = orange + 1]")
            except Exception:
                try:
                    ants_food = self.netlogo.report("count turtles with [carrying-food?]")
                except Exception:
                    ants_food = 0

            try:
                chemical = self.netlogo.report("mean [chemical] of patches")
            except Exception:
                chemical = 0

            data["ticks"].append(tick)
            data["ants_with_food"].append(int(ants_food))
            data["chemical_level"].append(float(chemical))

            if tick % 100 == 0:
                elapsed = time.time() - start
                print(f"  Tick {tick}: {ants_food} ants foraging ({elapsed:.1f}s)")

        # Save
        filename = self.output_dir / f"colony{colony_id}_trial{trial_id}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        return data

    def run_all(self):
        """Run all experiments"""
        print("\n" + "=" * 70)
        print("FORMICABOT BASELINE FORAGING EXPERIMENTS")
        print("=" * 70)
        print(f"Colonies: {self.num_colonies}")
        print(f"Trials per colony: {self.num_trials}")
        print(f"Duration: {self.trial_duration} ticks")
        print("=" * 70)

        # Test first
        if not self.test_setup():
            print("\n✗ Setup failed. Please fix errors above.")
            return

        results = []

        try:
            # Initialize
            print("\nInitializing NetLogo...")
            self.netlogo = netlogo_utils.init_netlogo(gui=False, netlogo_home=self.netlogo_home)
            self.netlogo.load_model(self.model_path)
            print("✓ Ready\n")

            # Run experiments
            for colony in range(1, self.num_colonies + 1):
                print(f"\n{'═'*70}")
                print(f"COLONY {colony}")
                print(f"{('═'*70)}")

                for trial in range(1, self.num_trials + 1):
                    data = self.run_trial(colony, trial)
                    results.append(data)

            # Generate summary
            self.create_summary(results)

            print("\n" + "=" * 70)
            print("✓ EXPERIMENTS COMPLETE")
            print(f"  Results: {self.output_dir}/")
            print("=" * 70 + "\n")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            if self.netlogo:
                try:
                    self.netlogo.kill_workspace()
                except Exception:
                    pass

    def create_summary(self, results):
        """Generate summary"""
        print("\nCreating summary...")

        # Summary statistics
        summary = []
        for data in results:
            summary.append(
                {
                    "colony": data["colony"],
                    "trial": data["trial"],
                    "max_foraging": max(data["ants_with_food"]),
                    "avg_chemical": np.mean(data["chemical_level"]),
                    "total_food_collected": sum(data["ants_with_food"]),
                }
            )

        df = pd.DataFrame(summary)
        df.to_csv(self.output_dir / "summary.csv", index=False)
        print("✓ Saved: summary.csv")

        print("\nResults:")
        print(df.to_string())

        # Create plots
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(2, 2, figsize=(12, 10))

            # Plot 1: Foraging activity over time
            ax = axes[0, 0]
            for data in results:
                label = f"C{data['colony']}-T{data['trial']}"
                ax.plot(data["ticks"], data["ants_with_food"], label=label, alpha=0.7)
            ax.set_xlabel("Time (ticks)")
            ax.set_ylabel("Ants Foraging")
            ax.set_title("Foraging Activity Over Time")
            ax.legend()
            ax.grid(True, alpha=0.3)

            # Plot 2: Chemical trails
            ax = axes[0, 1]
            for data in results:
                label = f"C{data['colony']}-T{data['trial']}"
                ax.plot(data["ticks"], data["chemical_level"], label=label, alpha=0.7)
            ax.set_xlabel("Time (ticks)")
            ax.set_ylabel("Chemical Level")
            ax.set_title("Pheromone Trail Strength")
            ax.legend()
            ax.grid(True, alpha=0.3)

            # Plot 3: Max foraging by colony
            ax = axes[1, 0]
            colony_data = df.groupby("colony")["max_foraging"].mean()
            ax.bar(colony_data.index, colony_data.values, color="skyblue", edgecolor="black")
            ax.set_xlabel("Colony")
            ax.set_ylabel("Avg Max Foraging Ants")
            ax.set_title("Foraging Efficiency by Colony")
            ax.grid(True, alpha=0.3)

            # Plot 4: Total food collected
            ax = axes[1, 1]
            ax.bar(
                df["colony"].astype(str) + "-" + df["trial"].astype(str),
                df["total_food_collected"],
                color="lightgreen",
                edgecolor="black",
            )
            ax.set_xlabel("Colony-Trial")
            ax.set_ylabel("Total Food Collected")
            ax.set_title("Food Collection by Trial")
            ax.tick_params(axis="x", rotation=45)
            ax.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(self.output_dir / "experiment_results.png", dpi=150)
            print("✓ Saved: experiment_results.png")
            plt.close()

        except Exception as e:
            print(f"⚠ Plot creation warning: {e}")


if __name__ == "__main__":
    exp = FormicaBotExperiment()
    exp.run_all()
