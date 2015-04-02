**bnsim** is a Simple Boolean Network simulator that implements background chatter -noise at the input levels- and quenched -frozen- chatter.

# Installation instructions #
Download and unzip the bnsim archive `bnsim-0.1.tar.gz`
**bnsim** is ready to run.

# User-specified settings #
The executable file bnsim needs 4 parameters to run:
  * `-r <filename>.rules`:  rules file. This file defines the nodes and logic rules of the boolean network
  * `-c <filename>.condis`: simulation conditions file. This file defines the simulation conditions of the network.
    * Parameter `Num_New_Iterations`: defines the number of iterations to perform.
    * Parameter `<node>*`: defines the update rule of input node `<node>`.The current implementation of bnsim accepts two types of input node:
      * Periodic inputs are specificed by:  `<node>* Sequence <periodic sequence> <error probability>`. For example:
```
A* = Sequence 111000 0.0
```
> > > See also example 2.
      * Chatter inputs are specificed by: `<node>* Sequence <one-digit default value> <error probability>`. For example:
```
A* = Sequence 0 0.50
```
> > > See also example 3.
  * `-s <filename>.states`: states file. This file defines the initial values of the network nodes, given in the same order as the node names given in the hash-commented line.
  * `-o <filename>.out`: output file. This file defines the location and name of the output file. The output file is formatted such that there is one hash-commented initial row with node information, followed by one row of states values per iteration.