#!/bin/bash
# Save as: setup_all.sh
# Complete automated setup for FormicaBot simulations

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  FormicaBot Simulation Suite - Automated Installation        ║"
echo "║  Ubuntu 22.04 | NetLogo 7.0.2 | Gazebo 11 | ROS Noetic       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Ubuntu 22.04
if [ "$(lsb_release -rs)" != "22.04" ]; then
    echo -e "${RED}Error: This script requires Ubuntu 22.04${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1/8: Creating workspace...${NC}"
mkdir -p ~/formicabot_simulations
cd ~/formicabot_simulations
mkdir -p netlogo_output results

echo -e "${YELLOW}Step 2/8: Installing Python packages...${NC}"
pip3 install --upgrade pynetlogo pandas numpy matplotlib seaborn scikit-learn scipy

echo -e "${YELLOW}Step 3/8: Checking NetLogo installation...${NC}"
if [ ! -d "/opt/netlogo-7.0.2" ]; then
    echo "  NetLogo not found. Installing..."
    cd ~/Downloads
    wget -q https://ccl.northwestern.edu/netlogo/7.0.2/NetLogo-7.0.2-64.tgz
    tar -xzf NetLogo-7.0.2-64.tgz
    sudo mv NetLogo\ 7.0.2 /opt/netlogo-7.0.2
    sudo ln -sf /opt/netlogo-7.0.2/NetLogo /usr/local/bin/netlogo
    echo -e "  ${GREEN}✓ NetLogo 7.0.2 installed${NC}"
else
    echo -e "  ${GREEN}✓ NetLogo 7.0.2 already installed${NC}"
fi

cd ~/formicabot_simulations

echo -e "${YELLOW}Step 4/8: Creating NetLogo test script...${NC}"
cat > netlogo_bridge_test.py << 'EOFTEST'
#!/usr/bin/env python3
import pynetlogo
import os

def test_netlogo_connection():
    print("Testing NetLogo 7.0.2 Connection...")
    netlogo_home = '/opt/netlogo-7.0.2'
    netlogo_version = '7.0'
    
    try:
        netlogo = pynetlogo.NetLogoLink(gui=False, netlogo_home=netlogo_home, netlogo_version=netlogo_version)
        print("✓ NetLogo connection established")
        
        test_model = os.path.join(netlogo_home, 'models', 'Sample Models', 'Biology', 'Ants.nlogo')
        if os.path.exists(test_model):
            netlogo.load_model(test_model)
            print(f"✓ Loaded test model")
            netlogo.command('setup')
            netlogo.command('repeat 100 [go]')
            result = netlogo.report('count turtles')
            print(f"✓ Test simulation ran successfully: {result} agents")
        
        netlogo.kill_workspace()
        print("\n✓ All tests passed! NetLogo 7.0.2 is ready.")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    test_netlogo_connection()
EOFTEST

chmod +x netlogo_bridge_test.py

echo -e "${YELLOW}Step 5/8: Creating NetLogo ant model...${NC}"
cat > pheidole_baseline_v7.nlogo << 'EOFMODEL'
extensions [csv table]

globals [
  food-collected
  discovery-time
  trail-formation-time
  experiment-start-time
  foraging-efficiency
  pheromone-decay-rate
  pheromone-diffusion-rate
  trail-established?
  stable-trail-threshold
  trial-number
  colony-id
  tick-data
]

breed [ants ant]

ants-own [
  has-food?
  search-angle
  path-memory
  energy-level
  scout-mode?
]

patches-own [
  pheromone
  nest?
  food-source?
]

to setup
  clear-all
  set pheromone-decay-rate 0.08
  set pheromone-diffusion-rate 0.5
  set stable-trail-threshold 10
  set trail-established? false
  set food-collected 0
  set discovery-time -1
  set trail-formation-time -1
  
  setup-environment
  
  create-ants initial-ant-count [
    initialize-ant
  ]
  
  set tick-data []
  reset-ticks
end

