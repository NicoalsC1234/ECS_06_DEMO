from enum import Enum
import json
import pygame

from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator

from src.create.prefab_creator_debug import create_debug_input, create_editor_placer
from src.create.prefab_creator_game import create_ball, create_block, create_game_input, create_paddle, create_play_field
from src.create.prefab_creator_interface import TextAlignment, create_text

from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform 
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.editor.c_editor_draggable import CEditorDraggable
from src.ecs.components.editor.c_editor_placer import CEditorPlacer
from src.ecs.components.tags.c_tag_ball import CTagBall
from src.ecs.components.tags.c_tag_block import CTagBlock
from src.ecs.components.tags.c_tag_paddle import CTagPaddle

from src.ecs.systems.editor.s_editor_draggable import system_editor_draggable
from src.ecs.systems.s_block_count import system_block_count
from src.ecs.systems.s_collision_ball_block import system_collision_ball_block
from src.ecs.systems.s_collision_paddle_ball import system_collision_paddle_ball
from src.ecs.systems.s_follow_mouse import system_follow_mouse
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.debug.s_rendering_debug_rects import system_rendering_debug_rects
from src.ecs.systems.debug.s_rendering_debug_velocity import system_rendering_debug_velocity
from src.ecs.systems.s_screen_ball import system_screen_ball
from src.ecs.systems.s_screen_paddle import system_screen_paddle
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
        with open("assets/cfg/paddle.json") as paddle_file:
            self.paddle_cfg = json.load(paddle_file)
        with open("assets/cfg/ball.json") as ball_file:
            self.ball_cfg = json.load(ball_file)
        with open("assets/cfg/blocks.json") as blocks_file:
            self.blocks_cfg = json.load(blocks_file)
        with open("assets/cfg/editor_cursor.json") as editor_cursor_file:
            self.editor_cursor_cfg = json.load(editor_cursor_file)
        
        self._paddle_ent = -1
        self._paused = False
        self._debug_view = DebugView.NONE
        self._mouse_pos:pygame.Vector2 = pygame.Vector2(0, 0)
        self._editor_mode = False

    def do_create(self):
        # Recargar nivel, por si acaso estoy entrando 
        # y saliendo después de grabar
        with open(self.level_path) as level_file:
            self.level_cfg = json.load(level_file)

        create_text(self.ecs_world, "Press ESC to go back", 8, 
                    pygame.Color(50, 255, 50), pygame.Vector2(320, 20), 
                    TextAlignment.CENTER)
        
        ball_ent = create_ball(self.ecs_world, 
                               self.ball_cfg, 
                               self.level_cfg["ball_start"])
        self._b_t = self.ecs_world.component_for_entity(ball_ent, CTransform)

        create_play_field(self.ecs_world, 
                          self.level_cfg["blocks_field"], 
                          self.blocks_cfg)
        
        paddle_ent = create_paddle(self.ecs_world, 
                                   self.paddle_cfg, 
                                   self.level_cfg["paddle_start"])
        self._p_v = self.ecs_world.component_for_entity(paddle_ent, CVelocity)
        self._p_t = self.ecs_world.component_for_entity(paddle_ent, CTransform)
                
        paused_text_ent = create_text(self.ecs_world, "PAUSED", 16, 
                    pygame.Color(255, 50, 50), pygame.Vector2(320, 180), 
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
        system_screen_paddle(self.ecs_world, self.screen_rect)
        system_screen_ball(self.ecs_world, self.screen_rect, self)
        system_block_count(self.ecs_world, self)
        
        if not self._paused:
            system_movement(self.ecs_world, delta_time)
            system_collision_ball_block(self.ecs_world, delta_time)
            system_collision_paddle_ball(self.ecs_world, self.ball_cfg["velocity"])
        
        if self._editor_mode:
            system_follow_mouse(self.ecs_world, self._mouse_pos)
            system_editor_draggable(self.ecs_world, self._mouse_pos)

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
        if action.name == "LEFT":
            if action.phase == CommandPhase.START:
                self._p_v.vel.x -= self.paddle_cfg["input_velocity"]
            elif action.phase == CommandPhase.END:
                self._p_v.vel.x += self.paddle_cfg["input_velocity"]
        elif action.name == "RIGHT":
            if action.phase == CommandPhase.START:
                self._p_v.vel.x += self.paddle_cfg["input_velocity"]
            elif action.phase == CommandPhase.END:
                self._p_v.vel.x -= self.paddle_cfg["input_velocity"]

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

        if action.name == "TOGGLE_EDITOR" and action.phase == CommandPhase.START:
            self._editor_mode = not self._editor_mode
            self.placer_s.visible = self._editor_mode
            self.editor_text_s.visible = self._editor_mode
            if self._editor_mode:
                self._b_t.pos.x = self.level_cfg["ball_start"]["pos"]["x"]
                self._b_t.pos.y = self.level_cfg["ball_start"]["pos"]["y"]
                self._p_t.pos.x = self.level_cfg["paddle_start"]["pos"]["x"]
                self._p_t.pos.y = self.level_cfg["paddle_start"]["pos"]["y"]
                self._paused = True
                self.p_txt_s.visible = self._paused

        if self._editor_mode:
            self._do_editor_action(action)
    
    def _do_editor_action(self, action: CInputCommand):
        if action.name == "MOUSE_MOVE":
            self._mouse_pos = action.mouse_pos

        if action.name == "DRAG_BLOCK":
            b_type = self.placer_ed.types[self.placer_ed.curr_type_idx]
            if b_type is None:
                if action.phase == CommandPhase.START:
                    components = self.ecs_world.get_components(CTransform, CSurface, CEditorDraggable)
                    for _, (c_t, c_s, c_d) in components:
                        surf_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
                        placer_rect = CSurface.get_area_relative(self.placer_s.area, self.placer_t.pos)
                        if surf_rect.colliderect(placer_rect):
                            c_d.is_dragging = True
                else:
                    components = self.ecs_world.get_component(CEditorDraggable)
                    for _, c_d in components:
                        c_d.is_dragging = False
                self.editor_text_saved_s.visible = False
        
        if action.name == "CHANGE_ENTITY" and action.phase == CommandPhase.START:
            self.placer_ed.curr_type_idx += 1
            self.placer_ed.curr_type_idx %= len(self.placer_ed.types)
            b_type = self.placer_ed.types[self.placer_ed.curr_type_idx]
            if b_type is not None:
                self.placer_s.surf = ServiceLocator.images_service.get(self.blocks_cfg[b_type]["image"])
                self.placer_s.area = self.placer_s.surf.get_rect()
            else:
                self.placer_s.surf = pygame.Surface((self.editor_cursor_cfg["size"]["x"],
                                                     self.editor_cursor_cfg["size"]["y"]))
                self.placer_s.surf.fill(pygame.Color(self.editor_cursor_cfg["color"]["r"],
                                                     self.editor_cursor_cfg["color"]["g"],
                                                     self.editor_cursor_cfg["color"]["b"]))
                self.placer_s.area = self.placer_s.surf.get_rect()
            self.editor_text_saved_s.visible = False
        
        if action.name == "PLACE_ENTITY" and action.phase == CommandPhase.START:
            b_type = self.placer_ed.types[self.placer_ed.curr_type_idx]
            if b_type is not None:
                create_block(self.ecs_world, 
                             b_type,
                             self.blocks_cfg[b_type], 
                             self._mouse_pos - pygame.Vector2(1,1))
            self.editor_text_saved_s.visible = False
        
        if action.name == "DELETE_ENTITY" and action.phase == CommandPhase.START:
            components = self.ecs_world.get_components(CTransform, CSurface, CEditorDraggable)
            for ent, (c_t, c_s, c_d) in components:
                surf_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
                placer_rect = CSurface.get_area_relative(self.placer_s.area, self.placer_t.pos)
                if surf_rect.colliderect(placer_rect):
                    self.ecs_world.delete_entity(ent)
            self.editor_text_saved_s.visible = False
        
        if action.name == "SAVE_LEVEL" and action.phase == CommandPhase.START:
            level = {}
            components = self.ecs_world.get_components(CTransform, CTagBall)
            for ent, (c_t, _) in components:
                level["ball_start"] = {}
                level["ball_start"]["pos"] = {}
                level["ball_start"]["pos"]["x"] = c_t.pos.x
                level["ball_start"]["pos"]["y"] = c_t.pos.y

            components = self.ecs_world.get_components(CTransform, CTagPaddle)
            for ent, (c_t, _) in components:
                level["paddle_start"] = {}
                level["paddle_start"]["pos"] = {}
                level["paddle_start"]["pos"]["x"] = c_t.pos.x
                level["paddle_start"]["pos"]["y"] = c_t.pos.y

            level["blocks_field"] = []
            components = self.ecs_world.get_components(CTransform, CTagBlock)
            for ent, (c_t, c_b) in components:
                block = {}
                block["type"] = c_b.b_type
                block["pos"] = {}
                block["pos"]["x"] = c_t.pos.x
                block["pos"]["y"] = c_t.pos.y
                level["blocks_field"].append(block)
            
            with open("assets/cfg/editor_level.json", "w") as write_file:
                json.dump(level, write_file, indent=4)
            
            self.editor_text_saved_s.visible = True


