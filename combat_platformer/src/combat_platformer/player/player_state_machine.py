from simple_platformer.game_state_machine import *
from simple_platformer.animatable_object import *
from combat_platformer.player.basic_states import *
from combat_platformer.player.action_keys import *
from combat_platformer.player import PlayerBase

AK = PlayerActionKeys
class PlayerStateMachine(StateMachine,PlayerBase):
    
    def __init__(self):
    
        # superclass constructors
        PlayerBase.__init__(self)
        StateMachine.__init__(self)
        
        # registering handler
        self.add_event_handler(AnimatableObject.Events.ANIMATION_SEQUENCE_COMPLETED,self.action_sequence_expired_handler)
        
        
    def setup(self):
        
        self.create_transition_rules()        
        return True
        
    def action_sequence_expired_handler(self):
            self.execute(AK.ACTION_SEQUENCE_EXPIRED)
            
            
    def create_transition_rules(self):
        
        run_state = RunningState(self)
        dash_state = DashState(self)
        midair_dash_state = MidairDashState(self)
        dash_breaking_state = DashBreakingState(self)
        stand_state = StandState(self)
        stand_edge_state = StandOnEdgeState(self)
        jump_state = JumpState(self)
        fall_state = FallState(self)
        land_state = LandState(self)
        hanging_state = HangingState(self)
        climbing_state = ClimbingState(self)
        
        
        # transitions
        sm = self
        
        sm.add_transition(run_state,AK.CANCEL_MOVE,PlayerStateMachine.StateKeys.STANDING)
        sm.add_transition(run_state,AK.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(run_state,AK.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(run_state,AK.DASH,PlayerStateMachine.StateKeys.DASHING)
        sm.add_transition(run_state,AK.MOVE_LEFT,PlayerStateMachine.StateKeys.DASH_BREAKING,
                          lambda: self.momentum > 0)
        sm.add_transition(run_state,AK.MOVE_RIGHT,PlayerStateMachine.StateKeys.DASH_BREAKING,
                          lambda: self.momentum < 0)
        
        
        sm.add_transition(dash_state,AK.CANCEL_DASH,PlayerStateMachine.StateKeys.DASH_BREAKING,
                          lambda: self.animation_set_progress_percentage()>0.2)
        sm.add_transition(dash_state,AK.CANCEL_DASH,PlayerStateMachine.StateKeys.RUNNING,
                          lambda: not (self.animation_set_progress_percentage()>0.2))
        sm.add_transition(dash_state,AK.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(dash_state,AK.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(dash_state,AK.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.RUNNING)
        
        
        sm.add_transition(midair_dash_state,AK.CANCEL_DASH,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(midair_dash_state,AK.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.FALLING)
        
        sm.add_transition(dash_breaking_state,AK.MOVE_LEFT,PlayerStateMachine.StateKeys.RUNNING,
                          lambda: not self.facing_right)
        sm.add_transition(dash_breaking_state,AK.MOVE_RIGHT,PlayerStateMachine.StateKeys.RUNNING,
                          lambda: self.facing_right)
        sm.add_transition(dash_breaking_state,AK.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(dash_breaking_state,AK.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(dash_breaking_state,AK.STEP_GAME,PlayerStateMachine.StateKeys.STANDING,
                          lambda: self.momentum == 0)
        
        
        sm.add_transition(stand_state,AK.RUN,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_state,AK.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(stand_state,AK.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(stand_state,AK.MOVE_LEFT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_state,AK.MOVE_RIGHT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_state,AK.DASH,PlayerStateMachine.StateKeys.DASHING)
        sm.add_transition(stand_state,AK.PLATFORMS_IN_RANGE,PlayerStateMachine.StateKeys.STANDING_ON_EDGE,
                          lambda: stand_state.is_standing_on_edge)
        sm.add_transition(stand_state,AK.PLATFORMS_IN_RANGE,PlayerStateMachine.StateKeys.FALLING,
                  lambda: stand_state.is_beyond_edge)
        
        
        sm.add_transition(stand_edge_state,AK.RUN,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,AK.JUMP,PlayerStateMachine.StateKeys.JUMPING)
        sm.add_transition(stand_edge_state,AK.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(stand_edge_state,AK.MOVE_LEFT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,AK.MOVE_RIGHT,PlayerStateMachine.StateKeys.RUNNING)
        sm.add_transition(stand_edge_state,AK.DASH,PlayerStateMachine.StateKeys.DASHING)
        
        sm.add_transition(jump_state,AK.DASH,PlayerStateMachine.StateKeys.MIDAIR_DASHING,
                          lambda: self.midair_dash_countdown > 0)
        sm.add_transition(jump_state,AK.LAND,PlayerStateMachine.StateKeys.LANDING)
        sm.add_transition(jump_state,AK.COLLISION_BELOW,PlayerStateMachine.StateKeys.LANDING,
                          lambda : jump_state.has_landed)
        sm.add_transition(jump_state,AK.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(jump_state,AK.COLLISION_ABOVE,PlayerStateMachine.StateKeys.FALLING)
        sm.add_transition(jump_state,AK.PLATFORMS_IN_RANGE,PlayerStateMachine.StateKeys.HANGING,
                          lambda : jump_state.edge_in_reach)
        
        sm.add_transition(fall_state,AK.DASH,PlayerStateMachine.StateKeys.MIDAIR_DASHING,
                          lambda: self.midair_dash_countdown > 0)
        sm.add_transition(fall_state,AK.LAND,PlayerStateMachine.StateKeys.LANDING)
        sm.add_transition(fall_state,AK.COLLISION_BELOW,PlayerStateMachine.StateKeys.LANDING,
                          lambda : fall_state.has_landed)
        sm.add_transition(fall_state,AK.PLATFORMS_IN_RANGE,PlayerStateMachine.StateKeys.HANGING,
                          lambda : fall_state.edge_in_reach)
        
        sm.add_transition(hanging_state,AK.JUMP,PlayerStateMachine.StateKeys.JUMPING,
                          lambda : self.animation_set_progress_percentage()>0.2) 
        sm.add_transition(hanging_state,AK.MOVE_UP,PlayerStateMachine.StateKeys.CLIMBING,
                          lambda : self.animation_set_progress_percentage()>=1) 
        
        sm.add_transition(climbing_state,AK.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.STANDING) 
        
        
        sm.add_transition(land_state,AK.ACTION_SEQUENCE_EXPIRED,PlayerStateMachine.StateKeys.STANDING)  
        sm.add_transition(land_state,AK.JUMP,PlayerStateMachine.StateKeys.JUMPING,
                          lambda : self.animation_set_progress_percentage()>0.2)  
        sm.add_transition(land_state,AK.DASH,PlayerStateMachine.StateKeys.DASHING,
                          lambda : self.animation_set_progress_percentage()>0.2)
        sm.add_transition(land_state,AK.PLATFORM_LOST,PlayerStateMachine.StateKeys.FALLING) 