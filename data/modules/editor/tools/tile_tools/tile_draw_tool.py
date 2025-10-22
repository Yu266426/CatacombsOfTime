from typing import TYPE_CHECKING

import pygame
import pygbase

from data.modules.base.constants import TILE_SIZE
from data.modules.base.utils import draw_rect_outline
from data.modules.editor.actions.editor_actions import EditorActionBatch
from data.modules.editor.actions.tile_actions import PlaceTileAction, RemoveTileAction
from data.modules.editor.tools.editor_tool import EditorTool
from data.modules.level.tile import Tile

if TYPE_CHECKING:
	from data.modules.editor.actions.editor_actions import EditorActionQueue
	from data.modules.editor.editor_selection_info import TileSelectionInfo
	from data.modules.editor.shared_editor_state import SharedEditorState
	from data.modules.level.room import EditorRoom


class TileDrawTool(EditorTool):
	def __init__(self, room: EditorRoom, shared_state: SharedEditorState, action_queue: EditorActionQueue):
		super().__init__(room, shared_state, action_queue)

		self.current_place_tile: tuple[int, int] | None = None
		self.current_erase_tile: tuple[int, int] | None = None

		self.current_batch: EditorActionBatch | None = None

	def draw_tiles(self, mouse_pos: tuple[int, int], selection_info: TileSelectionInfo):
		for row, row_data in selection_info.ids.items():
			for col, image_id in row_data.items():
				tile_x = mouse_pos[0] + col - selection_info.selected_topleft[0]
				tile_y = mouse_pos[1] + row - selection_info.selected_topleft[1]

				if self.current_place_tile != mouse_pos:
					action = PlaceTileAction(self._room, selection_info.layer, tile_y, tile_x, Tile(
						selection_info.sprite_sheet_name,
						image_id,
						(tile_x * TILE_SIZE, (tile_y + 1) * TILE_SIZE),
					))
					action.execute()

					if self.current_batch is None:
						self.current_batch = EditorActionBatch()

					self.current_batch.add_action(action)

		self.current_place_tile = mouse_pos

	def erase_tiles(self, mouse_pos: tuple[int, int], selection_info: TileSelectionInfo):
		for row in range(selection_info.selected_bottomright[1] - selection_info.selected_topleft[1] + 1):
			for col in range(selection_info.selected_bottomright[0] - selection_info.selected_topleft[0] + 1):
				tile_x = mouse_pos[0] + col
				tile_y = mouse_pos[1] + row

				if self.current_erase_tile != mouse_pos:
					action = RemoveTileAction(self._room, selection_info.layer, tile_y, tile_x)
					action.execute()

					if self.current_batch is None:
						self.current_batch = EditorActionBatch()

					self.current_batch.add_action(action)

		self.current_erase_tile = mouse_pos

	def update(self, mouse_tile_pos: tuple[int, int], selection_info: TileSelectionInfo):
		# Draw
		if pygbase.Input.mouse_pressed(0):
			self._shared_state.show_global_ui = False
			self.draw_tiles(mouse_tile_pos, selection_info)

		# Erase
		elif pygbase.Input.mouse_pressed(2):
			self._shared_state.show_global_ui = False
			self.erase_tiles(mouse_tile_pos, selection_info)

		if pygbase.Input.mouse_just_released(0) or pygbase.Input.mouse_just_released(2):
			self._shared_state.show_global_ui = True

			if self.current_batch is not None:
				self._action_queue.add_action(self.current_batch)
				self.current_batch = None

			self.current_place_tile = None
			self.current_erase_tile = None

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera, mouse_tile_pos: tuple, selection_info: TileSelectionInfo):
		# Tile outline rect
		draw_rect_outline(
			surface, (255, 255, 255),
			camera.world_to_screen((mouse_tile_pos[0] * TILE_SIZE, mouse_tile_pos[1] * TILE_SIZE)),
			(
				TILE_SIZE * (selection_info.selected_bottomright[0] - selection_info.selected_topleft[0] + 1),
				TILE_SIZE * (selection_info.selected_bottomright[1] - selection_info.selected_topleft[1] + 1),
			),
			2,
		)

		# If not deleting tiles, draw ghost tile
		if not pygbase.Input.mouse_pressed(2):
			for row, row_data in selection_info.ids.items():
				for col, image_id in row_data.items():
					tile_x = mouse_tile_pos[0] + col - selection_info.selected_topleft[0]
					tile_y = mouse_tile_pos[1] + row - selection_info.selected_topleft[1]

					Tile(
						selection_info.sprite_sheet_name,
						image_id,
						(tile_x * TILE_SIZE, (tile_y + 1) * TILE_SIZE),
					).draw(surface, camera, flag=pygame.BLEND_ADD)
