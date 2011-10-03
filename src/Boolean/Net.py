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

import os.path
from random import random,shuffle,sample
import numpy
from scipy.stats.distributions import *
import Node

class Net:
    """
    Basic class defining network properties and methods
    """
    
    # Properties
    Nodes = dict()    # dictionary of nodes
    Iteration = None
    Output_Nodes = [] 
    __Names_In_Rules = []
    
    # Constructor
    def __init__(self, Rules_File=None,
                 States_File=None,method=None,):
        self.Iteration = 0
        
        if os.path.isfile(Rules_File):
            self.Load_Rules(Rules_File,method)
        else:
            print "Error: No rules file found"
            exit()            
        if os.path.isfile(States_File):
            self.Load_States(States_File)                                                    
        else:
            print "Error: No states file found"
            exit()           
        
        return

    # Methods
        
    def Load_Rules(self, File,method):    
        Language = ['(',')','not', 'and', 'or','in',',','True', 'False']
        Lines = open(File,'r').readlines()
        Node_Count = 0
        Names_In_Rules = []
        for Line in Lines:
            if "*" in Line:
                (name,equal,logic_string) = Line.rpartition("=")                
                Name = name.replace("*","").strip()

                if logic_string.strip() == "None":
                    Command = "def Logic(n):\n    return n.Nodes['%s'].State[n.Iteration]" % Name
                else:
                    Logic_Splitted = logic_string.replace('(', ' ( ').replace(')',' ) ').replace(',',' , ').split()
                    Logic_Rewritten = []
                    for e in Logic_Splitted:
                        if e in Language:
                            Logic_Rewritten.append(e)
                        else:
                            Names_In_Rules.append(e)
                            if method=='Asynchronous':
                               Logic_Rewritten.append("n.Nodes['%s'].State[n.Iteration+1]"%e)
                            elif method=='Semi_Asynchronous':
                               Logic_Rewritten.append("n.Nodes['%s']._Aux_State"%e)
                            else:
                               Logic_Rewritten.append("n.Nodes['%s'].State[n.Iteration]"%e)
                    Command = "def Logic(n):\n    return %s" % ' '.join(Logic_Rewritten)
                exec Command
                self.Nodes[Name] = Node.Node(Node_Count, Name, Logic)
                Node_Count += 1
        self.__Names_In_Rules = set(Names_In_Rules)
        Names_With_No_Rules = self.__Names_In_Rules.difference(self.Nodes.keys() + ['None']) 
        if len(Names_With_No_Rules) > 0:
            print "Some node rules lacking:"
            print Names_With_No_Rules
            exit()
        self.Output_Nodes = set(self.Nodes.keys()).difference(self.__Names_In_Rules)
        return
    
    def Load_States(self, File):
        Lines = open(File,'r').readlines()
        # NDP: cannot rely on a fixed number of commented lines!
        # self.Iteration = len(Lines)-2
        # self.Names = Lines[0].replace('#','').split()
        count = 0
        for Line in Lines[0:]:
          if Line.startswith('# NODES'):
            self.Names = Line.replace('# NODES',' ').strip().split(' ')            
          if not Line.startswith('#'):  
            self.Iteration = count
            for Name, Value in zip(self.Names, list(Line.strip())):
                self.Nodes[Name].State.append(Value=='1')
            count = count + 1
    
    def Simulate(self, Conditions_File):
        if os.path.isfile(Conditions_File):    
            self.Load_Conditions(Conditions_File) 
            for i in range(self.Iteration,self.Iteration+self.Num_New_Iterations):
                for node in self.Nodes.values():
                    node.State[self.Iteration+1] = node.Logic(self)
                self.Iteration += 1
           
    def Simulate_Asynchronous(self, Conditions_File):
        if os.path.isfile(Conditions_File):    
            self.Load_Conditions(Conditions_File) 
            for i in range(self.Iteration,self.Iteration+self.Num_New_Iterations):
                # AJPR: First I fill the nodes at t+1 with states at t
                # as we change the state due to the operations
                # the new asynchronous value is filled at t+1
                for node in self.Nodes.values():
                    node.State[self.Iteration+1] = node.State[self.Iteration]
                New_Nodes=list(self.Nodes.values())
                shuffle(New_Nodes)
                for node in New_Nodes:
                    node.State[self.Iteration+1] = node.Logic(self)
                self.Iteration += 1

    def Simulate_Semi_Asynchronous(self, Conditions_File):
        if os.path.isfile(Conditions_File):    
            self.Load_Conditions(Conditions_File)
            N=len(self.Nodes)
            for i in range(self.Iteration,self.Iteration+self.Num_New_Iterations):
                # PR: Save the state of current iteration
                nodes = self.Nodes.values()
                for node in nodes:
                    node._Aux_State = node.State[self.Iteration]
                Is_Early = numpy.random.rand(N)>0.95
                for iNode,node in enumerate(nodes):
                    if Is_Early[iNode]:
                        node.State[self.Iteration+1] = node.Logic(self)
                    else:
                        node.State[self.Iteration+1] =  node.State[self.Iteration]
                for node in nodes:
                    node._Aux_State = node.State[self.Iteration+1]
                for iNode,node in enumerate(nodes):
                    if Is_Early[iNode]:
                        node.State[self.Iteration+1] = node._Aux_State
                    else:
                        node.State[self.Iteration+1] = node.Logic(self)
                self.Iteration += 1
                print self.Iteration,self.Num_New_Iterations

    def Load_Conditions(self, File):
        Lines = open(File,'r').readlines()
        for line in Lines[1:]:
                if not line.startswith("#"): 
                    (Name,Equals,Value) = line.rpartition("=")                      
                    if "*" not in line:  
                        Name=Name.strip().replace('_',' ').title().replace(' ', '_')
                        try: 
                            setattr(self,Name,int(Value)) 
                        except:
                            print "Wrong assignment in simulation conditions:" + Name
                            exit() 
                    else:
                        Name=Name.replace("*","").strip()
                        Func_Name, Space, Func_Args_Str = Value.strip().partition(' ')
                        Func_Args = ["'%s'" % Arg for Arg in Func_Args_Str.split()]
                        Func_String = "__%s(self, Name, %s)" %(Func_Name, ','.join(Func_Args))                    
                        Command = "Logic = %s" % Func_String
                        exec Command
                        self.Nodes[Name].Logic = Logic
        self.Set_States_Length()            
                            
    def Set_States_Length(self):
        for node in self.Nodes.values():
            node.State = node.State + ( self.Num_New_Iterations * [None] )
    
    def Save(self, Output_File):
        """ Saves the entire network """
        if os.path.isfile(Output_File):
            print "Warning: file " + Output_File + " already exists"
        fout = open(Output_File,'a')
        print >> fout, "# NODES " + ' '.join(self.Names)
        # AJPR: print output using node name order defined in states file:   
        for i in range(self.Iteration):
            print >> fout, ''.join(['1' if self.Nodes[name].State[i] else '0' for name in self.Names])
        fout.close()

    def Save_Requested_Nodes(self, Output_File, Requested_Nodes):
        """ Saves requested nodes only: """
        if os.path.isfile(Output_File):
            print "Warning: file " + Output_File + " already exists"
        Requested_Nodes_List=Requested_Nodes.replace('\'','').split(';')
        fout = open(Output_File,'a')
        print >> fout, "# NODES " + ' '.join(Requested_Nodes_List)
        # AJPR: print output using node name order defined in Requested_Nodes:   
        for i in range(self.Iteration):
            print >> fout, ''.join(['1' if self.Nodes[name].State[i] else '0' for name in Requested_Nodes_List])
        fout.close()

    def States_To_List(self,states_flag):
        states_list = []
        if states_flag == 'all':
            for i in range(self.Iteration):
                states_list.append(''.join(['1' if self.Nodes[name].State[i] else '0' for name in self.Names]))
        if states_flag == 'output_nodes':
            for i in range(self.Iteration):
                output_nodes = ['Akt','Erk','Rac','Cdc42']
                states_list.append(''.join(['1' if self.Nodes[name].State[i] else '0' for name in output_nodes]))                
        return states_list      