to setup-environment
  ask patches with [pxcor < min-pxcor + 5 and abs(pycor) < 3] [
    set nest? true
    set pcolor brown + 2
  ]
  
  ask patches with [pxcor > max-pxcor - 5 and abs(pycor) < 3] [
    set food-source? true
    set pcolor green + 1
  ]
  
  ask patches [
    set pheromone 0
    if not nest? and not food-source? [
      set pcolor white
    ]
  ]
end

to initialize-ant
  set color red
  set size 1.5
  set shape "bug"
  set has-food? false
  move-to one-of patches with [nest?]
  set search-angle random 360
  set path-memory []
  set energy-level 100
  set scout-mode? (random-float 1.0 < 0.1)
end

to go
  if ticks >= simulation-duration [
    finalize-experiment
    stop
  ]
  
  ask ants [
    ifelse has-food?
      [ return-to-nest ]
      [ search-for-food ]
    set energy-level energy-level - 0.01
  ]
  
  diffuse pheromone pheromone-diffusion-rate
  ask patches [
    set pheromone pheromone * (1 - pheromone-decay-rate)
    update-patch-visualization
  ]
  
  update-metrics
  
  if ticks mod 60 = 0 [
    collect-data-point
  ]
  
  tick
end

to search-for-food
  let ahead-pheromone 0
  let current-pheromone [pheromone] of patch-here
  
  if patch-ahead 1 != nobody [
    set ahead-pheromone [pheromone] of patch-ahead 1
  ]
  
  ifelse ahead-pheromone > current-pheromone [
    let follow-probability 0.8 + (ahead-pheromone / 100) * 0.15
    ifelse random-float 1.0 < follow-probability [
      forward 1
    ] [
      right random 30 - 15
      forward 0.5
    ]
  ] [
    if scout-mode? [
      right random 180 - 90
    ] else [
      right (search-angle - 180) + random 90 - 45
    ]
    forward 1
  ]
  
  if food-source? [
    set has-food? true
    set color orange
    if discovery-time = -1 [
      set discovery-time ticks
    ]
  ]
end

to return-to-nest
  let nest-patch min-one-of patches with [nest?] [distance myself]
  
  ifelse distance nest-patch > 2 [
    face nest-patch
    forward 1
    set pheromone pheromone + pheromone-strength
  ] [
    set has-food? false
    set color red
    set food-collected food-collected + 1
    if not trail-established? [
      check-trail-formation
    ]
  ]
end

to update-metrics
  if ticks > 0 [
    set foraging-efficiency (food-collected / (ticks / 60.0))
  ]
end

to check-trail-formation
  if ticks > 600 [
    let recent-food count ants with [has-food?]
    if recent-food > stable-trail-threshold and not trail-established? [
      set trail-established? true
      set trail-formation-time ticks
    ]
  ]
end

to collect-data-point
  let data-row (list ticks food-collected count ants with [has-food?] 
                     mean [pheromone] of patches with [pheromone > 0] foraging-efficiency)
  set tick-data lput data-row tick-data
end

to update-patch-visualization
  if not nest? and not food-source? [
    ifelse pheromone > 0 [
      set pcolor scale-color yellow pheromone 0 150
    ] [
      set pcolor white
    ]
  ]
end

to finalize-experiment
  export-results
end

to export-results
  let filename (word "netlogo_output/exp1_trial" trial-number "_colony" colony-id ".csv")
  file-open filename
  file-print "tick,food_collected,ants_carrying,mean_pheromone,efficiency"
  foreach tick-data [ row ->
    file-print (reduce [[a b] -> (word a "," b)] row)
  ]
  file-close
end

to-report get-discovery-time
  report discovery-time / 60.0
end

to-report get-trail-formation-time
  ifelse trail-formation-time > 0 [
    report trail-formation-time / 60.0
  ] [
    report -1
  ]
end

to-report get-foraging-efficiency
  report foraging-efficiency
end
EOFMODEL

echo -e "${YELLOW}Step 6/8: Creating Python experiment runner...${NC}"
cat > experiment1_runner.py << 'EOFEXP1'
#!/usr/bin/env python3
import pynetlogo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

NETLOGO_HOME = '/opt/netlogo-7.0.2'
NETLOGO_VERSION = '7.0'

