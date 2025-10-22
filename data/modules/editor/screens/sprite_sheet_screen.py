from typing import TYPE_CHECKING

import pygbase

from data.modules.base.utils import draw_rect_outline, get_tile_pos, sort_tuple

if TYPE_CHECKING:
	import pygame

	from data.modules.editor.editor_selection_info import TileSelectionInfo


class SpriteSheetScreen(pygbase.CameraController):
	def __init__(self, selection_info: TileSelectionInfo, sprite_sheet_name: str):
		self.selection_info = selection_info

		self.sprite_sheet_name: str = sprite_sheet_name
		self.sprite_sheet: pygbase.SpriteSheet = pygbase.Resources.get_resource("sprite_sheets", sprite_sheet_name)

		super().__init__(keep_in=(0, 0, self.sprite_sheet.n_cols * self.sprite_sheet.tile_width, self.sprite_sheet.n_rows * self.sprite_sheet.tile_height))

		self.selected_topleft = (0, 0)
		self.selected_bottomright = (0, 0)

		self._tiled_mouse_pos = (0, 0)

	def get_ids(self) -> dict[int, dict[int, int]]:
		ids = {}

		for row in range(self.selected_topleft[1], self.selected_bottomright[1] + 1):
			for col in range(self.selected_topleft[0], self.selected_bottomright[0] + 1):
				if row not in ids:
					ids[row] = {}

				ids[row][col] = row * self.sprite_sheet.n_cols + col

		return ids

	def update_state(self):
		selected_topleft, selected_bottomright = sort_tuple(self.selected_topleft, self.selected_bottomright)

		self.selected_topleft = selected_topleft
		self.selected_bottomright = selected_bottomright

		self.selection_info.selected_topleft = self.selected_topleft
		self.selection_info.selected_bottomright = self.selected_bottomright

		self.selection_info.ids = self.get_ids()

	def _get_mouse_pos(self):
		self._tiled_mouse_pos = get_tile_pos(self._world_mouse_pos, (self.sprite_sheet.tile_width, self.sprite_sheet.tile_height))

	def update(self, delta: float):
		self._mouse_update()
		self._get_mouse_pos()

		if pygbase.Input.mouse_just_pressed(0):
			if (
					0 <= self._tiled_mouse_pos[0] < self.sprite_sheet.n_cols and
					0 <= self._tiled_mouse_pos[1] < self.sprite_sheet.n_rows
			):
				self.selected_topleft = self._tiled_mouse_pos
				self.selected_bottomright = self._tiled_mouse_pos

		if pygbase.Input.mouse_pressed(0):
			if (
					0 <= self._tiled_mouse_pos[0] < self.sprite_sheet.n_cols and
					0 <= self._tiled_mouse_pos[1] < self.sprite_sheet.n_rows
			):
				self.selected_bottomright = self._tiled_mouse_pos

		if pygbase.Input.mouse_just_released(0):
			self.update_state()

		self._keyboard_control(delta)
		self._mouse_control()

	def draw(self, screen: pygame.Surface):
		self.sprite_sheet.draw_sheet(screen, self._camera)

		selected_topleft, selected_bottomright = sort_tuple(self.selected_topleft, self.selected_bottomright)

		draw_rect_outline(
			screen,
			(255, 255, 255),
			(selected_topleft[0] * self.sprite_sheet.tile_width - self._camera.pos.x, selected_topleft[1] * self.sprite_sheet.tile_height - self._camera.pos.y),
			(
				self.sprite_sheet.tile_width * (selected_bottomright[0] - selected_topleft[0] + 1),
				self.sprite_sheet.tile_height * (selected_bottomright[1] - selected_topleft[1] + 1),
			),
			2,
		)
