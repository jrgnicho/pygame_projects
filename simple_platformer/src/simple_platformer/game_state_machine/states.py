import sys
    
class State(object):
    
    def __init__(self,state_key,entry_cb = None,exit_cb = None):
        
        self.key = state_key
        self.actions = {} # dictionary of actions (keys) and their corresponding callbacks
        self.entry_callback= entry_cb
        self.exit_callback = exit_cb
        
    def set_entry_callback(self,entry_cb):
        
        self.entry_callback = entry_cb
        
    def set_exit_callback(self,exit_cb):
        
        self.exit_callback = exit_cb        
        
    def add_action(self,action_key,
                       action_cb = lambda: sys.stdout.write("No action callback\n")):
                        # ,condition_cb = lambda: True):
        """
        Adds supported action to the state
        
        Inputs:
        - action_key: action key for the action that can be executed during this state
        - action_cb: method that is invoked when this action is requested through the execute() method.
        """
        self.actions[action_key] = action_cb
        
    def has_action(self,action_key):
        
        return self.actions.has_key(action_key)
        
    def execute(self,action_key,action_cb_args=()):
        """
            Invokes the callback corresponding to this action upon entering this state.  
            
            Inputs:
            - action_key: action to be executed.
            - action_cb_args: tuple containing optional arguments to the registered action_callback
            Outputs:
            - Succeeded: True when action is registered within state.  False otherwise
                    
        """
        
        if self.actions.has_key(action_key):
            
            action_cb = self.actions[action_key]
            action_cb(*action_cb_args)
            #condition_cb = action_tuple[1]
            return True
        else:
            #print "State %s does not support %s action"%(self.key,action_key)
            return False
        
    def enter(self):
        
        if self.entry_callback != None:
            self.entry_callback()
        
    def exit(self):
        
        if self.exit_callback != None:
            self.exit_callback()
        
class StateMachine(object):
    
    def __init__(self):
        
        self.states_dict={}
        self.active_state_key = None
        self.transitions={}
        self.action_queue = [] # list of an action, arguments tuple 
        #self.enter = self.execute  # will be called when used as a sub state machine        

        
    def add_state(self,state_obj):
        
        if not self.states_dict.has_key(state_obj.key):
            self.states_dict[state_obj.key] = state_obj
        else:
            self.states_dict[state_obj.key] = state_obj
            print "State was already registered in state machine, new entry will now replace it"

    def add_transition(self,state_obj,action_key,next_state_key,condition_cb = lambda: True):
        
        # inserting as active state if None is currently selected
        if self.active_state_key == None:
            self.active_state_key = state_obj.key            
            
        if self.states_dict.has_key(state_obj.key): 
            
            # transition rules for the state           
            transition_dict = self.transitions[state_obj.key]   
            
            # add (next_state_key,condition_callback) tuple to the list
            if transition_dict.has_key(action_key):
                action_list = transition_dict[action_key]
                action_list.append( (next_state_key,condition_cb))
              
            # create new list for all transitions supported for this action
            # at this state  
            else:
                action_list = [(next_state_key,condition_cb)]
                transition_dict[action_key] = action_list
                
            #endif    
            
        else:       
            self.states_dict[state_obj.key] = state_obj
            self.transitions[state_obj.key] = {action_key:[(next_state_key,condition_cb)]}  
        
        #endif
            
        print "Added transition rule : From %s state : %s action : To %s state"%(state_obj.key,action_key,next_state_key)  
           
        
    def execute(self,action_key,action_cb_args=()):
        
        
        if self.transitions.has_key(self.active_state_key):            
            transition_dict = self.transitions[self.active_state_key]
            
            # check if valid transition
            if transition_dict.has_key(action_key):               

                
                # execute action on active state
                active_state_obj = self.states_dict[self.active_state_key]               
                if active_state_obj.has_action(action_key):
                    active_state_obj.execute(action_key,action_cb_args)
                
                #endif
                
                # go through each rule defined for this action and return true on the first one that validates
                action_list = transition_dict[action_key]  
                
                for action_tuple in action_list:
                    
                    state_key = action_tuple[0]
                    condition_cb = action_tuple[1]
                
                    # examine condition
                    if condition_cb():
                        next_state_obj = self.states_dict[state_key]                       
                        
                        
                        # exiting active state
                        active_state_obj.exit()
                        
                        # entering new state                        
                        next_state_obj.enter()
                        
                        # setting next state as active
                        self.active_state_key = state_key
                        
                        print "Transition from state [%s] : through action [%s] : to state [%s]"%(active_state_obj.key,
                                                                          action_key,
                                                                          self.active_state_key)
                        
                        # calling state enter routine
                        if next_state_obj.execute(action_key,action_cb_args):
                            
                            # transition succeeded

                            return True
                        
                        else: 
                            
                            # reverting upon failure
                            #self.active_state_key = active_state_obj.key                            
                            #print "Transition failed, reverted to state %s from state %s"%(self.active_state_key,state_key)
                            return False                 
                    
                        #endif
                    
                    else: # condition evaluation failed
                        
                        continue
                
                    #endif
                    
                #endfor                
                
            else:
                
                # no transition for this action, check if current state supports action
                active_state_obj = self.states_dict[self.active_state_key]
                if (active_state_obj.has_action(action_key) and 
                    active_state_obj.execute(action_key,action_cb_args)):
                    
                    # executed supported action under current state
                    return True
                else:
                
                    #print "Transition for the %s action at the state %s not supported"%(action_key,self.active_state_key)
                    return False
                #endif
                
            #endif
            
        else:
            print "Transitions from the state %s have not been defined"%(self.active_state_key)
            return False
        
        #endif
        
        return True
    
