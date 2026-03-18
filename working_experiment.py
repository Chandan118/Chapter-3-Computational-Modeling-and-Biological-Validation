#!/usr/bin/env python3
"""
Working Experiment 1 - Baseline Foraging Dynamics
Fixed version that handles all common issues
"""

import sys
import os
import netlogo_utils

import pandas as pd
import numpy as np
import seaborn as sns
from pathlib import Path
import json
import time


class WorkingExperiment:
    """Fully working baseline foraging experiment"""

    def __init__(self):
        self.netlogo_home = '/opt/netlogo-7.0.2'
        self.model_path = 'final_ants.nlogo'
        self.output_dir = Path('experiment_1_results')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Reduced parameters for testing (adjust as needed)
        self.num_trials = 2  # Start with 2 trials
        self.num_colonies = 2  # Start with 2 colonies
        self.trial_duration = 600  # 10 minutes for testing (change to 7200 for full 2hr)
        self.measurement_interval = 10

        self.netlogo = None
        print(f"✓ Output directory: {self.output_dir}")

    def test_connection(self):
        """Test NetLogo connection before running experiments"""
        print("\n" + "="*70)
        print("TESTING NETLOGO CONNECTION")
        print("="*70)

        try:
            print("  NetLogo home: {}".format(self.netlogo_home))
            print("  Model file: {}".format(self.model_path))

            # Check model file exists
            if not os.path.exists(self.model_path):
                print(f"  ✗ Model file not found: {self.model_path}")
                return False

            print("  ✓ Model file found")

            # Initialize NetLogo
            print("  Initializing NetLogo (this may take 10-30 seconds)...")
            try:
                self.netlogo = netlogo_utils.init_netlogo(gui=False, netlogo_home=self.netlogo_home)
                if isinstance(self.netlogo, netlogo_utils.MockNetLogoLink):
                    print("\n" + "!"*70)
                    print("WARNING: Running in MOCK mode. No real NetLogo simulation will be run.")
                    print("!"*70 + "\n")
                print("  ✓ NetLogo initialized")
            except Exception as e:
                print(f"  ✗ Failed to initialize NetLogo: {e}")
                raise

            # Load model
            print("  Loading model...")
            self.netlogo.load_model(self.model_path)
            print("  ✓ Model loaded")

            # Test setup command
            print("  Testing setup command...")
            self.netlogo.command('setup')
            print("  ✓ Setup works")

            # Test report command
            print("  Testing report command...")
            count = self.netlogo.report('count turtles')
            print("  ✓ Report works (found {} turtles)".format(count))

            # Test go command
            print("  Testing go command...")
            self.netlogo.command('repeat 5 [go]')
            print("  ✓ Go command works")

            print("\n✓ All connection tests passed!")
            return True

        except Exception as e:
            print(f"\n✗ Connection test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            if self.netlogo:
                try:
                    self.netlogo.kill_workspace()
                    print("  Connection closed")
                except Exception:
                    pass

    def run_single_trial(self, colony_id, trial_id):
        """Run one trial with better error handling"""
        print(f"\n{'─'*70}")
        print(f"Running: Colony {colony_id}, Trial {trial_id}")
        print(f"{'─'*70}")

        try:
            # Setup with colony-specific parameters
            self.netlogo.command('setup')

            diffusion = 50 + (colony_id - 1) * 5
            evaporation = 10 + (colony_id - 1) * 2

            self.netlogo.command(f'set diffusion-rate {diffusion}')
            self.netlogo.command(f'set evaporation-rate {evaporation}')

            print(f"  Parameters: diffusion={diffusion}, evaporation={evaporation}")

            # Data collection
            data = {
                'colony_id': colony_id,
                'trial_id': trial_id,
                'ticks': [],
                'ants_with_food': [],
                'returning_ants': [],
                'chemical_level': []
            }

            start_time = time.time()

            # Run simulation
            for tick in range(0, self.trial_duration, self.measurement_interval):
                # Execute steps
                self.netlogo.command(f'repeat {self.measurement_interval} [go]')

                # Collect data with error handling
                try:
                    ants_food = self.netlogo.report('count turtles with [has-food?]')
                    chemical = self.netlogo.report('mean [pheromone] of patches')

                    data['ticks'].append(tick)
                    data['ants_with_food'].append(ants_food)
                    data['returning_ants'].append(ants_food)  # Simplified
                    data['chemical_level'].append(chemical)

                except Exception as e:
                    print(f"  Warning: Data collection error at tick {tick}: {e}")
                    # Use default values
                    data['ticks'].append(tick)
                    data['ants_with_food'].append(0)
                    data['returning_ants'].append(0)
                    data['chemical_level'].append(0)

                # Progress update
                if tick % 100 == 0:
                    progress = (tick / self.trial_duration) * 100
                    elapsed = time.time() - start_time
                    print(f"  Progress: {progress:.0f}% (tick {tick}/{self.trial_duration}, {elapsed:.1f}s)")

            # Calculate simple metrics
            total_ants_found = sum(1 for x in data['ants_with_food'] if x > 0)
            avg_chemical = np.mean(data['chemical_level']) if data['chemical_level'] else 0

            data['metrics'] = {
                'discovery_rate': total_ants_found / len(data['ticks']) if data['ticks'] else 0,
                'avg_chemical': float(avg_chemical),
                'max_ants': int(max(data['ants_with_food'])) if data['ants_with_food'] else 0
            }

            print("  Results:")
            print(f"    Discovery rate: {data['metrics']['discovery_rate']:.3f}")
            print(f"    Avg chemical: {data['metrics']['avg_chemical']:.3f}")
            print(f"    Max ants with food: {data['metrics']['max_ants']}")

            # Save trial data
            self.save_trial(data)

            return data

        except Exception as e:
            print(f"  ✗ Trial failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def save_trial(self, data):
        """Save trial data"""
        filename = self.output_dir / f"colony_{data['colony_id']}_trial_{data['trial_id']}.json"

        # Convert numpy types to native Python types
        save_data = {}
        for key, value in data.items():
            if isinstance(value, (list, np.ndarray)):
                converted = []
                for x in value:
                    if isinstance(x, (np.integer, np.floating)):
                        converted.append(float(x))
                    else:
                        converted.append(x)
                save_data[key] = converted
            elif isinstance(value, dict):
                converted_dict = {}
                for k, v in value.items():
                    if isinstance(v, (np.integer, np.floating)):
                        converted_dict[k] = float(v)
                    else:
                        converted_dict[k] = v
                save_data[key] = converted_dict
            else:
                save_data[key] = value

        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)

        print(f"  ✓ Saved to: {filename.name}")

    def run_all_trials(self):
        """Run all trials"""
        print("\n" + "="*70)
        print("EXPERIMENT 1: BASELINE FORAGING DYNAMICS")
        print("="*70)
        print("Configuration:")
        print(f"  Colonies: {self.num_colonies}")
        print(f"  Trials per colony: {self.num_trials}")
        print(f"  Duration per trial: {self.trial_duration/60:.1f} minutes")
        print(f"  Total trials: {self.num_colonies * self.num_trials}")
        print("="*70)

        all_results = []

        try:
            # Initialize NetLogo once
            print("\nInitializing NetLogo...")
            try:
                self.netlogo = netlogo_utils.init_netlogo(gui=False, netlogo_home=self.netlogo_home)
                if isinstance(self.netlogo, netlogo_utils.MockNetLogoLink):
                    print("\n" + "!"*70)
                    print("WARNING: Running in MOCK mode. No real NetLogo simulation will be run.")
                    print("!"*70 + "\n")
                self.netlogo.load_model(self.model_path)
                print("✓ Ready to run experiments\n")
            except Exception as e:
                print(f"✗ Failed to initialize NetLogo for experiments: {e}")
                import traceback
                traceback.print_exc()
                return

            # Run all trials
            for colony_id in range(1, self.num_colonies + 1):
                print(f"\n{'═'*70}")
                print(f"COLONY {colony_id}")
                print(f"{'═'*70}")

                for trial_id in range(1, self.num_trials + 1):
                    result = self.run_single_trial(colony_id, trial_id)
                    if result:
                        all_results.append(result)

            # Generate summary
            if all_results:
                self.generate_summary(all_results)

            print("\n" + "="*70)
            print("✓ EXPERIMENT COMPLETED")
            print(f"  Total trials run: {len(all_results)}")
            print(f"  Results saved to: {self.output_dir}")
            print("="*70 + "\n")

        except Exception as e:
            print(f"\n✗ Experiment failed: {str(e)}")
            import traceback
            traceback.print_exc()

        finally:
            if self.netlogo:
                try:
                    self.netlogo.kill_workspace()
                    print("NetLogo connection closed")
                except Exception:
                    pass

    def generate_summary(self, results):
        """Generate summary statistics and plots"""
        print("\n" + "="*70)
        print("GENERATING SUMMARY")
        print("="*70)

        # Extract metrics
        summary_data = []
        for result in results:
            row = {
                'colony_id': result['colony_id'],
                'trial_id': result['trial_id'],
                **result['metrics']
            }
            summary_data.append(row)

        df = pd.DataFrame(summary_data)

        # Save CSV
        csv_file = self.output_dir / 'summary_all_trials.csv'
        df.to_csv(csv_file, index=False)
        print(f"✓ Summary saved to: {csv_file.name}")

        # Print statistics
        print("\nSummary Statistics:")
        print(df.describe().round(3))

        # Create plots
        self.create_plots(df, results)

    def create_plots(self, df, results):
        """Create visualization plots"""
        print("\nGenerating plots...")

        try:
            # Set style
            sns.set_style("whitegrid")

            # Import plotting backend locally to avoid module-level side-effects
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            # Plot 1: Metrics by colony
            fig, axes = plt.subplots(1, 3, figsize=(15, 4))
            fig.suptitle('Experiment 1: Summary Metrics', fontsize=14, fontweight='bold')

            # Discovery rate
            sns.barplot(data=df, x='colony_id', y='discovery_rate', ax=axes[0], palette='Set2')
            axes[0].set_title('Discovery Rate')
            axes[0].set_ylabel('Rate')

            # Average chemical
            sns.barplot(data=df, x='colony_id', y='avg_chemical', ax=axes[1], palette='Set2')
            axes[1].set_title('Average Chemical Level')
            axes[1].set_ylabel('Chemical')

            # Max ants
            sns.barplot(data=df, x='colony_id', y='max_ants', ax=axes[2], palette='Set2')
            axes[2].set_title('Max Ants with Food')
            axes[2].set_ylabel('Ants')

            plt.tight_layout()
            plot_file = self.output_dir / 'summary_metrics.png'
            plt.savefig(plot_file, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved: {plot_file.name}")
            plt.close()

            # Plot 2: Time series for first trial
            if results:
                first_trial = results[0]

                fig, axes = plt.subplots(2, 1, figsize=(10, 8))
                title = (
                    f"Trial Details: Colony {first_trial['colony_id']}, "
                    f"Trial {first_trial['trial_id']}"
                )
                fig.suptitle(title, fontsize=12, fontweight='bold')

                ticks = np.array(first_trial['ticks'])

                # Ants with food
                axes[0].plot(ticks, first_trial['ants_with_food'], 'b-', linewidth=2)
                axes[0].set_xlabel('Time (ticks)')
                axes[0].set_ylabel('Ants with Food')
                axes[0].set_title('Foraging Activity')
                axes[0].grid(True, alpha=0.3)

                # Chemical level
                axes[1].plot(ticks, first_trial['chemical_level'], 'g-', linewidth=2)
                axes[1].set_xlabel('Time (ticks)')
                axes[1].set_ylabel('Chemical Level')
                axes[1].set_title('Pheromone Trail Strength')
                axes[1].grid(True, alpha=0.3)

                plt.tight_layout()
                plot_file = self.output_dir / 'trial_timeseries.png'
                plt.savefig(plot_file, dpi=150, bbox_inches='tight')
                print(f"  ✓ Saved: {plot_file.name}")
                plt.close()

            print("✓ All plots generated")

        except Exception as e:
            print(f"  Warning: Plot generation error: {e}")


def main():
    """Main function with user-friendly interface"""
    print("\n" + "="*70)
    print("FORMICABOT SIMULATIONS - EXPERIMENT 1")
    print("="*70)

    exp = WorkingExperiment()

    # First test connection
    print("\nStep 1: Testing NetLogo connection...")
    if not exp.test_connection():
        print("\n✗ Connection test failed. Please fix issues before running experiments.")
        print("\nTroubleshooting:")
        print("  1. Check if NetLogo is at /opt/netlogo-7.0.2/")
        print("  2. Check if final_ants.nlogo exists")
        print("  3. Verify Java is installed: java -version")
        sys.exit(1)

    # Ask user to confirm
    print("\n" + "-"*70)
    print("Ready to run experiment with:")
    print(f"  • {exp.num_colonies} colonies")
    print(f"  • {exp.num_trials} trials per colony")
    print(f"  • {exp.trial_duration/60:.1f} minutes per trial")
    print(f"  • Total time: ~{(exp.num_colonies * exp.num_trials * exp.trial_duration/60):.0f} minutes")
    print("-"*70)

    response = input("\nContinue? (yes/no): ").strip().lower()

    if response in ['yes', 'y']:
        print("\nStarting experiments...\n")
        exp.run_all_trials()
    else:
        print("\nExperiment cancelled.")

    print("\nDone!")


if __name__ == "__main__":
    main()
