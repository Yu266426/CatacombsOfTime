from collections import deque
from typing import TYPE_CHECKING

import pygame
import pygbase

from data.modules.base.constants import TILE_SIZE
from data.modules.editor.actions.editor_actions import EditorActionBatch
from data.modules.editor.actions.tile_actions import PlaceTileAction, RemoveTileAction
from data.modules.editor.tools.editor_tool import EditorTool
from data.modules.level.tile import Tile

if TYPE_CHECKING:
	from data.modules.editor.actions.editor_actions import EditorActionQueue
	from data.modules.editor.editor_selection_info import TileSelectionInfo
	from data.modules.editor.shared_editor_state import SharedEditorState
	from data.modules.level.room import EditorRoom


class TileFillTool(EditorTool):
	def __init__(self, room: EditorRoom, shared_state: SharedEditorState, action_queue: EditorActionQueue):
		super().__init__(room, shared_state, action_queue)

		self.current_batch: EditorActionBatch | None = None

		self.fill_preview_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), flags=pygame.SRCALPHA)
		self.fill_preview_surface.fill((0, 40, 40, 50))

	def fill(self, mouse_pos: tuple[int, int], selection_info: TileSelectionInfo) -> set[tuple[int, int]]:
		directions: list[tuple[int, int]] = [
			(1, 0),
			(-1, 0),
			(0, 1),
			(0, -1),
		]

		starting_tile: Tile | None = self._room.get_tile(selection_info.layer, mouse_pos)
		visited: set[tuple[int, int]] = set()

		tile_queue: deque[tuple[int, int]] = deque()
		tile_queue.append(mouse_pos)

		fill_tiles: set[tuple[int, int]] = set()

		while len(tile_queue) > 0:
			current_pos = tile_queue.popleft()
			current_tile = self._room.get_tile(selection_info.layer, current_pos)

			if not self._room.check_bounds(current_pos):
				continue

			if starting_tile is not None and current_tile is not None:
				if (
						current_tile.sprite_sheet_name == starting_tile.sprite_sheet_name
						and current_tile.image_index == starting_tile.image_index
				):
					fill_tiles.add(current_pos)
				else:
					continue

			elif starting_tile is None and current_tile is None:
				fill_tiles.add(current_pos)
			else:
				continue

			for direction in directions:
				new_pos = current_pos[0] + direction[0], current_pos[1] + direction[1]
				if new_pos not in visited:
					visited.add(new_pos)
					tile_queue.append(new_pos)

		return fill_tiles

	def update(self, mouse_tile_pos: tuple[int, int], selection_info: TileSelectionInfo):
		def place_tile(current_pos: tuple[int, int]):
			action = PlaceTileAction(self._room, selection_info.layer, current_pos[1], current_pos[0], Tile(
				selection_info.sprite_sheet_name,
				selection_info.ids[selection_info.selected_topleft[1]][selection_info.selected_topleft[0]],
				(current_pos[0] * TILE_SIZE, (current_pos[1] + 1) * TILE_SIZE),
			))
			action.execute()

			self.current_batch.add_action(action)

		def remove_tile(current_pos: tuple[int, int]):
			action = RemoveTileAction(self._room, selection_info.layer, current_pos[1], current_pos[0])
			action.execute()

			self.current_batch.add_action(action)

		# Place
		if pygbase.Input.mouse_just_pressed(0):
			self.current_batch = EditorActionBatch()
			fill_tiles = self.fill(mouse_tile_pos, selection_info)
			for pos in fill_tiles:
				place_tile(pos)

			self._action_queue.add_action(self.current_batch)
			self.current_batch = None

		# Remove
		elif pygbase.Input.mouse_just_pressed(2):
			self.current_batch = EditorActionBatch()
			fill_tiles = self.fill(mouse_tile_pos, selection_info)
			for pos in fill_tiles:
				remove_tile(pos)

			self._action_queue.add_action(self.current_batch)
			self.current_batch = None

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera, mouse_tile_pos: tuple[int, int], selection_info: TileSelectionInfo):
		fill_tiles = self.fill(mouse_tile_pos, selection_info)
		for pos in fill_tiles:
			tile_pos = pos[0] * TILE_SIZE, pos[1] * TILE_SIZE
			surface.blit(self.fill_preview_surface, camera.world_to_screen(tile_pos), special_flags=pygame.BLEND_ADD)
