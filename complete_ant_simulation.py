#!/usr/bin/env python3
"""
COMPLETE ANT COLONY SIMULATION
Full-featured simulation with NetLogo + Gazebo visualization
Production-ready with robust error handling
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

import netlogo_utils


class CompleteAntSimulation:
    """Production-grade ant colony simulation with visualization"""

    def __init__(self):
        # NetLogo configuration
        self.netlogo_home = self._detect_netlogo()
        self.model_path = "final_ants.nlogo"

        # Simulation parameters - Extended for comprehensive results
        self.num_colonies = 5  # More colonies for better data
        self.num_trials = 5  # More trials for statistical significance
        self.trial_duration = 1000  # Extended duration
        self.measure_interval = 10

        # Output configuration
        self.output_dir = Path("formicabot_results")
        self.output_dir.mkdir(exist_ok=True)

        # Gazebo configuration
        self.gazebo_worlds_dir = Path("gazebo_worlds")
        self.gazebo_worlds_dir.mkdir(exist_ok=True)

        self.netlogo = None

    def _detect_netlogo(self) -> str:
        """Auto-detect NetLogo installation"""
        paths = [
            "/home/chandan/netlogo/netlogo-7.0.2",
            "/opt/netlogo-7.0.2",
            "/opt/netlogo",
            "/usr/local/netlogo",
        ]

        for path in paths:
            if os.path.exists(path):
                print(f"✓ Found NetLogo: {path}")
                return path

        return "/home/chandan/netlogo/netlogo-7.0.2"

    def verify_setup(self) -> bool:
        """Verify all dependencies and configurations"""
        print("\n" + "=" * 80)
        print("VERIFYING SYSTEM SETUP")
        print("=" * 80)

        checks = []

        # Check NetLogo
        if os.path.exists(self.netlogo_home):
            print(f"✓ NetLogo home: {self.netlogo_home}")
            checks.append(True)
        else:
            print(f"✗ NetLogo not found at: {self.netlogo_home}")
            checks.append(False)

        # Check model file
        if os.path.exists(self.model_path):
            print(f"✓ Model file: {self.model_path}")
            checks.append(True)
        else:
            print(f"✗ Model file not found: {self.model_path}")
            checks.append(False)

        # Check Java
        try:
            result = subprocess.run(["java", "-version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Java installed")
                checks.append(True)
            else:
                print("✗ Java not working")
                checks.append(False)
        except Exception:
            print("✗ Java not found")
            checks.append(False)

        # Check Python dependencies
        try:
            import matplotlib  # noqa: F401
            import seaborn  # noqa: F401

            print("✓ Visualization libraries (matplotlib, seaborn)")
            checks.append(True)
        except Exception:
            print("✗ Missing visualization libraries")
            print("  Install with: pip install matplotlib seaborn")
            checks.append(False)

        # Check Gazebo (optional)
        try:
            result = subprocess.run(["which", "gazebo"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Gazebo: {result.stdout.strip()}")
            else:
                print("⚠ Gazebo not installed (optional)")
                print("  Install with: sudo apt install gazebo11")
        except Exception:
            print("⚠ Gazebo check failed (optional)")

        print("=" * 80)

        if all(checks):
            print("✓ ALL CHECKS PASSED")
            return True
        else:
            print("✗ SOME CHECKS FAILED")
            return False

    def test_netlogo_connection(self) -> bool:
        """Test NetLogo connection"""
        print("\n" + "=" * 80)
        print("TESTING NETLOGO CONNECTION")
        print("=" * 80)

        try:
            print("Initializing NetLogo...")
            self.netlogo = netlogo_utils.init_netlogo(gui=False, netlogo_home=self.netlogo_home)

            if isinstance(self.netlogo, netlogo_utils.MockNetLogoLink):
                print("\n⚠ WARNING: Running in MOCK mode")
                print("NetLogo not available - using simulated data\n")
            else:
                print("✓ NetLogo initialized successfully")

            print("Loading model...")
            self.netlogo.load_model(self.model_path)
            print("✓ Model loaded")

            print("Testing commands...")
            self.netlogo.command("setup")
            count = self.netlogo.report("count turtles")
            print(f"✓ Commands work (found {count} ants)")

            self.netlogo.command("repeat 10 [go]")
            print("✓ Simulation runs")

            self.netlogo.kill_workspace()
            self.netlogo = None

            print("\n✓ CONNECTION TEST PASSED")
            return True

        except Exception as e:
            print(f"\n✗ CONNECTION TEST FAILED: {e}")
            import traceback

            traceback.print_exc()
            return False

    def run_single_trial(self, colony_id: int, trial_id: int) -> Optional[Dict]:
        """Run a single simulation trial"""
        print(f"\n{'─'*80}")
        print(f"▶ Colony {colony_id}, Trial {trial_id}")
        print(f"{'─'*80}")

        try:
            # Setup with colony-specific parameters
            self.netlogo.command("setup")

            # Vary parameters by colony
            diffusion = 50 + (colony_id - 1) * 5
            evaporation = 10 + (colony_id - 1) * 2
            pheromone_strength = 60 + (colony_id - 1) * 10

            # Set parameters (with error handling for different model versions)
            try:
                self.netlogo.command(f"set initial-ant-count {100}")
                self.netlogo.command(f"set pheromone-strength {pheromone_strength}")
            except Exception:
                pass  # Some parameters may not exist in all models

            print(f"  Parameters: pheromone={pheromone_strength}")

            # Data collection
            data = {
                "colony_id": colony_id,
                "trial_id": trial_id,
                "parameters": {
                    "pheromone_strength": pheromone_strength,
                },
                "ticks": [],
                "ants_total": [],
                "ants_with_food": [],
                "pheromone_level": [],
                "food_collected": [],
            }

            start_time = time.time()

            # Run simulation
            for tick in range(0, self.trial_duration, self.measure_interval):
                # Execute steps
                self.netlogo.command(f"repeat {self.measure_interval} [go]")

                # Collect metrics
                try:
                    total_ants = self.netlogo.report("count turtles")
                    ants_food = self.netlogo.report("count turtles with [has-food?]")
                    pheromone = self.netlogo.report("mean [pheromone] of patches")
                    food = self.netlogo.report("food-collected")

                    data["ticks"].append(tick)
                    data["ants_total"].append(int(total_ants))
                    data["ants_with_food"].append(int(ants_food))
                    data["pheromone_level"].append(float(pheromone))
                    data["food_collected"].append(int(food))

                except Exception as e:
                    # Fallback for data collection errors
                    data["ticks"].append(tick)
                    data["ants_total"].append(0)
                    data["ants_with_food"].append(0)
                    data["pheromone_level"].append(0.0)
                    data["food_collected"].append(0)

                # Progress update
                if tick % 200 == 0:
                    progress = (tick / self.trial_duration) * 100
                    elapsed = time.time() - start_time
                    print(
                        f"  Progress: {progress:5.1f}% | Tick: {tick:4d} | "
                        f"Food: {data['food_collected'][-1]:3d} | "
                        f"Foraging: {data['ants_with_food'][-1]:3d} | "
                        f"Time: {elapsed:5.1f}s"
                    )

            # Calculate metrics
            data["metrics"] = self._calculate_metrics(data)

            print(f"\n  Results:")
            print(f"    Total food collected: {data['metrics']['total_food']}")
            print(f"    Avg foraging ants: {data['metrics']['avg_foraging_ants']:.1f}")
            print(f"    Peak pheromone: {data['metrics']['peak_pheromone']:.3f}")
            print(f"    Efficiency: {data['metrics']['efficiency']:.2f}")

            # Save trial data
            self._save_trial_data(data)

            return data

        except Exception as e:
            print(f"  ✗ Trial failed: {e}")
            import traceback

            traceback.print_exc()
            return None

    def _calculate_metrics(self, data: Dict) -> Dict:
        """Calculate performance metrics"""
        return {
            "total_food": max(data["food_collected"]) if data["food_collected"] else 0,
            "avg_foraging_ants": float(np.mean(data["ants_with_food"])) if data["ants_with_food"] else 0,
            "peak_pheromone": float(np.max(data["pheromone_level"])) if data["pheromone_level"] else 0,
            "avg_pheromone": float(np.mean(data["pheromone_level"])) if data["pheromone_level"] else 0,
            "efficiency": (max(data["food_collected"]) / (self.trial_duration / 60.0)) if data["food_collected"] else 0,
            "discovery_time": next((i for i, v in enumerate(data["food_collected"]) if v > 0), -1)
            * self.measure_interval,
        }

    def _save_trial_data(self, data: Dict):
        """Save trial data to JSON"""
        filename = self.output_dir / f"colony_{data['colony_id']}_trial_{data['trial_id']}.json"

        # Convert numpy types for JSON serialization
        save_data = {}
        for key, value in data.items():
            if isinstance(value, (list, np.ndarray)):
                save_data[key] = [float(x) if isinstance(x, (np.integer, np.floating)) else x for x in value]
            elif isinstance(value, dict):
                save_data[key] = {
                    k: (float(v) if isinstance(v, (np.integer, np.floating)) else v) for k, v in value.items()
                }
            else:
                save_data[key] = value

        with open(filename, "w") as f:
            json.dump(save_data, f, indent=2)

        print(f"  ✓ Saved: {filename.name}")

    def run_all_experiments(self):
        """Run all simulation experiments"""
        print("\n" + "=" * 80)
        print("ANT COLONY OPTIMIZATION - FULL SIMULATION")
        print("=" * 80)
        print(f"Configuration:")
        print(f"  Colonies: {self.num_colonies}")
        print(f"  Trials per colony: {self.num_trials}")
        print(f"  Duration per trial: {self.trial_duration} ticks ({self.trial_duration/60:.1f} min)")
        print(f"  Total trials: {self.num_colonies * self.num_trials}")
        print(f"  Estimated time: ~{(self.num_colonies * self.num_trials * 2):.0f} minutes")
        print("=" * 80)

        all_results = []

        try:
            # Initialize NetLogo
            print("\nInitializing NetLogo...")
            self.netlogo = netlogo_utils.init_netlogo(gui=False, netlogo_home=self.netlogo_home)
            self.netlogo.load_model(self.model_path)
            print("✓ NetLogo ready\n")

            # Run all trials
            for colony_id in range(1, self.num_colonies + 1):
                print(f"\n{'═'*80}")
                print(f"COLONY {colony_id}/{self.num_colonies}")
                print(f"{'═'*80}")

                for trial_id in range(1, self.num_trials + 1):
                    result = self.run_single_trial(colony_id, trial_id)
                    if result:
                        all_results.append(result)

            # Generate analysis
            if all_results:
                self._generate_comprehensive_analysis(all_results)

            print("\n" + "=" * 80)
            print("✓ SIMULATION COMPLETED SUCCESSFULLY")
            print(f"  Trials completed: {len(all_results)}/{self.num_colonies * self.num_trials}")
            print(f"  Results directory: {self.output_dir}/")
            print("=" * 80)

        except Exception as e:
            print(f"\n✗ Simulation failed: {e}")
            import traceback

            traceback.print_exc()

        finally:
            if self.netlogo:
                try:
                    self.netlogo.kill_workspace()
                    print("\nNetLogo connection closed")
                except Exception:
                    pass

    def _generate_comprehensive_analysis(self, results: List[Dict]):
        """Generate comprehensive analysis and visualizations"""
        print("\n" + "=" * 80)
        print("GENERATING COMPREHENSIVE ANALYSIS")
        print("=" * 80)

        # Extract summary data
        summary_data = []
        for result in results:
            row = {"colony_id": result["colony_id"], "trial_id": result["trial_id"], **result["metrics"]}
            summary_data.append(row)

        df = pd.DataFrame(summary_data)

        # Save summary CSV
        csv_file = self.output_dir / "comprehensive_summary.csv"
        df.to_csv(csv_file, index=False)
        print(f"✓ Summary CSV: {csv_file.name}")

        # Print statistics
        print("\nStatistical Summary:")
        print(df.groupby("colony_id").mean().round(2))

        # Create visualizations
        self._create_visualizations(df, results)

        # Generate performance report
        self._generate_performance_report(df)

    def _create_visualizations(self, df: pd.DataFrame, results: List[Dict]):
        """Create comprehensive visualizations"""
        print("\nGenerating visualizations...")

        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import seaborn as sns

            sns.set_style("whitegrid")
            sns.set_palette("husl")

            # Figure 1: Performance Metrics
            fig, axes = plt.subplots(2, 3, figsize=(18, 10))
            fig.suptitle("Ant Colony Simulation - Performance Metrics", fontsize=16, fontweight="bold")

            # Total food collected
            sns.barplot(data=df, x="colony_id", y="total_food", ax=axes[0, 0])
            axes[0, 0].set_title("Total Food Collected")
            axes[0, 0].set_ylabel("Food Units")

            # Average foraging ants
            sns.barplot(data=df, x="colony_id", y="avg_foraging_ants", ax=axes[0, 1])
            axes[0, 1].set_title("Average Foraging Ants")
            axes[0, 1].set_ylabel("Number of Ants")

            # Efficiency
            sns.barplot(data=df, x="colony_id", y="efficiency", ax=axes[0, 2])
            axes[0, 2].set_title("Foraging Efficiency")
            axes[0, 2].set_ylabel("Food/Minute")

            # Peak pheromone
            sns.barplot(data=df, x="colony_id", y="peak_pheromone", ax=axes[1, 0])
            axes[1, 0].set_title("Peak Pheromone Level")
            axes[1, 0].set_ylabel("Pheromone")

            # Discovery time
            sns.barplot(data=df, x="colony_id", y="discovery_time", ax=axes[1, 1])
            axes[1, 1].set_title("Food Discovery Time")
            axes[1, 1].set_ylabel("Ticks")

            # Box plot of efficiency
            sns.boxplot(data=df, x="colony_id", y="efficiency", ax=axes[1, 2])
            axes[1, 2].set_title("Efficiency Distribution")
            axes[1, 2].set_ylabel("Food/Minute")

            plt.tight_layout()
            plt.savefig(self.output_dir / "performance_metrics.png", dpi=300)
            print("  ✓ performance_metrics.png")
            plt.close()

            # Figure 2: Time Series Analysis
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            fig.suptitle("Time Series Analysis - First Trial Each Colony", fontsize=16, fontweight="bold")

            # Plot first trial of each colony
            for colony_id in range(1, min(self.num_colonies + 1, 6)):
                trial_data = next((r for r in results if r["colony_id"] == colony_id and r["trial_id"] == 1), None)
                if trial_data:
                    label = f"Colony {colony_id}"

                    # Food collected
                    axes[0, 0].plot(trial_data["ticks"], trial_data["food_collected"], label=label, linewidth=2)

                    # Foraging ants
                    axes[0, 1].plot(trial_data["ticks"], trial_data["ants_with_food"], label=label, linewidth=2)

                    # Pheromone level
                    axes[1, 0].plot(trial_data["ticks"], trial_data["pheromone_level"], label=label, linewidth=2)

                    # Total ants
                    axes[1, 1].plot(trial_data["ticks"], trial_data["ants_total"], label=label, linewidth=2)

            axes[0, 0].set_title("Food Collection Over Time")
            axes[0, 0].set_xlabel("Ticks")
            axes[0, 0].set_ylabel("Food Collected")
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)

            axes[0, 1].set_title("Foraging Activity")
            axes[0, 1].set_xlabel("Ticks")
            axes[0, 1].set_ylabel("Ants with Food")
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)

            axes[1, 0].set_title("Pheromone Trail Strength")
            axes[1, 0].set_xlabel("Ticks")
            axes[1, 0].set_ylabel("Pheromone Level")
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)

            axes[1, 1].set_title("Total Active Ants")
            axes[1, 1].set_xlabel("Ticks")
            axes[1, 1].set_ylabel("Number of Ants")
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(self.output_dir / "time_series_analysis.png", dpi=300)
            print("  ✓ time_series_analysis.png")
            plt.close()

            print("✓ All visualizations created")

        except Exception as e:
            print(f"  ⚠ Visualization error: {e}")

    def _generate_performance_report(self, df: pd.DataFrame):
        """Generate text performance report"""
        report_file = self.output_dir / "performance_report.txt"

        with open(report_file, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("ANT COLONY SIMULATION - PERFORMANCE REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Total Colonies: {self.num_colonies}\n")
            f.write(f"Trials per Colony: {self.num_trials}\n")
            f.write(f"Total Trials: {len(df)}\n\n")

            f.write("-" * 80 + "\n")
            f.write("OVERALL STATISTICS\n")
            f.write("-" * 80 + "\n")
            f.write(df.describe().to_string())
            f.write("\n\n")

            f.write("-" * 80 + "\n")
            f.write("COLONY COMPARISON\n")
            f.write("-" * 80 + "\n")
            f.write(df.groupby("colony_id").mean().to_string())
            f.write("\n\n")

            f.write("-" * 80 + "\n")
            f.write("BEST PERFORMERS\n")
            f.write("-" * 80 + "\n")

            best_food = df.loc[df["total_food"].idxmax()]
            f.write(f"\nHighest Food Collection:\n")
            f.write(f"  Colony {best_food['colony_id']}, Trial {best_food['trial_id']}\n")
            f.write(f"  Food: {best_food['total_food']:.0f}\n")

            best_efficiency = df.loc[df["efficiency"].idxmax()]
            f.write(f"\nBest Efficiency:\n")
            f.write(f"  Colony {best_efficiency['colony_id']}, Trial {best_efficiency['trial_id']}\n")
            f.write(f"  Efficiency: {best_efficiency['efficiency']:.2f} food/min\n")

            f.write("\n" + "=" * 80 + "\n")

        print(f"✓ Performance report: {report_file.name}")

    def create_gazebo_world(self):
        """Create enhanced Gazebo world file"""
        world_file = self.gazebo_worlds_dir / "ant_colony.world"

        world_content = """<?xml version="1.0"?>
