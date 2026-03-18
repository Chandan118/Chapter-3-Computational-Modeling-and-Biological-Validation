;; ant_foraging.nlogo - NetLogo 7.0.2 Format

globals [
  food-collected
  discovery-time
  trail-formation-time
  foraging-efficiency
]

breed [ants ant]
ants-own [ has-food? ]
patches-own [ pheromone nest? food-source? ]

to setup
  clear-all
  set food-collected 0
  set discovery-time -1
  set trail-formation-time -1
  ask patches with [pxcor < -10] [ set nest? true set pcolor brown ]
  ask patches with [pxcor > 10] [ set food-source? true set pcolor green ]
  ;; normalize nest? to boolean values to avoid headless/runtime type errors
  ask patches [ set nest? (nest? != 0) ]
  create-ants initial-ant-count [
    set color red
    set has-food? false
    if any? patches with [nest?] [ move-to one-of patches with [nest?] ]
  ]
  ; ensure any numeric-encoded booleans are coerced after clear-all and patch setup
  preflight
  reset-ticks
end

to go
  if ticks >= simulation-duration [ stop ]
  ask ants [
    ifelse has-food? [ go-nest ] [ find-food ]
  ]
  diffuse pheromone 0.5
  ask patches [ set pheromone pheromone * 0.92 ]
  if ticks > 0 [ set foraging-efficiency food-collected / (ticks / 60.0) ]
  tick
end

to preflight
  ;; coerce numeric-encoded booleans into real booleans for headless runs
  ask patches [ set nest? (nest? != 0) set food-source? (food-source? != 0) ]
  ask turtles [ ifelse (has-food? = 0) [ set has-food? false ] [ set has-food? true ] ]
end

to find-food
  forward 1
  if food-source? [
    set has-food? true
    set color orange
    if discovery-time = -1 [ set discovery-time ticks ]
  ]
end

to go-nest
  if any? patches with [nest?] [ face min-one-of patches with [nest?] [distance myself] ]
  forward 1
  set pheromone pheromone + pheromone-strength
  if nest? [
    set has-food? false
    set color red
    set food-collected food-collected + 1
  ]
end

to-report get-discovery-time
  report discovery-time / 60.0
end

to-report get-trail-formation-time
  report -1
end

to-report get-foraging-efficiency
  report foraging-efficiency
end
@#$#@#$#@
GRAPHICS-WINDOW
210
10
647
448
-1
-1
13.0
1
10
1
1
1
0
1
1
1
-16
16
-16
16
0
0
1
ticks
30.0

BUTTON
18
28
84
61
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
97
28
160
61
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
18
78
190
111
initial-ant-count
initial-ant-count
10
200
100.0
1
1
NIL
HORIZONTAL

SLIDER
18
123
190
156
simulation-duration
simulation-duration
1000
10000
7200.0
100
1
NIL
HORIZONTAL

SLIDER
18
168
190
201
pheromone-strength
pheromone-strength
20
100
60.0
5
1
NIL
HORIZONTAL

SLIDER
18
213
190
246
trial-number
trial-number
1
10
1.0
1
1
NIL
HORIZONTAL

SLIDER
18
258
190
291
colony-id
colony-id
1
5
1.0
1
1
NIL
HORIZONTAL

MONITOR
18
303
175
348
Food Collected
food-collected
17
1
11

@#$#@#$#@
## WHAT IS IT?

Ant foraging simulation for thesis experiments.

## HOW IT WORKS

Ants search for food and return to nest depositing pheromones.

## HOW TO USE IT

1. Click SETUP
2. Click GO
3. Watch ants collect food

## CREDITS

Created for FormicaBot thesis experiments.
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30
@#$#@#$#@
NetLogo 7.0.2
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
ENDFILE

