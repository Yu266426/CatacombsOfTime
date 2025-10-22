from typing import TYPE_CHECKING

import pygame
import pygbase
from pygbase.ui import *

from data.modules.base.constants import (
	EDITOR_BUTTON_FRAME_GAP,
	EDITOR_BUTTON_FRAME_HEIGHT,
	EDITOR_BUTTON_FRAME_PADDING,
	FRAME_BACKGROUND_COLOR,
	PIXEL_SCALE,
)
from data.modules.editor.editor_states.editor_state import EditorState, EditorStates
from data.modules.editor.screens.object_selection_screen import ObjectSelectionScreen

if TYPE_CHECKING:
	from data.modules.editor.actions.editor_actions import EditorActionQueue
	from data.modules.editor.editor_selection_info import ObjectSelectionInfo
	from data.modules.editor.shared_editor_state import SharedEditorState
	from data.modules.level.room import EditorRoom


class ObjectSelectionState(EditorState):
	def __init__(self, room: EditorRoom, shared_state: SharedEditorState, action_queue: EditorActionQueue, object_selection_info: ObjectSelectionInfo):
		super().__init__(room, shared_state, action_queue)

		self.object_selection_info: ObjectSelectionInfo = object_selection_info

		self.object_screen_index: int = 0
		self.object_screens: list[ObjectSelectionScreen] = [
			ObjectSelectionScreen(
				self.object_selection_info,
				["small_cube", "small_red_cube", "small_green_cube", "large_cube", "large_red_cube", "large_green_cube", "lever", "chest", "torch"],
				(16 * PIXEL_SCALE, 16 * PIXEL_SCALE),
				n_cols=6,
			),
			ObjectSelectionScreen(self.object_selection_info, ["rune_altar"], (32 * PIXEL_SCALE, 48 * PIXEL_SCALE), n_cols=5),
		]

		with Frame(size=(Grow(), Grow()), y_align=YAlign.BOTTOM) as self.ui, Frame(
				size=(Grow(), EDITOR_BUTTON_FRAME_HEIGHT),
				padding=Padding.all(EDITOR_BUTTON_FRAME_PADDING),
				gap=EDITOR_BUTTON_FRAME_GAP,
				bg_color=FRAME_BACKGROUND_COLOR,
				can_interact=True,
				blocks_mouse=True,
		):
			for i in range(len(self.object_screens)):
				with Button(self.switch_screen, (i,), size=(Fit(), Grow())):
					Image("images/tile_set_button", size=(Fit(), Grow()))

	def switch_screen(self, new_index: int):
		self.object_screen_index = new_index

		self.object_selection_info.set_object(self.object_screens[self.object_screen_index].objects[self.object_screens[self.object_screen_index].selected_object_index])

	def update(self, delta: float):
		self._shared_state.show_global_ui = False

		self.ui.update(delta)

		if self._shared_state.should_draw_tool:
			self.object_screens[self.object_screen_index].update(delta)

	def draw(self, screen: pygame.Surface):
		self.object_screens[self.object_screen_index].draw(screen)

		self.ui.draw(screen)

	def next_state(self, mode_index: int) -> EditorStates | None:
		if mode_index == 0:
			return EditorStates.TILE_DRAW_STATE
		if mode_index == 1:
			if pygbase.Input.key_pressed(pygame.K_SPACE):
				return EditorStates.OBJECT_SELECTION_STATE
			return EditorStates.OBJECT_DRAW_STATE
		return None
