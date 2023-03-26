import pygame
import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_paddle import CTagPaddle

def system_screen_paddle(world: esper.World, screen_rect: pygame.Rect):
    components = world.get_components(CTransform, CSurface, CTagPaddle)
    for _, (c_t, c_s, _) in components:
        paddle_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
        if not screen_rect.contains(paddle_rect):
            paddle_rect.clamp_ip(screen_rect)
            c_t.pos.x = paddle_rect.x
            c_t.pos.y = paddle_rect.y
