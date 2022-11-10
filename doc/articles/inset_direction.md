Wall Ordering
====
This setting determines which walls are printed first, printing them from the outside in, or from the inside out.


![The inner wall is printed first](images/outer_inset_first_disabled.gif)
![The outer wall is printed first](images/outer_inset_first_enabled.gif)

This setting has a small effect on quality as well as dimensional accuracy:
* Printing from outside inwards will improve dimensional accuracy. Adjacent walls generally push each other a bit, especially if the wall line width is smaller than the nozzle size. The wall that gets printed first will have been solidified and then doesn't get pushed as much. Therefore printing the outer wall first will make your outer wall be in a more accurate location.
* If the infill is printed before the walls, printing from the outside in will reduce how much the infill shows through on the surface. Otherwise the infill is printed first, then the inner walls which get pushed outwards by the infill, and then the outer wall which gets pushed outwards by the inner walls. As a result, a pattern could be visible on the outside. If the outer wall is printed first, the outer wall can solidify before the inner wall is able to push on it.
* Printing from the inside out is better for overhang. The outer wall is further removed from the previous layer than the inner wall. When printing the outer wall first, the outer wall has nothing yet to grab on to. When the inner wall is printed first, the outer wall can attach sideways to the outer wall.

When there is an odd number of walls, the wall in the centre will always be printed last.