# Internal functions:
def __Sequence(n, Name, Seq, Error = 0):
    Logic_Sequence = [s=='1' for s in Seq]
    Seq_Length = len(Seq)
    Error = float(Error)
    if Error == 0:
        def Logic_Function(n):
            Index = n.Iteration % Seq_Length
            Output = Logic_Sequence[Index]
            return Output
    else:
        def Logic_Function(n):
            Index = n.Iteration % Seq_Length 
            Output = Logic_Sequence[Index]
            r = random()
            if r < Error:
                Output = not Output
            return Output
    return Logic_Function

def __Quenched(n, Name, Error = 0):
    Error=float(Error)
    def Logic_Function(n):
        if n.Iteration==0:
            r = random()
            return (r < Error)
        else:
            return n.Nodes[Name].State[1]
    return Logic_Function

def __SineSequence(n,Name,Amplitude,Period,Phase = 0):
  def Logic_Function(n):
    Arg = float(Phase) + 2 * numpy.pi/float(Period) * n.Iteration
    Prob = 0.5 * (float(Amplitude) * numpy.sin(Arg) + 1.)
    return bernoulli.rvs(Prob,size=1)
  return Logic_Function
  
def __AmpSineSequence(n,Name,Amplitude,Period,Phase = 0):
  Amplitude = float(Amplitude)
  Phase = float(Phase)
  Period = float(Period)
  def Logic_Function(n):
    Arg = Phase + 2 * numpy.pi/Period * n.Iteration
    Prob = Amplitude * 0.5 * ( 1 + numpy.sin(Arg))
    return bernoulli.rvs(Prob,size=1)
  return Logic_Function  
  
def __RelSineSequence(n,Name,RelAmplitude,Period,Chatter,Phase=0):
  Chatter = float(Chatter)
  Amplitude = float(RelAmplitude)*min([Chatter,1-Chatter])
  Phase = float(Phase)
  Period = float(Period)
  def Logic_Function(n):
    Arg = Phase + 2 * numpy.pi/Period * n.Iteration
    Prob = Amplitude * numpy.sin(Arg) + Chatter
    return bernoulli.rvs(Prob,size=1)
  return Logic_Function    

def __RandomON(n, Name, PercentON):
    PercentON = float(PercentON)
    def Logic_Function(n):
        r = random()
        Output = (r < PercentON)
        return Output
    return Logic_Function


