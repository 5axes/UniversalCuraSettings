Monotonic Top Surface Order
====
Normally, Cura orders lines such that the travel distance between them is small. If this setting is enabled, it will order the top surface lines such that adjacent lines are always printed overlapping in the same direction.

When printing top surface lines, the lines usually overlap a bit with the lines next to them, because the shape of a line is not a perfect rectangle. This overlap gives the lines a slight slope, causing them to reflect light differently in different directions. If adjacent lines overlap differently, this reflection changes. You can see this in the final result. It gives different areas of the surface a different shine. Printing in a monotonic order ensures that the overlap is the same on the entire surface, so there is no difference in how it reflects light. This makes the surface look more consistent and smooth.

![Not a monotonic order](images/skin_monotonic_disabled.gif)
![Monotonic order, always from the bottom-right corner](images/skin_monotonic_enabled.gif)

The monotonic order will slightly increase the length of travel moves, but this effect is very minimal. It only has a visual effect on the print. There are no mechanical advantages to the monotonic ordering.

To achieve a smooth surface, consider pairing this setting with setting the [Combing Mode](retraction_combing.md) to avoid skin, and perhaps to enable [Z Hops](retraction_hop.md). Alternatively you could also enable [ironing](ironing_enabled.md), but that completely overrides the usefulness of this setting. Ironing has its own [monotonic option](ironing_monotonic.md).