from enum import Enum
import json
import pygame

from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator

from src.create.prefab_creator_debug import create_debug_input, create_editor_placer
from src.create.prefab_creator_game import create_ball, create_block, create_game_input, create_paddle, create_play_field
from src.create.prefab_creator_interface import TextAlignment, create_text
from src.create.prefab_creator import create_enemy_spawner, create_input_player, create_player_square, create_bullet


from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform 
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.editor.c_editor_draggable import CEditorDraggable
from src.ecs.components.editor.c_editor_placer import CEditorPlacer
from src.ecs.components.tags.c_tag_ball import CTagBall
from src.ecs.components.tags.c_tag_block import CTagBlock
from src.ecs.components.tags.c_tag_paddle import CTagPaddle
from src.ecs.components.tags.c_tag_bullet import CTagBullet



from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_collision_enemy_bullet import system_collision_enemy_bullet
from src.ecs.systems.editor.s_editor_draggable import system_editor_draggable
from src.ecs.systems.s_enemy_count import system_enemy_count
from src.ecs.systems.s_collision_ball_block import system_collision_ball_block
from src.ecs.systems.s_collision_paddle_ball import system_collision_paddle_ball
from src.ecs.systems.s_follow_mouse import system_follow_mouse
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.debug.s_rendering_debug_rects import system_rendering_debug_rects
from src.ecs.systems.debug.s_rendering_debug_velocity import system_rendering_debug_velocity
from src.ecs.systems.s_screen_ball import system_screen_ball
from src.ecs.systems.s_screen_paddle import system_screen_paddle

from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_input_player import system_input_player
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_player import system_screen_player
from src.ecs.systems.s_screen_bullet import system_screen_bullet

from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_explosion_kill import system_explosion_kill
from src.ecs.systems.s_enemy_hunter_state import system_enemy_hunter_state
import src.engine.game_engine

class DebugView(Enum):
    NONE = 0
    RECTS = 1
    VELOCITY = 2

