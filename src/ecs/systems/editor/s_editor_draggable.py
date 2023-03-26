import pygame
import esper

from src.ecs.components.editor.c_editor_draggable import CEditorDraggable
from src.ecs.components.c_transform import CTransform

def system_editor_draggable(world:esper.World, mouse_pos:pygame.Vector2):
    components = world.get_components(CTransform, CEditorDraggable)
    for _, (c_t, c_d) in components:
        if c_d.is_dragging:
            c_t.pos.x = mouse_pos.x
            c_t.pos.y = mouse_pos.y