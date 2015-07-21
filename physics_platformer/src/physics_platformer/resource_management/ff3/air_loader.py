from physics_platformer.geometry2d import Box2D
from physics_platformer.animation import AnimationElement, AnimationAction
import re
from construct import *
import os
import logging

  
class AIRLoader(object):
  
  __EXTENSION__ = ".air"
  __ANIMATION_NAME__ = '^; (.*)'
  __BEGIN_HEADER__ = '\[Begin Action ([0-9]+)\]'
  __BOX_INFO__ = '(-?[0-9]+), '*3 +  '(-?[0-9]+)' # left, top, right, bottom (x+ from left to right and y+ from top to bottom)
  __COLLISION_BOX_STATIC_LIST__ = 'Clsn2Default: ([1-9]+)'
  __COLLISION_BOX_LIST__ = 'Clsn2: ([1-9]+)'
  __COLLISION_BOX_ENTRY__ = 'Clsn2\[([0-9]+)\] = '
  __HIT_BOX_LIST__ = 'Clsn1: ([1-9]+)'
  __HIT_BOX_ENTRY__ = 'Clsn1\[([0-9]+)\] = '
  __SPRITE_ENTRY__ = '[,| ]*([0-9]+)'*5 #  group, sprite_no, offsetx, offsety, time(framerate) -> 50,1, 0,0, 6
  
  def __init__(self):
    self.animations_ = []
    self.groups_ = []
  
  @property
  def animations(self):
    return self.animations_    
  
  @property
  def groups(self):
    return self.groups_
  
  def load(self,filename):
    
    # openning file
    if not ( os.path.exists(filename) and filename.endswith(AIRLoader.__EXTENSION__)):
      logging.error("File %s is invalid"%(filename))
      return False
    
    f = open(filename,'r')
    lines = f.readlines()
    
    self.animations_ = []    
    linecount = 0    
    anim_action = None
    anim_elmt = None
    
    while linecount < len(lines):   
      
      line = lines[linecount]      
      linecount+=1     
      
      m = re.search(AIRLoader.__ANIMATION_NAME__,line)
      if m is not None: # new animation found
        
        # save current animation
        if anim_action is not None:
          
          # compute average framerate
          for elmt in anim_action.animation_elements:
            anim_action.framerate += elmt.game_ticks
            
          anim_action.framerate /= len(anim_action.animation_elements)
          
          self.animations_.append(anim_action)
        
        anim_name = m.group(1)  
        anim_action = AnimationAction(anim_name)
        anim_elmt = AnimationElement()
        
        
        # finding begin header   
        line = lines[linecount]      
        linecount+=1           
        m = re.search(AIRLoader.__BEGIN_HEADER__,line)
        if m is not None: # animation header found
          anim_id  = int(m.group(1))
          anim_action.id = anim_id
        else:
          logging.error("Animation header was not found");
          return False       
        
        continue    
      
      
      # find Default Collision Boxes "Clsn2Default"
      m = re.search(AIRLoader.__COLLISION_BOX_STATIC_LIST__,line)
      if m is not None:
        box_count = int(m.group(1))              
        box_list,linecount = self.__parseCollisionBoxList__(lines, linecount)   
        
        if len(box_list) != box_count:
          logging.error("Size of static box (Clsn2Default) list is incorrect, expected %i and got %i"%(box_count,len(box_list)))    
          return False
        
        anim_action.rigid_body_boxes = box_list
        continue
        
      # find Hit Boxes
      m = re.search(AIRLoader.__HIT_BOX_LIST__,line)
      if m is not None:
        box_count = int(m.group(1))
        box_list,linecount = self.__parseHitBoxList__(lines, linecount)
        
        if (len(box_list) != box_count ) :
          logging.error("Size of hit box (Clsn1) list is incorrect, expected %i and got %i"%(box_count,len(box_list)))  
          return False  
                
        anim_elmt.hit_boxes = box_list    
        continue     

        
      # find Collision Boxes
      m = re.search(AIRLoader.__COLLISION_BOX_LIST__,line)
      if m is not None:
        box_count = int(m.group(1))
        box_list,linecount = self.__parseCollisionBoxList__(lines, linecount)
        
        if (len(box_list) != box_count ) :
          logging.error("Size of collision box (Clsn2) list is incorrect")
          return False
                
        anim_elmt.collision_boxes = box_list
        continue
        
      # find parent sprite
      sprite_entry = self.__parseSpriteEntry__(line)
      if sprite_entry is not None:
      
        anim_elmt.group_no = sprite_entry[0]
        anim_elmt.im_no = sprite_entry[1]
        anim_elmt.game_ticks = sprite_entry[4]
        
        # save animation element
        anim_action.animation_elements.append(anim_elmt)
        anim_elmt = AnimationElement()
        
        continue
      
    # collecting all groups
    for anim in self.animations_:
      for elmt in anim.animation_elements:
        if self.groups_.count(elmt.group_no)== 0:
          self.groups_.append(elmt.group_no)
          
    return True
        
        
  def __parseCollisionBoxList__(self,lines,linecount):
    return self.__parseBoxList__(AIRLoader.__COLLISION_BOX_ENTRY__, lines, linecount)
  
  def __parseHitBoxList__(self,lines,linecount):    
    return self.__parseBoxList__(AIRLoader.__HIT_BOX_ENTRY__, lines, linecount)
      
  def __parseBoxList__(self,token_expr,lines,linecount):
    
    proceed = True
    box_list = []
    
    while proceed:
      line = lines[linecount]
      m = re.search(token_expr,line)
      
      if m is None:
        proceed = False
        break
      
      # parsing box coordinates
      start = m.end()
      b = re.search(AIRLoader.__BOX_INFO__,line[start:])
      
      if b is None:
        logging.error("Failed to parse box info from line: %s"%(line[start:]))
        proceed = False
        break
      
      left = float(b.group(1))
      top = -float(b.group(2))
      right = float(b.group(3))
      bottom = -float(b.group(4))
      
      w = abs(right - left)
      h = abs(top - bottom)
      cx = left + w*0.5
      cy = bottom + h*0.5
      
      box = Box2D(w,h,(cx,cy))
      box_list.append(box)
      linecount+=1      
      proceed = True
      
    return (box_list,linecount)
  
  def __parseSpriteEntry__(self,line):
    
    group_no = 0
    im_no = 0
    offsetx = 0
    offsety = 0
    delay = 0
    
    m = re.search(AIRLoader.__SPRITE_ENTRY__,line)
    if m is None:
      return None
    
    group_no = int(m.group(1))
    im_no = int(m.group(2))
    offsetx = int(m.group(3))
    offsety = int(m.group(4))
    delay = int(m.group(5))
    
    return (group_no,im_no,offsetx,offsety,delay)
    
         
      
      
      