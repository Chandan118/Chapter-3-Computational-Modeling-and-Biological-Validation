cat > pheidole_working.nlogo << 'EOFMODEL'
extensions [csv table]

globals [
  food-collected
  discovery-time
  trail-formation-time
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
    set color red
    set size 1.5
    set shape "bug"
    set has-food? false
    move-to one-of patches with [nest?]
    set search-angle random 360
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

to go
  if ticks >= simulation-duration [ stop ]
  ask ants [
    ifelse has-food?
      [ return-to-nest ]
      [ search-for-food ]
  ]
  diffuse pheromone pheromone-diffusion-rate
  ask patches [
    set pheromone pheromone * (1 - pheromone-decay-rate)
    if not nest? and not food-source? [
      ifelse pheromone > 0 [
        set pcolor scale-color yellow pheromone 0 150
      ] [ set pcolor white ]
    ]
  ]
  if ticks > 0 [
    set foraging-efficiency (food-collected / (ticks / 60.0))
  ]
  tick
end

to search-for-food
  let ahead-pheromone 0
  if patch-ahead 1 != nobody [
    set ahead-pheromone [pheromone] of patch-ahead 1
  ]
  ifelse ahead-pheromone > [pheromone] of patch-here [
    ifelse random-float 1.0 < 0.8 [ forward 1 ] [ right random 30 - 15 forward 0.5 ]
  ] [
    right (search-angle - 180) + random 90 - 45
    forward 1
  ]
  if food-source? [
    set has-food? true
    set color orange
    if discovery-time = -1 [ set discovery-time ticks ]
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
    if not trail-established? and ticks > 600 [
      if count ants with [has-food?] > stable-trail-threshold [
        set trail-established? true
        set trail-formation-time ticks
      ]
    ]
  ]
end

to-report get-discovery-time
  report discovery-time / 60.0
end

to-report get-trail-formation-time
  ifelse trail-formation-time > 0 [ report trail-formation-time / 60.0 ] [ report -1 ]
end

to-report get-foraging-efficiency
  report foraging-efficiency
end
EOFMODEL

# Verify it was created
ls -lh pheidole_working.nlogo
head -10 pheidole_working.nlogo

# Test it works
python3 << 'EOF'
import pynetlogo
netlogo = pynetlogo.NetLogoLink(gui=False, netlogo_home='/opt/netlogo-7.0.2')
try:
    netlogo.load_model('pheidole_working.nlogo')
    print("✓ Model loaded!")
    netlogo.command('set initial-ant-count 50')
    netlogo.command('set simulation-duration 100')
    netlogo.command('set pheromone-strength 60')
    netlogo.command('set trial-number 1')
    netlogo.command('set colony-id 1')
    netlogo.command('setup')
    print("✓ Setup successful!")
    for i in range(100):
        netlogo.command('go')
    food = netlogo.report('food-collected')
    print(f"✓ Simulation works! Food collected: {food}")
    netlogo.kill_workspace()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
EOF