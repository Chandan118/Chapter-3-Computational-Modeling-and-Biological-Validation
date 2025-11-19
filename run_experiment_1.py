#!/usr/bin/env python3
"""Quick test to verify everything works"""
import time
import netlogo_utils

print("="*70)
print("QUICK NETLOGO TEST")
print("="*70)

NETLOGO_HOME = '/opt/netlogo-7.0.2'
MODEL_FILE = 'final_ants.nlogo'

print(f"\nNetLogo home: {NETLOGO_HOME}")
print(f"Model file: {MODEL_FILE}")

try:
    print("\n[1/5] Initializing NetLogo...")
    print("      (This may take 10-30 seconds on first run)")
    start = time.time()
    try:
        netlogo = netlogo_utils.init_netlogo(gui=False, netlogo_home=NETLOGO_HOME)
    except RuntimeError as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    print(f"      ✓ Done ({time.time()-start:.1f}s)")

    print("\n[2/5] Loading model...")
    start = time.time()
    netlogo.load_model(MODEL_FILE)
    print(f"      ✓ Done ({time.time()-start:.1f}s)")

    print("\n[3/5] Running setup...")
    start = time.time()
    netlogo.command('setup')
    print(f"      ✓ Done ({time.time()-start:.1f}s)")

    print("\n[4/5] Checking initial state...")
    num_turtles = netlogo.report('count turtles')
    num_patches = netlogo.report('count patches')
    print(f"      ✓ Found {num_turtles} ants")
    print(f"      ✓ Found {num_patches} patches")

    print("\n[5/5] Running 50 simulation steps...")
    start = time.time()
    for i in range(5):
        netlogo.command('repeat 10 [go]')
        ants_with_food = netlogo.report('count turtles with [food > 0]')
        chemical = netlogo.report('mean [chemical] of patches')
        print(f"      Step {(i+1)*10}: {ants_with_food} ants found food, avg chemical: {chemical:.4f}")
    print(f"      ✓ Done ({time.time()-start:.1f}s)")

    print("\n[✓] Closing connection...")
    netlogo.kill_workspace()

    print("\n" + "="*70)
    print("SUCCESS! Everything is working correctly.")
    print("You can now run: python3 run_experiment_1.py")
    print("="*70 + "\n")

except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
