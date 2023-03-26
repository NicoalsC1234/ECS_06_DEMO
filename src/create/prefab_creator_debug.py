import pygame
import esper
from src.create.prefab_creator import create_square
from src.ecs.components.editor.c_editor_follow_mouse import CEditorFollowMouse

from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_surface import CSurface
from src.ecs.components.editor.c_editor_placer import CEditorPlacer

def create_debug_input(world:esper.World):
    switch_debug_view = world.create_entity()
    world.add_component(switch_debug_view,
                        CInputCommand("TOGGLE_DEBUG_VIEW", 
                                      pygame.K_LCTRL))
    switch_editor_mode = world.create_entity()
    world.add_component(switch_editor_mode,
                        CInputCommand("TOGGLE_EDITOR", 
                                      pygame.K_TAB))
    mouse_move = world.create_entity()
    world.add_component(mouse_move,
                        CInputCommand("MOUSE_MOVE", 
                                      pygame.MOUSEMOTION))
    mouse_down_left = world.create_entity()
    world.add_component(mouse_down_left,
                        CInputCommand("DRAG_BLOCK", 
                                      pygame.BUTTON_LEFT))
    
    place_entity = world.create_entity()
    world.add_component(place_entity,
                        CInputCommand("PLACE_ENTITY", 
                                      pygame.BUTTON_LEFT))
    
    mouse_change_entity = world.create_entity()
    world.add_component(mouse_change_entity,
                        CInputCommand("CHANGE_ENTITY", 
                                      pygame.BUTTON_RIGHT))
    
    mouse_delete_entity = world.create_entity()
    world.add_component(mouse_delete_entity,
                        CInputCommand("DELETE_ENTITY", 
                                      pygame.BUTTON_MIDDLE))
    
    save_level_action = world.create_entity()
    world.add_component(save_level_action,
                        CInputCommand("SAVE_LEVEL", 
                                      pygame.K_RETURN))
    
def create_editor_placer(world:esper.World):
    placer_entity = create_square(world,
                                  pygame.Vector2(10, 10),
                                  pygame.Color(0, 255, 0),
                                  pygame.Vector2(0,0),
                                  pygame.Vector2(0,0))
    placer_s = world.component_for_entity(placer_entity, CSurface)
    placer_s.visible = False
    world.add_component(placer_entity,
                        CEditorFollowMouse())
    world.add_component(placer_entity,
                        CEditorPlacer([None, "B1", "B2", "B3", "B4", "B5", "B6"]))
    return placer_entity
    