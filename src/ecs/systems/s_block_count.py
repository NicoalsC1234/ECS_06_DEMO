import esper

from src.ecs.components.tags.c_tag_block import CTagBlock

from src.engine.scenes.scene import Scene

def system_block_count(world: esper.World, scene:Scene):
    component_count = len(world.get_components(CTagBlock))
    if component_count <= 0:
        scene.switch_scene("WIN_SCENE")
            
