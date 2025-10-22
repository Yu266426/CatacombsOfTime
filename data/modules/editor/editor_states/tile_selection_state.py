from typing import TYPE_CHECKING

import pygame
import pygbase
from pygbase.ui import *

from data.modules.base.constants import (
	EDITOR_BUTTON_FRAME_GAP,
	EDITOR_BUTTON_FRAME_HEIGHT,
	EDITOR_BUTTON_FRAME_PADDING,
	FRAME_BACKGROUND_COLOR,
)
from data.modules.editor.editor_states.editor_state import EditorState, EditorStates
from data.modules.editor.screens.sprite_sheet_screen import SpriteSheetScreen

if TYPE_CHECKING:
	from data.modules.editor.actions.editor_actions import EditorActionQueue
	from data.modules.editor.editor_selection_info import TileSelectionInfo
	from data.modules.editor.shared_editor_state import SharedEditorState
	from data.modules.level.room import EditorRoom


class TileSelectionState(EditorState):
	def __init__(self, room: EditorRoom, shared_state: SharedEditorState, action_queue: EditorActionQueue, tile_selection_info: TileSelectionInfo):
		super().__init__(room, shared_state, action_queue)

		self.tile_selection_info = tile_selection_info

		self.sprite_sheet_index = 0
		self.sprite_sheets: list[SpriteSheetScreen] = [
			SpriteSheetScreen(self.tile_selection_info, "tiles"),
			SpriteSheetScreen(self.tile_selection_info, "walls"),
		]

		with Frame(size=(Grow(), Grow()), y_align=YAlign.BOTTOM) as self.ui, Frame(
				size=(Grow(), EDITOR_BUTTON_FRAME_HEIGHT),
				padding=Padding.all(EDITOR_BUTTON_FRAME_PADDING),
				gap=EDITOR_BUTTON_FRAME_GAP,
				bg_color=FRAME_BACKGROUND_COLOR,
				can_interact=True,
				blocks_mouse=True,
		):
			for i in range(len(self.sprite_sheets)):
				with Button(self.switch_screen, (i,), size=(Fit(), Grow())):
					Image("images/tile_set_button", size=(Fit(), Grow()))

	def switch_screen(self, new_index: int):
		self.sprite_sheet_index = new_index

		self.tile_selection_info.sprite_sheet_name = self.sprite_sheets[self.sprite_sheet_index].sprite_sheet_name
		self.tile_selection_info.selected_topleft = self.sprite_sheets[self.sprite_sheet_index].selected_topleft
		self.tile_selection_info.selected_bottomright = self.sprite_sheets[self.sprite_sheet_index].selected_bottomright

		self.tile_selection_info.ids = self.sprite_sheets[self.sprite_sheet_index].get_ids()

	def update(self, delta: float):
		self._shared_state.show_global_ui = False

		self.ui.update(delta)

		if self._shared_state.should_draw_tool:
			self.sprite_sheets[self.sprite_sheet_index].update(delta)

	def draw(self, screen: pygame.Surface):
		self.sprite_sheets[self.sprite_sheet_index].draw(screen)

		self.ui.draw(screen)

	def next_state(self, mode_index: int) -> EditorStates | None:
		if mode_index == 0:
			if pygbase.Input.key_pressed(pygame.K_SPACE):
				return EditorStates.TILE_SELECTION_STATE
			self.sprite_sheets[self.sprite_sheet_index].update_state()
			return EditorStates.TILE_DRAW_STATE
		if mode_index == 1:
			return EditorStates.OBJECT_DRAW_STATE
		return None
