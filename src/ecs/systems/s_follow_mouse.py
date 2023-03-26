import pygame
import esper

from src.ecs.components.editor.c_editor_follow_mouse import CEditorFollowMouse
from src.ecs.components.c_transform import CTransform

def system_follow_mouse(world:esper.World, mouse_pos:pygame.Vector2):
    components = world.get_components(CTransform, CEditorFollowMouse)
    for _, (c_t, _) in components:
        c_t.pos.x = mouse_pos.x
        c_t.pos.y = mouse_pos.y