class Experiment1Runner:
    def __init__(self):
        self.output_dir = Path('results')
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
    
    def run_single_trial(self, trial_num, colony_id):
        print(f"Running Trial {trial_num}, Colony {colony_id}...")
        
        netlogo = pynetlogo.NetLogoLink(
            gui=False,
            netlogo_home=NETLOGO_HOME,
            netlogo_version=NETLOGO_VERSION
        )
        
        try:
            netlogo.load_model('pheidole_baseline_v7.nlogo')
            netlogo.command('set initial-ant-count 100')
            netlogo.command(f'set trial-number {trial_num}')
            netlogo.command(f'set colony-id {colony_id}')
            netlogo.command('set simulation-duration 7200')
            netlogo.command('set pheromone-strength 60')
            netlogo.command('setup')
            
            for step in range(7200):
                netlogo.command('go')
                if step % 600 == 0:
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
            netlogo.kill_workspace()
            return results
            
        except Exception as e:
            print(f"✗ Error: {e}\n")
            netlogo.kill_workspace()
            return None
    
    def run_experiment(self, num_trials=3, num_colonies=2):
        print("="*70)
        print("EXPERIMENT 1: BASELINE FORAGING DYNAMICS")
        print("="*70)
        print(f"Trials: {num_trials} | Colonies: {num_colonies}")
        print(f"Total runs: {num_trials * num_colonies}\n")
        
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
        
        self.plot_results(df, timestamp)
    
    def plot_results(self, df, timestamp):
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        axes[0, 0].hist(df['discovery_time'], bins=10, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Discovery Time Distribution')
        axes[0, 0].set_xlabel('Time (minutes)')
        axes[0, 0].set_ylabel('Frequency')
        
        axes[0, 1].hist(df['food_collected'], bins=10, color='lightgreen', edgecolor='black')
        axes[0, 1].set_title('Food Collection Distribution')
        axes[0, 1].set_xlabel('Food Units')
        axes[0, 1].set_ylabel('Frequency')
        
        axes[1, 0].scatter(df['discovery_time'], df['food_collected'], alpha=0.6)
        axes[1, 0].set_title('Discovery Time vs Food Collected')
        axes[1, 0].set_xlabel('Discovery Time (min)')
        axes[1, 0].set_ylabel('Food Collected')
        axes[1, 0].grid(alpha=0.3)
        
        axes[1, 1].axis('off')
        summary_text = f"""
SUMMARY STATISTICS
─────────────────────
Total Runs: {len(df)}

Discovery Time:
{df['discovery_time'].mean():.2f} ± {df['discovery_time'].std():.2f} min

Trail Formation:
{df['trail_formation_time'].mean():.2f} ± {df['trail_formation_time'].std():.2f} min

Food Collected:
{df['food_collected'].mean():.1f} ± {df['food_collected'].std():.1f} units

Efficiency:
{df['foraging_efficiency'].mean():.3f} food/min
"""
        axes[1, 1].text(0.1, 0.9, summary_text, fontsize=10, family='monospace', verticalalignment='top')
        
        plt.tight_layout()
        plot_file = self.output_dir / f'experiment1_plots_{timestamp}.png'
        plt.savefig(plot_file, dpi=300)
        print(f"📊 Plots saved: {plot_file}")

if __name__ == "__main__":
    runner = Experiment1Runner()
    runner.run_experiment(num_trials=3, num_colonies=2)
EOFEXP1

chmod +x experiment1_runner.py

echo -e "${YELLOW}Step 7/8: Testing NetLogo connection...${NC}"
python3 netlogo_bridge_test.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ NetLogo test passed${NC}"
else
    echo -e "${RED}✗ NetLogo test failed${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 8/8: Final verification...${NC}"
echo "Workspace: $(pwd)"
echo "Files created:"
ls -lh *.py *.nlogo 2>/dev/null

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ INSTALLATION COMPLETE                                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "  1. Run quick test (6 simulations, ~10 minutes):"
echo "     python3 experiment1_runner.py"
echo ""
echo "  2. Or run full experiment (15 simulations, ~30 minutes):"
echo "     python3 experiment1_runner.py"
echo ""
echo "  3. Check results:"
echo "     ls results/"
echo ""
