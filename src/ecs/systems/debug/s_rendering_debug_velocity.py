import esper
import pygame

from src.engine.service_locator import ServiceLocator
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity

def system_rendering_debug_velocity(world:esper.World, screen:pygame.Surface):
    fnt = ServiceLocator.fonts_service.get("assets/fnt/PressStart2P.ttf", 6)
    debug_font:pygame.Surface = fnt.render("DEBUG_VIEW: VELOCITIES", False, pygame.Color(255, 100, 100))
    pos = pygame.Vector2(20, 20)
    screen.blit(debug_font, pos)

    components = world.get_components(CTransform, CVelocity)
    for _, (c_t, c_v) in components:
        font_surf:pygame.Surface = fnt.render(str(c_v.vel), False, pygame.Color(255,255,255))
        pos = c_t.pos - pygame.Vector2(font_surf.get_size())
        screen.blit(font_surf, pos)