# -*- coding: utf-8 -*-
#    Copyright (C) 2011 Nuria Domedel-Puig, Antonio J. Pons-Rivero, Pau Rué and
#    Jordi Garcia-Ojalvo
#
#    Created: 2011-09-27 by Nuria Domedel-Puig, Antonio J. Pons-Rivero and Pau Rué 
#
#    This file is part of bnsim.
#
#    bnsim is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    bnsim is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with bnsim.  If not, see <http://www.gnu.org/licenses/>.

class Node:
    """
    Class defining the Network node properties
    """

    # Properties
    Name=""       # node name
    Index=None    # node numbering
    State=None    # list of states over time
    Logic=None    # function defining the update
    
    # Constructor:
    def __init__(self,Index,Name,Logic):
        self.Index=Index
        self.Name=Name
        self.State=[]
        self.Logic=Logic
        return
    
    # Set input function 
    def SetInput(self,rule):
        print rule
        return

