Support Interface Flow
====
This setting adjusts the flow rate for the support interface only. The flow rate for the support interface can be adjusted separately from the flow rate of the rest of the support.

Adjusting the flow rate during the support interface is a stop gap method to fix problems with extrusion rate or adhesion between the model and support. The same effect can be achieved by adjusting the [line width](support_interface_line_width.md) or [line spacing](support_roof_line_distance.md) of the support interface, but adjusting the flow rate may be more intuitive.

If there is a problem with extrusion rate, it is better to look at the [printing speeds](./speed_support_interface.md), [temperature](material_print_temperature.md) and [line width](support_interface_line_width.md). Perhaps there is too great of a difference between the flow rate of the support interface and the other structures on the layer. Perhaps the line width is too thin to extrude properly. If the interface is printed with a [different material](support_interface_extruder_nr.md), a common problem is that the material that the interface is printed with doesn't get enough time to start flowing properly. This can be fixed by using a [prime tower](prime_tower_enable.md) or increasing the [area of the support interface](support_interface_offset.md).

If the support sticks too well to the model, adjusting the [line width](support_interface_line_width.md) will usually be more effective since it also causes the lines to be closer together to achieve the same support infill density.