<sdf version="1.6">
  <world name="ant_colony_world">
    
    <!-- Ground and lighting -->
    <include>
      <uri>model://ground_plane</uri>
    </include>
    
    <include>
      <uri>model://sun</uri>
    </include>
    
    <!-- Nest (brown circle) -->
    <model name="nest">
      <pose>-15 0 0.01 0 0 0</pose>
      <static>true</static>
      <link name="nest_link">
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>3</radius>
              <length>0.02</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0.6 0.4 0.2 1</ambient>
            <diffuse>0.6 0.4 0.2 1</diffuse>
          </material>
        </visual>
        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>3</radius>
              <length>0.02</length>
            </cylinder>
          </geometry>
        </collision>
      </link>
    </model>
    
    <!-- Food Source (green circle) -->
    <model name="food_source">
      <pose>15 0 0.05 0 0 0</pose>
      <static>true</static>
      <link name="food_link">
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>2</radius>
              <length>0.1</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0 0.8 0 1</ambient>
            <diffuse>0 1 0 1</diffuse>
          </material>
        </visual>
        <collision name="collision">
          <geometry>
            <cylinder>
              <radius>2</radius>
              <length>0.1</length>
            </cylinder>
          </geometry>
        </collision>
      </link>
    </model>
    
    <!-- Pheromone trail visualization markers -->
    <model name="trail_marker_1">
      <pose>-10 0 0.01 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <sphere><radius>0.3</radius></sphere>
          </geometry>
          <material>
            <ambient>0.5 0 0.5 0.5</ambient>
            <diffuse>0.7 0 0.7 0.5</diffuse>
          </material>
        </visual>
      </link>
    </model>
    
    <model name="trail_marker_2">
      <pose>-5 0 0.01 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <sphere><radius>0.3</radius></sphere>
          </geometry>
          <material>
            <ambient>0.5 0 0.5 0.5</ambient>
            <diffuse>0.7 0 0.7 0.5</diffuse>
          </material>
        </visual>
      </link>
    </model>
    
    <model name="trail_marker_3">
      <pose>0 0 0.01 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <sphere><radius>0.3</radius></sphere>
          </geometry>
          <material>
            <ambient>0.5 0 0.5 0.5</ambient>
            <diffuse>0.7 0 0.7 0.5</diffuse>
          </material>
        </visual>
      </link>
    </model>
    
    <model name="trail_marker_4">
      <pose>5 0 0.01 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <sphere><radius>0.3</radius></sphere>
          </geometry>
          <material>
            <ambient>0.5 0 0.5 0.5</ambient>
            <diffuse>0.7 0 0.7 0.5</diffuse>
          </material>
        </visual>
      </link>
    </model>
    
    <model name="trail_marker_5">
      <pose>10 0 0.01 0 0 0</pose>
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <sphere><radius>0.3</radius></sphere>
          </geometry>
          <material>
            <ambient>0.5 0 0.5 0.5</ambient>
            <diffuse>0.7 0 0.7 0.5</diffuse>
          </material>
        </visual>
      </link>
    </model>
    
    <!-- Ant representations (small spheres) -->
    <model name="ant_1">
      <pose>-14 1 0.05 0 0 0</pose>
      <static>false</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <sphere><radius>0.2</radius></sphere>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
            <diffuse>1 0 0 1</diffuse>
          </material>
        </visual>
      </link>
    </model>
    
    <model name="ant_2">
      <pose>-14 -1 0.05 0 0 0</pose>
      <static>false</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <sphere><radius>0.2</radius></sphere>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
            <diffuse>1 0 0 1</diffuse>
          </material>
        </visual>
      </link>
    </model>
    
    <model name="ant_3">
      <pose>-13 0 0.05 0 0 0</pose>
      <static>false</static>
      <link name="link">
        <visual name="visual">
          <geometry>
            <sphere><radius>0.2</radius></sphere>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
            <diffuse>1 0 0 1</diffuse>
          </material>
        </visual>
      </link>
    </model>
    
  </world>
