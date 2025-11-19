import os
import netlogo_utils

print("=" * 70)
print("FINAL NETLOGO TEST")
print("=" * 70)

# --- Configuration ---
NETLOGO_HOME = '/opt/netlogo-7.0.2'
MODEL_FILE = 'test.nlogo'
# ---------------------

print(f"NetLogo home: {NETLOGO_HOME}")
print(f"Model file: {MODEL_FILE}")

netlogo = None
try:
    print("\n[1/4] Initializing NetLogo...")
    # This is the corrected, simple version for pynetlogo 0.5.2.
    # It does NOT have the 'java_home' keyword.
    try:
        netlogo = netlogo_utils.init_netlogo(gui=False, netlogo_home=NETLOGO_HOME)
    except RuntimeError as e:
        print(f"\n✗ AN ERROR OCCURRED: {e}")
        raise
    print("      ✓ Done.")

    print("\n[2/4] Loading model...")
    netlogo.load_model(os.path.abspath(MODEL_FILE))
    print("      ✓ SUCCESS! Model loaded correctly.")

    print("\n[3/4] Running simulation commands...")
    netlogo.command('setup')
    netlogo.command('repeat 5 [ go ]')
    count = netlogo.report('count turtles')
    print(f"      ✓ Commands executed. Final turtle count: {count}.")

except Exception as e:
    print(f"\n✗ AN ERROR OCCURRED: {e}")
    print("\n   TROUBLESHOOTING:")
    print("   1. Is the JAVA_HOME environment variable set correctly before running?")
    print("   2. Is the NetLogo installation at /opt/netlogo-7.0.2/ intact?")

finally:
    if netlogo:
        print("\n[4/4] Closing NetLogo workspace...")
        netlogo.kill_workspace()
        print("      ✓ Done.")

print("\n" + "=" * 70)
