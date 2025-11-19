#!/usr/bin/env python3
import os

import netlogo_utils
import pandas as pd
import time

print("=" * 70)
print("ANT FORAGING EXPERIMENT - Using Official NetLogo Ants Model")
print("=" * 70)

results = []

try:
    netlogo = netlogo_utils.init_netlogo(gui=False, netlogo_home='/opt/netlogo-7.0.2')
    netlogo.load_model('final_ants.nlogo')
    print("✓ Model loaded successfully\n")

    for trial in range(1, 4):
        print(f"Running Trial {trial}/3...")
        netlogo.command('setup')

        for step in range(5000):
            netlogo.command('go')
            if step % 1000 == 0 and step > 0:
                print(f"  {step} steps completed...")

        try:
            food = netlogo.report('count patches with [food > 0]')
        except Exception:
            food = 0

        try:
            ants = netlogo.report('count turtles')
        except Exception:
            ants = 0

        results.append({
            'trial': trial,
            'remaining_food_patches': food,
            'ants': ants,
            'steps': 5000
        })

        print(f"  ✓ Trial {trial} complete\n")

    # ensure results dir exists
    os.makedirs('results', exist_ok=True)
    df = pd.DataFrame(results)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    df.to_csv(f'results/ants_experiment_{timestamp}.csv', index=False)
    print("="*70)
    print("RESULTS:")
    print("="*70)
    print(df.to_string())
    print(f"\n✓ Saved to: results/ants_experiment_{timestamp}.csv")
    if 'netlogo' in locals() and netlogo:
        netlogo.kill_workspace()

except Exception as e:
    print(f"\n✗ Error: {e}")
    if 'netlogo' in locals() and netlogo:
        try:
            netlogo.kill_workspace()
        except Exception:
            pass