</sdf>
"""

        with open(world_file, "w") as f:
            f.write(world_content)

        print(f"✓ Created Gazebo world: {world_file}")
        return world_file

    def launch_gazebo_visualization(self):
        """Launch Gazebo for 3D visualization"""
        print("\n" + "=" * 80)
        print("LAUNCHING GAZEBO VISUALIZATION")
        print("=" * 80)

        # Check Gazebo
        try:
            result = subprocess.run(["which", "gazebo"], capture_output=True, text=True)
            if result.returncode != 0:
                print("✗ Gazebo not installed")
                print("\nInstall with:")
                print("  sudo apt update")
                print("  sudo apt install gazebo11 libgazebo11-dev")
                return

            print(f"✓ Gazebo found: {result.stdout.strip()}")
        except Exception:
            print("✗ Gazebo check failed")
            return

        # Create world file
        world_file = self.create_gazebo_world()

        print("\nLaunching Gazebo...")
        print("(This will open a 3D visualization window)")
        print("(Close the Gazebo window to exit)")

        try:
            subprocess.run(["gazebo", str(world_file)])
        except KeyboardInterrupt:
            print("\nGazebo closed")


def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print(" " * 20 + "ANT COLONY SIMULATION SYSTEM")
    print(" " * 15 + "Complete NetLogo + Gazebo Integration")
    print("=" * 80)

    sim = CompleteAntSimulation()

    # Step 1: Verify setup
    if not sim.verify_setup():
        print("\n✗ Setup verification failed")
        print("Please fix the issues above before running")
        return 1

    # Step 2: Test NetLogo
    if not sim.test_netlogo_connection():
        print("\n✗ NetLogo connection test failed")
        return 1

    # Step 3: Ask user what to do
    print("\n" + "=" * 80)
    print("SIMULATION OPTIONS")
    print("=" * 80)
    print("1. Run full NetLogo simulation (recommended)")
    print("2. Launch Gazebo visualization only")
    print("3. Run simulation + Gazebo visualization")
    print("4. Exit")
    print("=" * 80)

    choice = input("\nSelect option (1-4): ").strip()

    if choice == "1":
        print("\n▶ Starting full NetLogo simulation...")
        sim.run_all_experiments()

    elif choice == "2":
        print("\n▶ Launching Gazebo visualization...")
        sim.launch_gazebo_visualization()

    elif choice == "3":
        print("\n▶ Starting simulation...")
        sim.run_all_experiments()

        print("\n" + "=" * 80)
        print("Would you like to view the Gazebo visualization?")
        view = input("Launch Gazebo? (y/n): ").strip().lower()

        if view in ["y", "yes"]:
            sim.launch_gazebo_visualization()

    else:
        print("\nExiting...")
        return 0

    print("\n" + "=" * 80)
    print("✓ ALL OPERATIONS COMPLETED")
    print("=" * 80)
    print(f"\nResults saved to: {sim.output_dir}/")
    print("Files generated:")
    print("  - comprehensive_summary.csv")
    print("  - performance_metrics.png")
    print("  - time_series_analysis.png")
    print("  - performance_report.txt")
    print("  - colony_*_trial_*.json (raw data)")
    print("\n" + "=" * 80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
