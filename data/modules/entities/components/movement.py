from typing import TYPE_CHECKING

import pygame

from data.modules.base.constants import TILE_SIZE
from data.modules.base.utils import get_1d_tile_pos, to_scaled

if TYPE_CHECKING:
	from data.modules.entities.components.box_collider import BoxCollider
	from data.modules.level.level import Level


class Movement:
	def __init__(self, speed: float, drag: float, level: Level, hitbox: BoxCollider):
		self.speed = to_scaled(speed)
		self.drag = drag

		self.velocity = pygame.Vector2()

		self.level = level
		self.hitbox = hitbox

	def move_in_direction(self, pos: pygame.Vector2, direction: pygame.Vector2, delta: float):
		normalized_direction = direction.copy()
		if normalized_direction.length() != 0:
			normalized_direction.normalize_ip()

		acceleration = normalized_direction * self.speed

		is_collision = [False, False]

		pos.x += self.velocity.x * delta + 0.5 * acceleration.x * delta ** 2
		hitbox = self.hitbox.rect
		if self.velocity.x > 0:
			top_right_tile = self.level.get_tile(hitbox.topright)
			if top_right_tile:
				pos.x = (get_1d_tile_pos(hitbox.x, TILE_SIZE) + 1) * TILE_SIZE - hitbox.width / 2 - 1
				is_collision[0] = True

			bottom_right_tile = self.level.get_tile(hitbox.bottomright)
			if bottom_right_tile:
				pos.x = (get_1d_tile_pos(hitbox.x, TILE_SIZE) + 1) * TILE_SIZE - hitbox.width / 2 - 1
				is_collision[0] = True
		elif self.velocity.x < 0:
			top_left_tile = self.level.get_tile(hitbox.topleft)
			if top_left_tile:
				pos.x = (get_1d_tile_pos(hitbox.x, TILE_SIZE) + 1) * TILE_SIZE + hitbox.width / 2 + 1
				is_collision[0] = True

			bottom_left_tile = self.level.get_tile(hitbox.bottomleft)
			if bottom_left_tile:
				pos.x = (get_1d_tile_pos(hitbox.x, TILE_SIZE) + 1) * TILE_SIZE + hitbox.width / 2 + 1
				is_collision[0] = True

		if is_collision[0]:
			self.velocity.x = 0

		pos.y += self.velocity.y * delta + 0.5 * acceleration.y * delta ** 2
		hitbox = self.hitbox.rect
		if self.velocity.y > 0:
			bottom_left_tile = self.level.get_tile(hitbox.bottomleft)
			if bottom_left_tile:
				pos.y = (get_1d_tile_pos(hitbox.y, TILE_SIZE) + 1) * TILE_SIZE - 1
				is_collision[1] = True

			bottom_right_tile = self.level.get_tile(hitbox.bottomright)
			if bottom_right_tile:
				pos.y = (get_1d_tile_pos(hitbox.y, TILE_SIZE) + 1) * TILE_SIZE - 1
				is_collision[1] = True
		elif self.velocity.y < 0:
			top_left_tile = self.level.get_tile(hitbox.topleft)
			if top_left_tile:
				pos.y = (get_1d_tile_pos(hitbox.y, TILE_SIZE) + 1) * TILE_SIZE + hitbox.height + 1
				is_collision[1] = True

			top_right_tile = self.level.get_tile(hitbox.topright)
			if top_right_tile:
				pos.y = (get_1d_tile_pos(hitbox.y, TILE_SIZE) + 1) * TILE_SIZE + hitbox.height + 1
				is_collision[1] = True

		if is_collision[1]:
			self.velocity.y = 0

		self.velocity += (acceleration - self.velocity * self.drag) * delta

		return is_collision

	def add_force(self, direction: pygame.Vector2, force: float):
		normalized_direction = direction.copy()
		if normalized_direction.length() != 0:
			normalized_direction.normalize_ip()

		self.velocity += direction * force
