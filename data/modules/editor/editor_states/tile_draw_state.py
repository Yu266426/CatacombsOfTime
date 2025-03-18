import enum

import pygame
import pygbase
from pygbase.ui import *

from data.modules.base.constants import TILE_SIZE, SCREEN_HEIGHT, FRAME_BACKGROUND_COLOR, EDITOR_BUTTON_FRAME_HEIGHT, EDITOR_BUTTON_FRAME_PADDING, EDITOR_BUTTON_FRAME_GAP
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
		self.tool_highlight_index = 0

		with Frame(size=(Grow(), Grow()), layout=Layout.TOP_TO_BOTTOM) as self.ui:
			with Frame(size=(Grow(), Grow()), padding=Padding.all(10), x_align=XAlign.RIGHT):
				self.layer_text = Text("1", 60, (200, 200, 200))

			with Frame(
					size=(Grow(), EDITOR_BUTTON_FRAME_HEIGHT),
					padding=Padding.all(EDITOR_BUTTON_FRAME_PADDING),
					gap=EDITOR_BUTTON_FRAME_GAP,
					bg_color=FRAME_BACKGROUND_COLOR,
					can_interact=True,
					blocks_mouse=True
			):
				with Button(self.set_tool, (TileTools.DRAW, 0), size=(Fit(), Grow())) as button:
					Image("images/draw_tool_button", size=(Fit(), Grow()))

				with Button(self.set_tool, (TileTools.FILL, 1), size=(Fit(), Grow())):
					Image("images/draw_tool_button", size=(Fit(), Grow()))

		self.button_size = button.size

		self.particle_manager = pygbase.Common.get("particle_manager")

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

		self.tools[self.current_tool].update(self.tiled_mouse_pos, self.tile_selection_info)

	def draw(self, screen: pygame.Surface):
		draw_rect_outline(screen, (255, 255, 0), -self._shared_state.camera_controller.camera.pos, (self._room.n_cols * TILE_SIZE, self._room.n_rows * TILE_SIZE), 2)
		self._room.draw(screen, self._shared_state.camera_controller.camera)

		if self._shared_state.should_draw_tool:
			self.tools[self.current_tool].draw(screen, self._shared_state.camera_controller.camera, self.tiled_mouse_pos, self.tile_selection_info)

		self.ui.draw(screen)

		# Tool Selection Outline
		pygame.draw.rect(
			screen,
			(47, 186, 224),
			(
				(
					(self.button_size.x + EDITOR_BUTTON_FRAME_PADDING) * self.tool_highlight_index + EDITOR_BUTTON_FRAME_GAP,
					SCREEN_HEIGHT - self.button_size.y - EDITOR_BUTTON_FRAME_PADDING
				),
				self.button_size
			),
			width=2
		)

		self.layer_text.draw(screen)

	def next_state(self, mode_index: int):
		if mode_index == 0:
			if pygbase.Input.key_pressed(pygame.K_SPACE):
				return EditorStates.TILE_SELECTION_STATE
			else:
				return EditorStates.TILE_DRAW_STATE
		elif mode_index == 1:
			return EditorStates.OBJECT_DRAW_STATE
