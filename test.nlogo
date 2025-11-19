<?xml version="1.0" encoding="utf-8"?>
<model version="NetLogo 7.0.2" snapToGrid="true">
  <code><![CDATA[
to setup
  clear-all
  create-turtles 10
  reset-ticks
end

to go
  ask turtles [ forward 1 ]
  tick
end
]]></code>
  <interface>
    <dimensions x="640" y="480" />
  </interface>
</model>
