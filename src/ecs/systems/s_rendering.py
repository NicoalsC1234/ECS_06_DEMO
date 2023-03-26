import esper
import pygame

from src.ecs.components.c_changing_text import CChangingText
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface

def system_rendering(world:esper.World, screen:pygame.Surface):    
    components = world.get_components(CTransform, CSurface)
    for ent, (c_t, c_s) in components:
        if not c_s.visible:
            continue
        
        # Special case for changing text, needs to redo the surface all the time
        if world.has_component(ent, CChangingText):
            c_txt = world.component_for_entity(ent, CChangingText)
            c_s.surf = c_txt.font.render(c_txt.text, True, c_s.color)
        screen.blit(c_s.surf, c_t.pos, area=c_s.area)    