import math
import pygame
import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_ball import CTagBall
from src.ecs.components.tags.c_tag_paddle import CTagPaddle

def system_collision_paddle_ball(world: esper.World, ball_speed:float):
    components_paddle = world.get_components(CSurface, CTransform, CTagPaddle)
    components_ball = world.get_components(CSurface, CTransform, CVelocity, CTagBall)

    for _, (c_s, c_t, _) in components_paddle:
        paddle_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
        for _, (c_b_s, c_b_t, c_b_v, _) in components_ball:
            ball_rect = CSurface.get_area_relative(c_b_s.area, c_b_t.pos)
            if paddle_rect.colliderect(ball_rect):
                if ball_rect.y < paddle_rect.y:
                    # ¿Cómo determinar a que angulo sale de vuelta?
                    # https://www.youtube.com/watch?v=QIbQ3jJDBw8
                    dist = ball_rect.centerx - paddle_rect.centerx
                    ball_range = (dist / paddle_rect.w) * 2
                    ball_range = pygame.math.clamp(ball_range, -1, 1)
                    # Entre -135 y -45 grados
                    angle = (-math.pi/2) + (ball_range * math.pi/4)
                    # Velocidad final dado el angulo
                    c_b_v.vel.x = math.cos(angle) * ball_speed
                    c_b_v.vel.y = math.sin(angle) * ball_speed
