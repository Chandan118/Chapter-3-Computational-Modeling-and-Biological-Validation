import os
import netlogo_utils

# --- Configuration ---
NETLOGO_HOME = '/opt/netlogo-7.0.2'
MODEL_FILE = 'simple_ants.nlogo'
# ---------------------

model_path = os.path.abspath(MODEL_FILE)
if not os.path.exists(model_path):
    print(f"Error: Model file not found at {model_path}")
    exit()

netlogo = None
try:
    print("Initializing NetLogo link...")
    try:
        netlogo = netlogo_utils.init_netlogo(gui=False, netlogo_home=NETLOGO_HOME)
    except RuntimeError as e:
        print(f"An error occurred while initializing NetLogo: {e}")
        netlogo = None
        raise

    print(f"Loading model: {model_path}")
    netlogo.load_model(model_path)

    print("Running 'setup' command...")
    netlogo.command('setup')

    print("Running model for 10 ticks and reporting 'count ants'...")
    counts = netlogo.repeat_report(['count ants'], 10)

    print("\n--- Results ---")
    print(counts)
    print("---------------")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if netlogo:
        print("Closing NetLogo workspace.")
        netlogo.kill_workspace()