class SubStateMachine(StateMachine):
    
    class ActionKeys(object):
        
        START_SM = 'START_SM'
        STOP_SM = 'STOP_SM'
        
        
    class StateKeys(object):
        
        START = 'START'
        STOP = 'STOP'
        
        
    class StartState(State):
        
        def __init__(self,parent_sm):
            
            State.__init__(self,SubStateMachine.StateKeys.START)
            self.parent_sm = parent_sm
            
        def enter(self):    
            print "SM START state enter method invoked"        
            self.parent_sm.start()
            
            
    class StopState(State):
        
        def __init__(self,parent_sm):
            
            State.__init__(self,SubStateMachine.StateKeys.STOP)
            self.parent_sm = parent_sm
            
        def enter(self):   
            print 'SM STOP state enter method invoked'         
            self.parent_sm.stop()
            
    
    def __init__(self,key,parent_state_machine):
        StateMachine.__init__(self)
        
        self.key = key
        self.parent_sm = parent_state_machine
        self.start_state = SubStateMachine.StartState(self)
        self.stop_state = SubStateMachine.StopState(self)    
        
    def has_action(self,action_key):
        
        #print "SM at state %s has not action %s"%(self.active_state_key,action_key)
        active_state_obj = self.states_dict[self.active_state_key]
        
        if self.active_state_key == SubStateMachine.StateKeys.START:
            self.start()
            return False
        else:
           return active_state_obj.has_action(action_key)
        #endif 
        
        
    def start(self):
        
        self.execute(SubStateMachine.ActionKeys.START_SM)  
            
    def stop(self):
        
        self.active_state_key = self.start_state.key
        self.parent_sm.execute(SubStateMachine.ActionKeys.STOP_SM)
        
    def enter(self):
        
        active_state_obj = self.states_dict[self.active_state_key]
        active_state_obj.enter()
        
        
    def exit(self):
        active_state_obj = self.states_dict[self.active_state_key]
        active_state_obj.exit()
        self.active_state_key = self.start_state.key
        
    
        
        
        
    
        
    
        