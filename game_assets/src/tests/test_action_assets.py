#!/usr/bin/env python

import pygame
from game_assets.object_assets import *
from game_assets.object_assets import ActionAssets
from game_assets.object_assets import AssetSet
from game_assets.serialization import AssetCollectionXml

def create_action_asset():
    
    player_assets = ActionAssets()
    print 'Default action assets object %s'%(str(player_assets))
    
    attack_assets = AttackAssets()
    print 'Default attack assets object %s'%(str(attack_assets))
    
def create_asset_collection_xml():
    
    asset_set = AssetSet()
    action_assets = ActionAssets()
    collection_writer = AssetCollectionXml()
    
    # first rectangle
    num_rects = 4
    rect = pygame.Rect(0,0,10,20)
    for i in range(0,4):
        
        r = rect.copy();
        r.x+=i*num_rects
        action_assets.collision.rectangles.append(r)

    #endfor
    
    # adding action asset to set
    asset_set.actions_assets_dict['TEST_ACTION'] = action_assets
    
    # saving to xml
    collection_writer.save([asset_set],'test_asset_collection.xml')   
    
    
    
if __name__ == '__main__':
    
    create_action_asset()
    create_asset_collection_xml()

    