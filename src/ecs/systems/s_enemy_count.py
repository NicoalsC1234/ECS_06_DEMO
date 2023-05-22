import esper

from src.ecs.components.tags.c_tag_enemy import CTagEnemy

from src.engine.scenes.scene import Scene

def system_enemy_count(world: esper.World, scene:Scene):
    component_count = len(world.get_components(CTagEnemy))
    if component_count <= 0:
        scene.switch_scene("WIN_SCENE")
            