class PlayScene(Scene):
    def __init__(self, level_path:str, engine:'src.engine.game_engine.GameEngine') -> None:
        super().__init__(engine)
        self.level_path = level_path
        
        with open(level_path) as level_file:
            self.level_cfg = json.load(level_file)
        with open("assets/cfg/enemies.json") as enemies_file:
            self.enemies_cfg = json.load(enemies_file)
        with open("assets/cfg/level_01.json") as level_01_file:
            self.level_01_cfg = json.load(level_01_file)
        with open("assets/cfg/player.json") as player_file:
            self.player_cfg = json.load(player_file)
        with open("assets/cfg/bullet.json") as bullet_file:
            self.bullet_cfg = json.load(bullet_file)
        with open("assets/cfg/explosion.json") as explosion_file:
            self.explosion_cfg = json.load(explosion_file)
        
        self._paused = False
        self._debug_view = DebugView.NONE

    def do_create(self):
        # Recargar nivel, por si acaso estoy entrando 
        # y saliendo después de grabar
        with open(self.level_path) as level_file:
            self.level_cfg = json.load(level_file)

        create_text(self.ecs_world, "Press ESC to go back", 8, 
                    pygame.Color(50, 255, 50), pygame.Vector2(128, 20), 
                    TextAlignment.CENTER)

        self._player_entity = create_player_square(self.ecs_world, self.player_cfg, self.level_01_cfg["player_spawn"])
        self._player_c_v = self.ecs_world.component_for_entity(self._player_entity, CVelocity)
        self._player_c_t = self.ecs_world.component_for_entity(self._player_entity, CTransform)
        self._player_c_s = self.ecs_world.component_for_entity(self._player_entity, CSurface)

        create_enemy_spawner(self.ecs_world, self.level_01_cfg)
        create_input_player(self.ecs_world)
        
                
        paused_text_ent = create_text(self.ecs_world, "PAUSED", 16, 
                    pygame.Color(255, 50, 50), pygame.Vector2(128, 120), 
                    TextAlignment.CENTER)
        self.p_txt_s = self.ecs_world.component_for_entity(paused_text_ent, CSurface)
        self.p_txt_s.visible = self._paused

        create_game_input(self.ecs_world)
        create_debug_input(self.ecs_world)

        placer_entity = create_editor_placer(self.ecs_world)
        self.placer_s = self.ecs_world.component_for_entity(placer_entity, CSurface)
        self.placer_t = self.ecs_world.component_for_entity(placer_entity, CTransform)
        self.placer_ed = self.ecs_world.component_for_entity(placer_entity, CEditorPlacer)

        editor_text_entity = create_text(self.ecs_world, "EDITOR MODE - PRESS ENTER SO SAVE MAP AS editor_level.json", 6, 
                                         pygame.Color(255, 50, 50), pygame.Vector2(20, 50), TextAlignment.LEFT)
        self.editor_text_s = self.ecs_world.component_for_entity(editor_text_entity, CSurface)

        editor_text_saved_entity = create_text(self.ecs_world, "editor_level.json saved!", 6, 
                                         pygame.Color(255, 255, 50), pygame.Vector2(20, 70), TextAlignment.LEFT)
        self.editor_text_saved_s = self.ecs_world.component_for_entity(editor_text_saved_entity, CSurface)

        self.placer_s.visible = False
        self.editor_text_s.visible = False
        self.editor_text_saved_s.visible = False
    
    def do_update(self, delta_time: float):
        system_screen_player(self.ecs_world, self.screen_rect, self)
        system_screen_bullet(self.ecs_world, self.screen_rect)
        #system_enemy_count(self.ecs_world, self)
        
        if not self._paused:
            system_enemy_spawner(self.ecs_world, self.enemies_cfg, delta_time)
            system_movement(self.ecs_world, delta_time)
            system_collision_enemy_bullet(self.ecs_world, self.explosion_cfg)
            system_collision_player_enemy(self.ecs_world, self._player_entity,
                                      self.level_01_cfg, self.explosion_cfg)
            system_explosion_kill(self.ecs_world)
            system_player_state(self.ecs_world)
            system_enemy_hunter_state(self.ecs_world, self._player_entity, self.enemies_cfg["Enemy01"])
            system_enemy_hunter_state(self.ecs_world, self._player_entity, self.enemies_cfg["Enemy02"])
            system_enemy_hunter_state(self.ecs_world, self._player_entity, self.enemies_cfg["Enemy03"])
            system_animation(self.ecs_world, delta_time)
    
        
        self.ecs_world._clear_dead_entities()
        self.num_bullets = len(self.ecs_world.get_component(CTagBullet))

    def do_draw(self, screen):
        # Evaluar vistas de depurado y vistas normales
        if not self._debug_view == DebugView.RECTS:
            system_rendering(self.ecs_world, screen)
        else:
            system_rendering_debug_rects(self.ecs_world, screen)

        if self._debug_view == DebugView.VELOCITY:
            system_rendering_debug_velocity(self.ecs_world, screen)        

    def do_clean(self):
        self._debug_view = DebugView.NONE
        self._paused = False
        self._editor_mode = False

    def do_action(self, action: CInputCommand):
        if action.name == "PLAYER_LEFT":
            if action.phase == CommandPhase.START:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
            elif action.phase == CommandPhase.END:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
        if action.name == "PLAYER_RIGHT":
            if action.phase == CommandPhase.START:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
            elif action.phase == CommandPhase.END:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
        if action.name == "PLAYER_FIRE" and self.num_bullets < self.level_01_cfg["player_spawn"]["max_bullets"]:
            create_bullet(self.ecs_world, self._player_c_t.pos,
                          self._player_c_s.area.size, self.bullet_cfg)

        if action.name == "QUIT_TO_MENU" and action.phase == CommandPhase.START:
            self.switch_scene("MENU_SCENE")

        if action.name == "PAUSE" and action.phase == CommandPhase.START:
            self._paused = not self._paused
            self.p_txt_s.visible = self._paused

        if action.name == "TOGGLE_DEBUG_VIEW" and action.phase == CommandPhase.START:
            if self._debug_view == DebugView.NONE:
                self._debug_view = DebugView.RECTS
            elif self._debug_view == DebugView.RECTS:
                self._debug_view = DebugView.VELOCITY
            elif self._debug_view == DebugView.VELOCITY:
                self._debug_view = DebugView.NONE

    

