from panda3d.core import LColor
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import TransformState
from panda3d.core import BitMask32
from panda3d.core import NodePath
from panda3d.core import PandaNode
from panda3d.core import PNMImage, PNMImageHeader, Filename
from panda3d.core import SequenceNode
from panda3d.core import CardMaker
from panda3d.core import Texture
from panda3d.core import TextureStage
from panda3d.core import TransparencyAttrib
import logging

class SpriteAnimator(PandaNode):
    PANDA_TAG = 'PandaNodeSubclass'
    
    class PlayMode(object):
        
        STOPPED = -1
        PLAYING = 0
        LOOPING = 1
        PAUSED = 2
        
        ALLOWED_MODES = [STOPPED,
                         PLAYING,
                         LOOPING,
                         PAUSED]
    
    def __init__(self,name):
        
        PandaNode.__init__(self,name) 
        PandaNode.setPythonTag(self,SpriteAnimator.PANDA_TAG,self)       
        self.seq_left_ = None
        self.seq_right_ = None
        self.facing_right_ = True
        self.size_ = (0,0) # (horizontal_scale, vertical_scale
        self.play_mode_ = SpriteAnimator.PlayMode.STOPPED
    
    
    def loadImages(self,images_right, images_left,frame_rate, scale = 1.0):   
        """
        loadImages
            Loads the images for the right and left side of the sprite animation
            Inputs:
             - images_right: List containing PNMImage objects for tanimating the character when it is facing right.
             - images_left:  List containing PNMImage objects for animating the character when it is facing left.
             - frame_rate: Rate in hz at which the images will be played.
             - scale: ratio in units/pixels that will be used to set the size of the card geometry that holds the image.
                 Thus the card dimensions will be equal to (width_image*scale , height_image*scale)
        """
        
        if (len(images_right) == 0) or (len(images_left) == 0):
            print "ERROR: Found empty image list"
            return False
    
        # storing individual sprite size
        w = images_right[0].getXSize() # assumes that all images in the in 'images' array are the same size
        h = images_right[0].getYSize()
        self.size_ = (w,h) # image size in pixels
    
        self.seq_right_ = self.createSequenceNode(self.getName() + '-right-seq',images_right,scale,frame_rate)
        self.seq_left_ = self.createSequenceNode(self.getName()+ '-left-seq',images_left,scale,frame_rate)
        self.addStashed(self.seq_right_)
        self.addStashed(self.seq_left_)
    
        self.faceRight(True)      
    
        return True
    
    def createSequenceNode(self,name,images,scale,frame_rate):
    
        seq = SequenceNode(name)
        w = images[0].getXSize() # assumes that all images in the in 'images' array are the same size
        h = images[0].getYSize()       
        cw = w*scale
        ch = h*scale 
        
        for i in range(0,len(images)):
            
            img = images[i]
            #sprite_img = PNMImage(w,h)
            #sprite_img.addAlpha()
            #sprite_img.alphaFill(0)
            #sprite_img.fill(1,1,1)
            #sprite_img.copySubImage(img ,0 ,0 ,0 ,0,w ,h)
            
            # Load the image onto the texture
            texture = Texture()        
            texture.setXSize(w)
            texture.setYSize(h)
            texture.setZSize(1)    
            texture.load(img)
            texture.setWrapU(Texture.WM_border_color) # gets rid of odd black edges around image
            texture.setWrapV(Texture.WM_border_color)
            texture.setBorderColor(LColor(0,0,0,0))
            
            # creating CardMaker to hold the texture
            cm = CardMaker(name +    str(i))
            cm.setFrame(-0.5*cw,0.5*cw,-0.5*ch,0.5*ch)
            card = NodePath(cm.generate())            
            card.setTexture(texture)
            seq.addChild(card.node(),i)
         
        seq.setFrameRate(frame_rate)   
        print "Sequence Node %s contains %i imagese of size %s and card size of %s"%(name,seq.getNumFrames(),str((w,h)),str((cw,ch)))        
        return seq 
    
    def isFacingRight(self):
        return self.facing_right_
    
    def faceRight(self,face_right):

        
        if face_right: 
            
            self.seq_left_.stop()
            self.stashChild(self.seq_left_)            
            self.unstashChild(self.seq_right_) 
    
        else:
            self.seq_right_.stop()
            self.stashChild(self.seq_right_)
            self.unstashChild(self.seq_left_)  
    
        self.facing_right_ = face_right  
        self.setPlayMode(self.play_mode_)  
        
    def getSelectedNode(self):
        """
        Returns the active NodePath containing the active SequenceNode (either left or right)
        """
        return self.seq_right_ if self.facing_right_ else self.seq_left_
    
    def play(self):        
        self.getSelectedNode().play()
        self.play_mode_ = SpriteAnimator.PlayMode.PLAYING
        
    def loop(self,restart = True):        
        self.getSelectedNode().loop(restart)
        self.play_mode_ = SpriteAnimator.PlayMode.LOOPING
        
    def stop(self):
        self.getSelectedNode().stop()
        self.play_mode_ = SpriteAnimator.PlayMode.STOPPED
        
    def pose(self,frame):
        self.getSelectedNode().pose(frame)
        
    def setPlayMode(self,mode):
        
        if SpriteAnimator.PlayMode.ALLOWED_MODES.count(mode) > 0:
            
            if SpriteAnimator.PlayMode.STOPPED:
                self.stop()
                
            if SpriteAnimator.PlayMode.PLAYING:
                self.play()
                
            if SpriteAnimator.PlayMode.LOOPING:
                self.loop()
            
        else:
            return False
        
        return True
    
    def getFrameRate(self):
        return self.getSelectedNode().getFrameRate()

        
    def getNumFrames(self):
        return self.getSelectedNode().getNumFrames()

    def getFrame(self):
        return self.getSelectedNode().getFrame()