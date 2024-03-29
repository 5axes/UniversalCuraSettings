Optimize Wall Printing Order
====
If this is enabled, Cura will spend some extra slicing time to optimise the order in which the walls are printed. The goal is to reduce the number of travel moves and retractions by printing walls that surround the same part after one another.


![Optimisation disabled](images/optimize_wall_printing_order_disabled.gif)
![Optimisation enabled](images/optimize_wall_printing_order_enabled.gif)

If this optimisation is enabled, the nozzle will print all the walls around one part first before moving to the next part, instead of printing all of the inner walls first before printing the outer walls. Optimising is usually positive, but with some parts it may impact dimensional accuracy because the previous wall hasn't solidified yet when placing down the next one next to it.

If the inner wall and the outer wall have greatly different flow rates, this optimisation also causes many more changes in flow rate. This manifests itself with a bigger [seam](../troubleshooting/seam.md) or some [blobs](../troubleshooting/blobs.md). The line width has a bigger impact on the print than this travel optimisation, so it's better to turn off the optimisation if this could be the problem in your print.