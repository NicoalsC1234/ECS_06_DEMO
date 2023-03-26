import esper
import pygame

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_ball import CTagBall
from src.engine.scenes.scene import Scene

def system_screen_ball(world: esper.World, screen_rect: pygame.Rect, scene:Scene):
    components = world.get_components(CTransform, CVelocity, CSurface, CTagBall)
    for _, (c_t, c_v, c_s, c_e) in components:
        cuad_rect = c_s.area.copy()
        cuad_rect.topleft = c_t.pos
        if cuad_rect.left < 0 or cuad_rect.right > screen_rect.width:
            c_v.vel.x *= -1
            cuad_rect.clamp_ip(screen_rect)
            c_t.pos.x = cuad_rect.x

        if cuad_rect.top < 0:
            c_v.vel.y *= -1
            cuad_rect.clamp_ip(screen_rect)
            c_t.pos.y = cuad_rect.y
        
        if  cuad_rect.bottom > screen_rect.height:
            scene.switch_scene("GAME_OVER_SCENE")
