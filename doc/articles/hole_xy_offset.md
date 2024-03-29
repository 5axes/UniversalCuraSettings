Hole Horizontal Expansion
====
This is a compensation measure for a printing effect where holes tend to end up being printed smaller than intended. With this setting you can expand the size of vertical holes in your print. Similar to the ordinary [Horizontal Expansion](xy_offset.md) setting, your print's holes will be expanded in all directions.

Because the hole is expanded in all directions, this setting's value effectively applies to the radius of holes, not to their diameter.

![The holes in this print need to fit screws and axles, but they print too small](images/hole_xy_offset_0.png)
![The holes have been made larger, but the rest of the shape hasn't changed](images/hole_xy_offset.png)

Due to the viscosity of the material, when printing a line of plastic in a curve, the plastic tends to get dragged along with the nozzle in the curve. This makes the curve slightly smaller than intended as the string gets pulled into the inside of the curve. Normally this isn't really visible, but when printing items that need to fit very exactly or when printing items with very small vertical holes, this becomes ruinous to the accuracy of your print. Screws won't fit any more, pieces don't slide into each other neatly any more, and so on.

This setting compensates for that by making all holes slightly bigger. Unlike [Horizontal Expansion](xy_offset.md) this only affects closed holes though. If there is even a tiny opening on one side (horizontally, on the same layer) then that part won't be considered a hole and won't be affected by this setting.

A positive value will make the holes bigger. A negative value will make the holes smaller. When combined with Horizontal Expansion, the holes are expanded first before applying the ordinary horizontal expansion. This could cause thin pieces to disappear entirely before they are expanded by the ordinary horizontal expansion.

Note that this setting only looks at holes in the layers' plane. It only adjusts the size of holes on the top or bottom of the print. Holes on the side of the print are not adjusted. What's more, there are no restrictions on the size or shape of the hole. Any cavity that is completely surrounded by material on that layer will get expanded, even the inside of a container. Furthermore, this means that as soon as there is an opening on the side of such a container, the inside is no longer completely enclosed on those layers, and so they won't get expanded. This often results in a visible ridge on the inside of a container, exactly at the height of an opening on the side, where the inside is momentarily not expanded due to that opening.