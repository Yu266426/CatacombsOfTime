import pygame
import pygbase

from data.modules.entities.components.line_collider import LineCollider
from data.modules.entities.entity import Entity


class SwordSwing(Entity, tags=("damage",)):
	def __init__(self, pos: pygame.Vector2, angle: float, length: float, damage: int, flip: int):
		super().__init__(pos)
		self.parent_pos = pos

		self.alive = True

		self.damage = damage

		self.starting_angle = angle - 20 * flip
		self.max_angle = 90
		self.swing_speed = 600

		self.collider = LineCollider(self.pos, self.starting_angle, length, start_offset=50).link_pos(pos)

		self.flip = flip
		self.animation = pygbase.Animation("sprite_sheets", "sword_swing_1", 0, 9, False)

	def is_alive(self):
		return self.alive

	def update(self, delta: float):
		self.collider.change_angle(self.flip * self.swing_speed * delta)

		self.animation.change_frame(40 * delta)

		if abs(self.collider.angle - self.starting_angle) > self.max_angle:
			self.alive = False

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera):
		self.collider.draw_debug(camera)

		angle = self.starting_angle
		if self.flip == 1:
			angle -= 90
		else:
			angle += 90 + 180

		self.animation.draw_at_pos(
			surface,
			self.parent_pos + pygame.Vector2(0, -70) * self.flip,
			camera,
			angle,
			(-0, 70 * self.flip),
			flip=(False, self.flip == -1),
			draw_pos="midbottom",
		)
