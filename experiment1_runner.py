#!/usr/bin/env python3
import os
import netlogo_utils
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

NETLOGO_HOME = os.environ.get('NETLOGO_HOME', '/opt/netlogo-7.0.2')
NETLOGO_VERSION = '7.0'


class Experiment1Runner:
    def __init__(self):
        self.output_dir = Path('results')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []

    def run_single_trial(self, trial_num, colony_id):
        print(f"Running Trial {trial_num}, Colony {colony_id}...")
        try:
            netlogo = netlogo_utils.init_netlogo(gui=False, netlogo_home=NETLOGO_HOME, netlogo_version=NETLOGO_VERSION)

        except Exception as e:
            print(f"✗ Error initializing NetLogo: {e}\n")
            return None

        try:
            netlogo.load_model('final_ants.nlogo')
            netlogo.command('set initial-ant-count 100')
            netlogo.command(f'set trial-number {trial_num}')
            netlogo.command(f'set colony-id {colony_id}')
            netlogo.command('set simulation-duration 7200')
            netlogo.command('set pheromone-strength 60')
            netlogo.command('setup')

            for step in range(7200):
                netlogo.command('go')
                if step % 1200 == 0:
                    print(f"  Progress: {(step/7200)*100:.0f}%")

            results = {
                'trial': trial_num,
                'colony_id': colony_id,
                'discovery_time': netlogo.report('get-discovery-time'),
                'trail_formation_time': netlogo.report('get-trail-formation-time'),
                'food_collected': netlogo.report('food-collected'),
                'foraging_efficiency': netlogo.report('get-foraging-efficiency')
            }

            print(f"✓ Complete: {results['food_collected']} food collected\n")
            if hasattr(netlogo, 'kill_workspace'):
                try:
                    netlogo.kill_workspace()
                except Exception:
                    pass
            return results
        except Exception as e:
            print(f"✗ Error: {e}\n")
            if 'netlogo' in locals() and netlogo:
                try:
                    netlogo.kill_workspace()
                except Exception:
                    pass
            return None

    def run_experiment(self, num_trials=3, num_colonies=2):
        print("="*70)
        print("EXPERIMENT 1: BASELINE FORAGING DYNAMICS")
        print("="*70)
        print(f"Trials: {num_trials} | Colonies: {num_colonies}")
        print(f"Total simulations: {num_trials * num_colonies}\n")

        for colony in range(1, num_colonies + 1):
            for trial in range(1, num_trials + 1):
                result = self.run_single_trial(trial, colony)
                if result:
                    self.results.append(result)

        self.analyze_results()

    def analyze_results(self):
        df = pd.DataFrame(self.results)
        print("\n" + "="*70)
        print("RESULTS SUMMARY")
        print("="*70)
        print(f"\nDiscovery Time: {df['discovery_time'].mean():.2f} ± {df['discovery_time'].std():.2f} min")
        print(f"Trail Formation: {df['trail_formation_time'].mean():.2f} ± {df['trail_formation_time'].std():.2f} min")
        print(f"Food Collected: {df['food_collected'].mean():.1f} ± {df['food_collected'].std():.1f} units")
        print(f"Efficiency: {df['foraging_efficiency'].mean():.3f} ± {df['foraging_efficiency'].std():.3f} food/min")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.output_dir / f'experiment1_results_{timestamp}.csv'
        df.to_csv(csv_file, index=False)
        print(f"\n💾 Data saved: {csv_file}")

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes[0, 0].hist(df['discovery_time'], bins=8, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Discovery Time Distribution')
        axes[0, 0].set_xlabel('Minutes')
        axes[0, 0].set_ylabel('Frequency')

        axes[0, 1].hist(df['food_collected'], bins=8, color='lightgreen', edgecolor='black')
        axes[0, 1].set_title('Food Collection')
        axes[0, 1].set_xlabel('Food Units')
        axes[0, 1].set_ylabel('Frequency')

        axes[1, 0].scatter(df['discovery_time'], df['food_collected'], s=100, alpha=0.6)
        axes[1, 0].set_title('Discovery Time vs Food Collected')
        axes[1, 0].set_xlabel('Discovery Time (min)')
        axes[1, 0].set_ylabel('Food Collected')
        axes[1, 0].grid(alpha=0.3)

        axes[1, 1].axis('off')
        summary_text = f"""SUMMARY STATISTICS
Total Runs: {len(df)}

Discovery Time:
{df['discovery_time'].mean():.2f} ± {df['discovery_time'].std():.2f} min

Food Collected:
{df['food_collected'].mean():.1f} ± {df['food_collected'].std():.1f} units

Efficiency:
{df['foraging_efficiency'].mean():.3f} food/min"""
        axes[1, 1].text(0.1, 0.5, summary_text, fontsize=11, family='monospace', verticalalignment='center')

        plt.tight_layout()
        plot_file = self.output_dir / f'experiment1_plots_{timestamp}.png'
        plt.savefig(plot_file, dpi=300)
        print(f"📊 Plots saved: {plot_file}")
        plt.close()


if __name__ == "__main__":
    runner = Experiment1Runner()
    runner.run_experiment(num_trials=3, num_colonies=2)
