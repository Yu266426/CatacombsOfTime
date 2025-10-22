import enum
from typing import TYPE_CHECKING

import pygame
import pygbase
from pygbase.ui import *

from data.modules.base.constants import (
	EDITOR_BUTTON_FRAME_GAP,
	EDITOR_BUTTON_FRAME_HEIGHT,
	EDITOR_BUTTON_FRAME_PADDING,
	FRAME_BACKGROUND_COLOR,
	TILE_SIZE,
)
from data.modules.base.utils import draw_rect_outline, get_tile_pos
from data.modules.editor.editor_states.editor_state import EditorState, EditorStates
from data.modules.editor.tools.object_tools.object_draw_tool import ObjectDrawTool

if TYPE_CHECKING:
	from data.modules.editor.actions.editor_actions import EditorActionQueue
	from data.modules.editor.editor_selection_info import ObjectSelectionInfo
	from data.modules.editor.shared_editor_state import SharedEditorState
	from data.modules.editor.tools.editor_tool import EditorTool
	from data.modules.level.room import EditorRoom


class ObjectTools(enum.Enum):
	DRAW = enum.auto()


class ObjectDrawState(EditorState):
	def __init__(self, room: EditorRoom, shared_state: SharedEditorState, action_queue: EditorActionQueue, object_selection_info: ObjectSelectionInfo):
		super().__init__(room, shared_state, action_queue)

		self.object_selection_info = object_selection_info

		self.current_tool: ObjectTools = ObjectTools.DRAW
		self.tools: dict[ObjectTools, EditorTool] = {
			ObjectTools.DRAW: ObjectDrawTool(self._room, self._shared_state, self._action_queue),
		}

		self.tiled_mouse_pos = get_tile_pos(self._shared_state.camera_controller.world_mouse_pos, (TILE_SIZE, TILE_SIZE))

		with Frame(size=(Grow(), Grow()), y_align=YAlign.BOTTOM) as self.ui:
			with Frame(
				size=(Grow(), EDITOR_BUTTON_FRAME_HEIGHT),
				padding=Padding.all(EDITOR_BUTTON_FRAME_PADDING),
				gap=EDITOR_BUTTON_FRAME_GAP,
				bg_color=FRAME_BACKGROUND_COLOR,
				can_interact=True,
				blocks_mouse=True,
			):
				with Button(self.reset_object_animations, size=(Fit(), Grow())):
					Image("images/reload_button", size=(Fit(), Grow()))

		self.particle_manager = pygbase.Common.get("particle_manager")

	def reset_object_animations(self):
		for game_object in self._room.objects:
			if game_object.is_animated:
				game_object.sprite.frame = 0

	def update(self, delta: float):
		self._shared_state.show_global_ui = True
		self.ui.update(delta)

		self._shared_state.camera_controller.update(delta)
		self.tiled_mouse_pos = get_tile_pos(self._shared_state.camera_controller.world_mouse_pos, (TILE_SIZE, TILE_SIZE))

		self.tools[self.current_tool].update(self.tiled_mouse_pos, self.object_selection_info)

	def draw(self, screen: pygame.Surface):
		draw_rect_outline(
			screen,
			(255, 255, 0),
			-self._shared_state.camera_controller.camera.pos,
			(self._room.n_cols * TILE_SIZE, self._room.n_rows * TILE_SIZE),
			2,
		)
		self._room.draw(screen, self._shared_state.camera_controller.camera)

		if self._shared_state.should_draw_tool:
			self.tools[self.current_tool].draw(screen, self._shared_state.camera_controller.camera, self.tiled_mouse_pos, self.object_selection_info)

		self.ui.draw(screen)

	def next_state(self, mode_index: int) -> EditorStates | None:
		if mode_index == 0:
			return EditorStates.TILE_DRAW_STATE
		if mode_index == 1:
			if pygbase.Input.key_pressed(pygame.K_SPACE):
				return EditorStates.OBJECT_SELECTION_STATE
			return EditorStates.OBJECT_DRAW_STATE
		return None
