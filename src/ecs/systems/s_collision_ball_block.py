import esper

from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_ball import CTagBall
from src.ecs.components.tags.c_tag_block import CTagBlock

def system_collision_ball_block(world: esper.World, delta_time:float):
    components_block = world.get_components(CSurface, CTransform, CTagBlock)
    components_ball = world.get_components(CSurface, CTransform, CVelocity, CTagBall)

    for block_ent, (c_s, c_t, _) in components_block:
        block_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
        for _, (c_b_s, c_b_t, c_b_v,  _) in components_ball:
            ball_rect = CSurface.get_area_relative(c_b_s.area, c_b_t.pos)
            if block_rect.colliderect(ball_rect):
                # Restauramos movimiento "hacia atras" para salir de la colision
                c_b_t.pos.y -= c_b_v.vel.y * delta_time
                c_b_t.pos.x -= c_b_v.vel.x * delta_time
                # Dependiendo del rectángulo de intersecion cambia la velocidad en X o Y
                clip = ball_rect.clip(block_rect)
                if clip.w > clip.h:
                    c_b_v.vel.y *= -1
                else:
                    c_b_v.vel.x *= -1

                world.delete_entity(block_ent)
                
