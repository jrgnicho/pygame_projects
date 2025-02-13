from panda3d.core import Vec3
from panda3d.bullet import BulletPersistentManifold
from panda3d.bullet import BulletManifoldPoint
from collections import namedtuple
from platformer_core.game_object import GameObject
from platformer_core.state_machine import *

class CharacterStateData(object):
  
  CollisionPoints = namedtuple("CollisionPoints", "manifolds on_self on_collided")
  
  class ContactData(object):
    
    def __init__(self,object_id, top = None , bottom = None , left = None, right = None): 
      '''
      ContactData(BulletPersistentManifold top = None ,BulletPersistentManifold bottom = None ,
                    BulletPersistentManifold left = None ,BulletPersistentManifold right = None)
                    
      Stores contact data from BulletPersistentManifold objects in a convenient manner
      '''
      empty = CharacterStateData.CollisionPoints(manifolds = None,on_self = [],on_collided = [])
      
      # hold list of BulletManifoldPoint
      self.object_id = object_id
      self.points_bottom = empty if bottom is None else CharacterStateData.ContactData.createCollisionPoints(object_id,bottom)
      self.points_top = empty if top is None else CharacterStateData.ContactData.createCollisionPoints(object_id,top)
      self.points_left = empty if left is None else CharacterStateData.ContactData.createCollisionPoints(object_id,left)
      self.points_right = empty if right is None else CharacterStateData.ContactData.createCollisionPoints(object_id,right)
      
    @staticmethod  
    def createCollisionPoints(object_id,contact_manifold):
      collided_is_b = contact_manifold.getNode0().getPythonTag(GameObject.ID_PYTHON_TAG) != object_id
      points_on_self = []
      points_on_collided = []
      manifolds = contact_manifold.getManifoldPoints()
      for cp in manifolds:          
        if collided_is_b:
          points_on_self.append(cp.getPositionWorldOnA())
          points_on_collided.append(cp.getPositionWorldOnB())
        else:
          points_on_self.append(cp.getPositionWorldOnB())
          points_on_collided.append(cp.getPositionWorldOnA())

      collision_points = CharacterStateData.CollisionPoints(manifolds = manifolds,on_self = points_on_self, on_collided = points_on_collided)
      return collision_points
      
    def clear(self):
      empty = CharacterStateData.CollisionPoints(manifolds = None,on_self = [],on_collided = [])
      self.points_bottom = empty 
      self.points_top = empty
      self.points_left = empty
      self.points_right = empty      
  
  
  def __init__(self):
    
    self.health = 100
    self.friction_enabled = False
    self.momentum = Vec3(0,0,0)
    self.velocity = Vec3(0,0,0)
    self.platform = None # Last platform that the character touched.
    self.ledge = None # Last ledge that the player came into contact with.
    self.contact_data = CharacterStateData.ContactData('') # contact data from last collision
    self.air_jumps_count = 0
    self.air_dashes_count = 0
