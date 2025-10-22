import math
from typing import TYPE_CHECKING

import pygbase

from data.modules.base.utils import draw_rect_outline, get_tile_pos
from data.modules.objects.object_loader import ObjectLoader

if TYPE_CHECKING:
	import pygame

	from data.modules.editor.editor_selection_info import ObjectSelectionInfo
	from data.modules.objects.object_loader import GameObject


class ObjectSelectionScreen(pygbase.CameraController):
	def __init__(self, object_selection_info: ObjectSelectionInfo, object_names: list, object_size: tuple[float, float], n_cols=1):
		super().__init__(keep_in=(0, 0, min(n_cols, len(object_names)) * object_size[0], math.ceil(len(object_names) / n_cols) * object_size[1]))

		self.object_selection_info = object_selection_info

		self.object_size = object_size
		self.n_cols = n_cols
		self.n_rows = len(object_names) // n_cols + 1

		self.selected_object_index = 0
		self.objects: list[GameObject] = []
		for index, object_name in enumerate(object_names):
			x = index % n_cols
			y = index // n_cols

			game_object = ObjectLoader.create_object(object_name, ((x + 0.5) * object_size[0], (y + 1) * object_size[1]), is_pixel=True)[0]
			game_object.removed()
			self.objects.append(game_object)

		self._tiled_mouse_pos = (0, 0)

	def _get_mouse_pos(self):
		self._tiled_mouse_pos = get_tile_pos(self._world_mouse_pos, (self.object_size[0], self.object_size[1]))

	def update(self, delta: float):
		self._mouse_update()
		self._get_mouse_pos()

		if pygbase.Input.mouse_just_pressed(0):
			if 0 <= self._tiled_mouse_pos[0] < self.n_cols and 0 <= self._tiled_mouse_pos[1] < self.n_rows:
				index = self._tiled_mouse_pos[1] * self.n_cols + self._tiled_mouse_pos[0]
				if index < len(self.objects):
					self.selected_object_index = index

					selected_object = self.objects[self.selected_object_index]

					self.object_selection_info.set_object(selected_object)

		# Animate objects
		for game_object in self.objects:
			game_object.animate(delta * 2)

		self._mouse_control()
		self._keyboard_control(delta)

	def draw(self, display: pygame.Surface):
		for game_object in self.objects:
			game_object.draw(display, self._camera)

		draw_rect_outline(
			display,
			(255, 255, 255),
			(
				(self.selected_object_index % self.n_cols) * self.object_size[0] - self._camera.pos.x,
				(self.selected_object_index // self.n_cols) * self.object_size[1] - self._camera.pos.y,
			),
			self.object_size,
			2,
		)

		draw_rect_outline(display, "yellow", self._camera.world_to_screen((self.keep_in[0], self.keep_in[1])), (self.keep_in[2], self.keep_in[3]), 1)
