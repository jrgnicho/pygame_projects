import pygame
from simple_platformer.game_state_machine import State
from simple_platformer.game_state_machine import SubStateMachine
from combat_platformer.player.action_keys import PlayerActionKeys
from combat_platformer.level.action_keys import LevelActionKeys
from combat_platformer.enemy import EnemyProperties
from combat_platformer.enemy import EnemyBase

class StateKeys(object):
    
    PATROL = 'PATROL'
    ALERT='ALERT'
    CHASE='CHASE'
    RUN = 'RUN'
    WALK = 'WALK'
    JUMP='JUMP'
    NAP='NAP'
    
    
class BasicState(State):
    
    LA = LevelActionKeys
    PA = PlayerActionKeys
    
    
    def __init__(self,key,character):
        
        State.__init__(self,key)
        self.character = character  
        
    def setup(self,assets):
        
        print "setup method for state %s is unimplemented"%(self.key)    


        
class RunState(BasicState):
    
    def __init__(self,character):
        
        BasicState.__init__(self,StateKeys.RUN,self.character)        
        self.speed = 0 
        
    def enter(self):
                 
        self.character.set_current_animation_key(StateKeys.RUN)
        
    def setup(self,assets):
        
        self.speed = self.character.properties.run_speed
        self.add_action(BasicState.LA.STEP_GAME, lambda : self.update())   
        
    def update(self):
        pass
        
class JumpState(BasicState):
    
    def __init__(self,character):
        
        BasicState.__init__(self,StateKeys.JUMP,character)        
              
        self.has_landed = False
                      
        
    def setup(self,asset):
        
        self.speed = self.character.properties.jump_speed 
        
        self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update())  
        self.add_action(BasicState.LA.APPLY_GRAVITY,lambda g: self.character.apply_gravity(g))    
        self.add_action(BasicState.LA.COLLISION_ABOVE,lambda platform : self.character.set_vertical_speed(0))
        self.add_action(BasicState.LA.COLLISION_RIGHT_WALL,lambda platform : self.character.set_momentum(0))
        self.add_action(BasicState.LA.COLLISION_LEFT_WALL,lambda platform : self.character.set_momentum(0)) 

    def update(self):
        pass
    
    def enter(self):        
        
        self.character.set_vertical_speed(self.speed)
        self.character.set_current_animation_key(StateKeys.JUMPING)
        self.character.midair_dash_countdown = self.character.properties.max_midair_dashes
        self.character.range_collision_group.add(self.range_sprite) 
        
    def exit(self):
        self.character.range_collision_group.remove(self.range_sprite)      
        self.has_landed = False
        
class AlertState(BasicState):
    
    def __init__(self,character):
        BasicState.__init__(self,StateKeys.ALERT,character) 
        
        self.time_consumed= False
        
    def setup(self,assets):
        
        self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update(time_elapsed))
        
    def update(self,time_elapsed):
        pass
        
    
