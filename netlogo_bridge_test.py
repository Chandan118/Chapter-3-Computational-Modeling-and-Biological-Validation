#!/usr/bin/env python3
import os
import netlogo_utils


def test_netlogo_connection():
    print("Testing NetLogo 7.0.2 Connection...")
    netlogo_home = os.environ.get('NETLOGO_HOME', '/opt/netlogo-7.0.2')
    netlogo_version = '7.0'
    try:
        netlogo = netlogo_utils.init_netlogo(gui=False, netlogo_home=netlogo_home, netlogo_version=netlogo_version)
        print("✓ NetLogo connection established")
        test_model = os.path.join(netlogo_home, 'models', 'Sample Models', 'Biology', 'Ants.nlogo')
        if os.path.exists(test_model):
            netlogo.load_model(test_model)
            print("✓ Loaded test model")
            netlogo.command('setup')
            netlogo.command('repeat 100 [go]')
            result = netlogo.report('count turtles')
            print(f"✓ Test ran: {result} agents")
        if 'netlogo' in locals() and netlogo:
            try:
                netlogo.kill_workspace()
            except Exception:
                pass
        print("\n✓ NetLogo ready!")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    test_netlogo_connection()
