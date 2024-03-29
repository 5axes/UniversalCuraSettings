Infill Flow
====
This setting adjusts the flow rate for the infill only. The flow rate for the infill can be adjusted separately from the flow rate of the rest of the print.

Adjusting the flow rate during the infill is a stop gap method to fix problems with extrusion rate or strength. The same effect can be achieved by adjusting the [distance between lines](infill_line_distance.md) and [line width](infill_line_width.md) of the infill, but this setting may be more intuitive.

Problems with extrusion rate or strength of the infill are typically caused by one of two things: Crossings in the infill pattern, or too much of a change in flow rate between the infill and other structures. Rather than adjusting this flow rate, it may be more effective to adjust the [infill pattern](infill_pattern.md) or the [line width](infill_line_width.md). Choose an infill pattern that doesn't cross itself, such as zigzag, and choose a line width that is closer to the extrusion rate of the walls and skin. If the line width needs to be increased for strength but is limited in the flow rate, it's a good idea to use the [infill multiplier](infill_multiplier.md) instead of increasing the flow.