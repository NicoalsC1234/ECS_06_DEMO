import pygame
import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.engine.scenes.scene import Scene



def system_screen_player(world: esper.World, screen_rect: pygame.Rect, scene:Scene):
    components = world.get_components(CTransform, CVelocity, CSurface, CTagPlayer)
    for _, (c_t, c_v, c_s, c_e) in components:
        player_rect = c_s.area.copy()
        player_rect.topleft = c_t.pos
        if not screen_rect.contains(player_rect):
            player_rect.clamp_ip(screen_rect)
            c_t.pos.xy = player_rect.topleft

        if player_rect.left < 0 or player_rect.right > screen_rect.width:
            c_v.vel.x *= -1
            player_rect.clamp_ip(screen_rect)
            c_t.pos.x = player_rect.x

        if player_rect.top < 0:
            c_v.vel.y *= -1
            player_rect.clamp_ip(screen_rect)
            c_t.pos.y = player_rect.y
        
        if  player_rect.bottom > screen_rect.height:
            scene.switch_scene("GAME_OVER_SCENE")
