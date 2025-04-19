import math

import pygame
from typing_extensions import Self

from data.modules.base.constants import TILE_SIZE
from data.modules.level.level import LevelGenerator


class Minimap:
	def __init__(self, draw_pos: tuple[int, int], size: tuple[int, int], room_display_size: int, room_separation: int):
		self.draw_pos = draw_pos
		self.size = size
		self.room_display_size = room_display_size
		self.room_separation = room_separation
		self.draw_offset = (
			size[0] / 2,
			size[1] / 2
		)
		self.show_room_radius = (
			int(size[0] / (room_display_size + room_separation)),
			int(size[1] / (room_display_size + room_separation))
		)

		self.surface = pygame.Surface(size, flags=pygame.SRCALPHA)
		self.mask = pygame.Surface(size, flags=pygame.SRCALPHA)
		self._create_mask()

		self.target_pos = pygame.Vector2()
		self.room_data = {}
		self.inv_room_size = 0

	def _create_mask(self):
		self.mask.fill((0, 0, 0, 0))

		center = self.size[0] / 2, self.size[1] / 2
		max_radius = int(center[0])

		for i in range(max_radius, 0, -1):
			# Flipped smoothstep
			x = (i / max_radius)
			factor = 6 * (-x + 1) ** 5 - 15 * (-x + 1) ** 4 + 10 * (-x + 1) ** 3

			pygame.draw.aacircle(self.mask, (255, 255, 255, int(255 * factor)), center, i)

	def update_pos(self, pos: pygame.typing.Point):
		self.target_pos.update(pos)

	def init(self, level_generator: LevelGenerator) -> Self:
		self.inv_room_size = 1 / (level_generator.room_separation * TILE_SIZE)

		connection_data = level_generator.hallway_connections

		for room_pos, connected_rooms in connection_data.items():
			connections = []

			for connected_room in connected_rooms:
				connections.append((connected_room[0] - room_pos[0], connected_room[1] - room_pos[1]))

			self.room_data[room_pos] = connections

		return self

	def draw(self, surface: pygame.Surface):
		self.surface.fill((20, 20, 20, 0))

		current_room_pos = self.target_pos * self.inv_room_size
		int_current_room_pos = math.floor(current_room_pos[0]), math.floor(current_room_pos[1])

		for room_pos, connections in self.room_data.items():
			if abs(room_pos[0] - int_current_room_pos[0]) > self.show_room_radius[0] and abs(room_pos[1] - int_current_room_pos[1]) > self.show_room_radius[1]:
				continue

			offset_room_pos = (room_pos[0] - current_room_pos.x), (room_pos[1] - current_room_pos.y)
			display_room_pos = (
				offset_room_pos[0] * self.room_display_size + (offset_room_pos[0] + 0.5) * self.room_separation + self.draw_offset[0],
				offset_room_pos[1] * self.room_display_size + (offset_room_pos[1] + 0.5) * self.room_separation + self.draw_offset[1]
			)

			room_center = display_room_pos[0] + self.room_display_size / 2, display_room_pos[1] + self.room_display_size / 2

			for connection in connections:
				pygame.draw.line(
					self.surface,
					(200, 200, 200, 150),
					room_center,
					(
						room_center[0] + connection[0] * self.room_display_size,
						room_center[1] + connection[1] * self.room_display_size
					),
					10
				)

			pygame.draw.rect(
				self.surface,
				(240, 240, 240) if room_pos == int_current_room_pos else (150, 150, 150),
				(
					display_room_pos,
					(
						self.room_display_size,
						self.room_display_size
					)
				),

			)

		self.surface.blit(self.mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
		surface.blit(self.surface, self.draw_pos)

# surface.blit(self.mask, self.draw_pos)
