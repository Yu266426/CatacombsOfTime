import enum

import pygame
import pygbase
import pygbase.ui.text

from data.modules.base.constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from data.modules.base.utils import get_tile_pos, draw_rect_outline
from data.modules.editor.actions.editor_actions import EditorActionQueue
from data.modules.editor.editor_selection_info import TileSelectionInfo
from data.modules.editor.editor_states.editor_state import EditorState, EditorStates
from data.modules.editor.shared_editor_state import SharedEditorState
from data.modules.editor.tools.editor_tool import EditorTool
from data.modules.editor.tools.tile_tools.tile_draw_tool import TileDrawTool
from data.modules.editor.tools.tile_tools.tile_fill_tool import TileFillTool
from data.modules.level.room import EditorRoom


class TileTools(enum.Enum):
	DRAW = enum.auto()
	FILL = enum.auto()


class TileDrawState(EditorState):
	def __init__(self, room: EditorRoom, shared_state: SharedEditorState, action_queue: EditorActionQueue, tile_selection_info: TileSelectionInfo):
		super().__init__(room, shared_state, action_queue)

		self.tile_selection_info = tile_selection_info

		self.current_tool: TileTools = TileTools.DRAW
		self.tools: dict[TileTools, EditorTool] = {
			TileTools.DRAW: TileDrawTool(self._room, self._shared_state, self._action_queue),
			TileTools.FILL: TileFillTool(self._room, self._shared_state, self._action_queue)
		}

		self.tiled_mouse_pos = get_tile_pos(self._shared_state.camera_controller.world_mouse_pos, (TILE_SIZE, TILE_SIZE))

		self.layer_text = pygbase.ui.text.Text((SCREEN_WIDTH - 10, 7), "arial", 60, (200, 200, 200), text="1", use_sys=True, alignment=pygbase.UIAlignment.TOP_RIGHT)

		self.tool_highlight_index = 0

		self.ui = pygbase.UIManager()

		self.button_frame = self.ui.add_frame(pygbase.Frame((pygbase.UIValue(0), pygbase.UIValue(SCREEN_HEIGHT - 90)), (pygbase.UIValue(1, False), pygbase.UIValue(90)), bg_colour=(20, 20, 20, 150)))
		self.button_size = self.button_frame.add_element(pygbase.Button(
			(pygbase.UIValue(10), pygbase.UIValue(10)),
			(pygbase.UIValue(0), pygbase.UIValue(70)),
			"images", "draw_tool_button",
			self.button_frame, self.set_tool, callback_args=(TileTools.DRAW, 0)
		)).size
		self.button_frame.add_element(pygbase.Button(
			(pygbase.UIValue(10), pygbase.UIValue(0)),
			(pygbase.UIValue(0), pygbase.UIValue(70)),
			"images", "draw_tool_button",
			self.button_frame, self.set_tool, callback_args=(TileTools.FILL, 1)
		), add_on_to_previous=(True, False), align_with_previous=(False, True))

		self.particle_manager = pygbase.Common.get_value("particle_manager")

	def set_tool(self, new_tool: TileTools, index: int):
		self.current_tool = new_tool
		self.tool_highlight_index = index

	def check_draw_layer(self):
		# Change draw layer
		if pygbase.Input.key_just_pressed(pygame.K_1):
			self.tile_selection_info.layer = 0
			self.layer_text.set_text("1")
		elif pygbase.Input.key_just_pressed(pygame.K_2):
			self.tile_selection_info.layer = 1
			self.layer_text.set_text("2")
		elif pygbase.Input.key_just_pressed(pygame.K_3):
			self.tile_selection_info.layer = 2
			self.layer_text.set_text("3")

	def update(self, delta: float):
		self._shared_state.show_global_ui = True
		self.ui.update(delta)

		self._shared_state.camera_controller.update(delta)
		self.tiled_mouse_pos = get_tile_pos(self._shared_state.camera_controller.world_mouse_pos, (TILE_SIZE, TILE_SIZE))

		self.check_draw_layer()

		if not self._shared_state.on_global_ui and not self.ui.on_ui():
			self.tools[self.current_tool].update(self.tiled_mouse_pos, self.tile_selection_info)

	def draw(self, screen: pygame.Surface):
		draw_rect_outline(screen, (255, 255, 0), -self._shared_state.camera_controller.camera.pos, (self._room.n_cols * TILE_SIZE, self._room.n_rows * TILE_SIZE), 2)
		self._room.draw(screen, self._shared_state.camera_controller.camera)

		if not self._shared_state.on_global_ui and self._shared_state.should_draw_tool and not self.ui.on_ui():
			self.tools[self.current_tool].draw(screen, self._shared_state.camera_controller.camera, self.tiled_mouse_pos, self.tile_selection_info)

		self.ui.draw(screen)

		# Tool Selection Outline
		pygame.draw.rect(screen, (47, 186, 224), (((self.button_size.x + 10) * self.tool_highlight_index + 10, SCREEN_HEIGHT - 80), self.button_size), width=2)

		self.layer_text.draw(screen)

	def next_state(self, mode_index: int):
		if mode_index == 0:
			if pygbase.Input.key_pressed(pygame.K_SPACE):
				return EditorStates.TILE_SELECTION_STATE
			else:
				return EditorStates.TILE_DRAW_STATE
		elif mode_index == 1:
			return EditorStates.OBJECT_DRAW_STATE