class PatrolState(SubStateMachine):
    
    class WalkState(BasicState):
    
        def __init__(self,character):
            
            BasicState.__init__(self,StateKeys.WALK,self.character)      
              
            self.speed = 0 
            self.patrol_rect = None
            self.time_active = 10
            self.time_left = 10
            self.time_consumed = False
            self.player_sighted = False
            
              
            self.sight_sprite = pygame.sprite.Sprite()
            self.range_sprite = pygame.sprite.Sprite()              
            
            self.add_action(BasicState.LA.STEP_GAME, lambda time_elapsed: self.update(time_elapsed))    
            self.add_action(BasicState.LA.COLLISION_RIGHT_WALL, lambda platforms : self.turn_around())
            self.add_action(BasicState.LA.COLLISION_LEFT_WALL, lambda platforms : self.turn_around())
            self.add_action(BasicState.LA.PLAYER_IN_RANGE,
                            lambda player,range_sprites : self.check_player_insight(player,range_sprites))
            
        def enter(self):
                     
            self.time_left = self.time_active
            self.time_consumed = False
                    
            self.character.set_current_animation_key(StateKeys.WALK)
            self.character.range_collision_group.add(self.range_sprite)
            self.character.range_collision_group.add(self.sight_sprite)
            
        def exit(self):
            self.character.range_collision_group.remove(self.range_sprite)
            self.character.range_collision_group.remove(self.sight_sprite)
            
        def setup(self,assets):
            
            self.speed = self.character.properties.walk_speed  
            self.patrol_rect  = self.character.properties.patrol_area_rect
            self.time_active = self.character.properties.patrol_walk_time
            
            # sight sprite
            pr = self.character.collision_sprite.rect
            self.sight_sprite.rect = pygame.Rect(0,0,200,100) 
            self.sight_sprite.offset = (0,(pr.height - self.sight_sprite.rect.height)/2)
            
            # range sprite
            self.range_height_extension = 4
            self.range_sprite.rect = self.character.collision_sprite.rect.copy()
            self.range_sprite.rect.height = self.range_sprite.rect.height + self.range_height_extension
            self.range_sprite.offset = (0,0)
            
        def turn_around(self):
            
            if self.character.facing_right:
                self.character.turn_left(self.speed)
            else:
                self.character.turn_right(self.speed)
            #endif
            
        def is_inside_patrol_area(self):
            
            ps = self.character.collision_sprite
            
            return (ps.rect.left > self.patrol_rect.left) or \
                (ps.rect.right < self.patrol_rect.right)  
                
        def check_player_insight(self,player,range_sprites):
            
            cs = self.character.collision_sprite
            ps = player.collision_sprite
            for sp in range_sprites:
                
                if sp == self.sight_sprite:                    
                    if self.character.facing_right and (self.rect.centerx < ps.rect.centerx):
                        self.player_sighted = True
                    
                    elif self.character.facing_left and (self.rect.centerx > ps.rect.centerx):
                        self.player_sighted = True
                        
                    #endif
                    
                    break
                
                #endif
            #endfor                   

            
        def update(self,time_elapsed):
            
            # update time counter
            self.time_left -= time_elapsed
            
            if self.is_inside_patrol_area(self):
                
                # check active time
                if self.time_left <= 0:
                    self.time_consumed = True
                #endif
                
            else:                
                self.turn_around()
            
            #endif
            
    class NapState(BasicState):
        
        def __init__(self,character):
            
            BasicState.__init__(self,StateKeys.NAP,self.character)
            
            self.time_active = 10
            self.time_left = 10 
            self.time_consumed = False
            
        def enter(self):      
            
            self.time_left = self.time_active
            self.time_consumed = False   
        
        def setup(self,assets):
            
            self.time_active = self.character.properties.patrol_nap_time
            
        def update(self,time_elapsed):
            
            self.time_left -= time_elapsed
            if self.time_left <= 0:
                
                self.time_consumed = True
            #endif                
    
    
    def __init__(self,parent_sm,character):
        
        SubStateMachine.__init__(self,StateKeys.PATROL ,parent_sm)
        self.character = character
        
    def setup(self,assets):
        
        self.create_transition_rules()   
        
        # invoking setup method for each state
        for state in self.states_dict.values():
            state.setup(assets)
        #endfor
        
    def create_transition_rules(self):
        
        self.walk_state = self.WalkState(self,self.character)
        self.nap_state = self.NapState(self,self.character)
        
        # transitions
        self.add_transition(self.start_state, self.ActionKeys.ENTER, self.walk_state)
        
        self.add_transition(self.walk_state, BasicState.LA.STEP_GAME, self.nap_state, self.walk_state.time_consumed)
        self.add_transition(self.walk_state, BasicState.LA.STEP_GAME, self.stop_state, self.walk_state.player_sighted)
        
        self.add_transition(self.nap_state, BasicState.LA.STEP_GAME, self.walk_state, self.nap_state.time_consumed)
        