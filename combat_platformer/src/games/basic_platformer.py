#!/usr/bin/env python

import pygame
import rospkg
from simple_platformer.utilities import *
from simple_platformer.game_state_machine import *
from simple_platformer.levels import Platform
from combat_platformer.player import PlayerStateMachine
from combat_platformer.level import LevelBase
from combat_platformer.enemy import EnemyBase
from combat_platformer.enemy import EnemyStateMachine

class BasicPlatformer(object):
    
    def __init__(self):        
        
        # player 
        self.player = PlayerStateMachine()
        
        #level
        self.level = LevelBase()
        self.level.player = self.player
        self.screen = None
        self.proceed = True
        
        # enemys
        self.num_enemies = 3
        self.enemies_list = []
        for i in range(0,self.num_enemies):
            enemy = EnemyStateMachine()
            self.enemies_list.append(enemy)
        #endfor

    def exit(self):
        
        self.proceed = False      

        
    def load_resources(self):
        
        rospack = rospkg.RosPack()   
        background_file = rospack.get_path('simple_platformer') + \
        '/resources/backgrounds/cplusplus_programming_background_960x800.jpg'        
        
        return self.level.load_background(background_file) \
            and self.load_player_sprites()\
            and self.load_enemy_sprites()
    
    def load_player_sprites(self):
        rospack = rospkg.RosPack()
        sprites_list_file = rospack.get_path('simple_platformer') + '/resources/hiei_sprites/sprite_list.txt' 
        
          
        self.sprite_loader = SpriteLoader() 
        
        if self.sprite_loader.load_sets(sprites_list_file):
            print "Sprites successfully loaded"
        else:
            print "Sprites failed to load"
            return False
        
        #endif
        
        self.player.properties.collision_width = 42
        self.player.properties.collision_height = 75        
        if not self.player.setup():            
            return False        
        
        self.player.rect.center = (0,500)       

        
        keys = self.player.states_dict.keys()
        print "Adding player animation keys: " + str(keys)
        
        for key in keys:
            
            if (not self.player.add_animation_sets(key,self.sprite_loader.sprite_sets[key],
                                                    self.sprite_loader.sprite_sets[key].invert_set())) :
                print "Error loading animation for animation key %s"%(key)
                return False
            #endif
            
        #endfor
        
        print "Added all animation sprites"

        return True
    
    def load_enemy_sprites(self):
        rospack = rospkg.RosPack()
        sprite_list_file = rospack.get_path('simple_platformer') + '/resources/enemy_sprites/guardians_enemy17/sprite_list.txt'
        self.sprite_loader.sprite_sets.clear()
        
        if self.sprite_loader.load_sets(sprite_list_file):
            print "Enemy sprites successfully loaded"
        else:
            print "Enemy sprites failed to load"
            return False
        #endif
        
        keys = ['WALK', 'UNWARY','ALERT','DROP','WIPEOUT', 'STANDUP']
        positions = [(200,200), (400,50), (300,80)]
        counter = 0
        for enemy in self.enemies_list:
            
            
            enemy.target_player = self.player
            enemy.setup()
            enemy.rect.center= positions[counter]
            counter+=1
            for key in keys:
                if (not enemy.add_animation_sets(key,self.sprite_loader.sprite_sets[key].invert_set(),
                                                 self.sprite_loader.sprite_sets[key])):
                    print "Error loading animation sprites for key %s"%(key)
                    return False
                #endif
            #endfor            
            self.level.add_enemy(enemy)
            
            print "Added enemy animation keys: %s"%(str(keys))
        #endfor
        
        return True      
        
          
    def setup(self):
        
        if not self.load_resources():
            return False 
        

        
        if not self.level.setup():
            return False
            
        return True
    
    def step_game(self,elapsed_time):
        
        if (self.proceed and self.level.update(elapsed_time)):
            self.level.draw(self.screen)            

            return True
        
        else:
            return False
    
    def run(self):
        
        pygame.init()
        
        size = [ScreenProperties.SCREEN_WIDTH,ScreenProperties.SCREEN_HEIGHT]
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Don't mess with this dragon [x: jump , z: dash, <-: left, ->: right")        
        
        if not self.setup():
            print "setup failed"
            pygame.quit()
            return
        
        clock = pygame.time.Clock()
        while self.step_game(clock.get_time()):
            
            clock.tick(GameProperties.FRAME_RATE)                     
            pygame.display.flip()
       #endwhile     
            
        
        pygame.quit()
    
if __name__ == "__main__":
    
    game = BasicPlatformer()
    game.run()

        
        