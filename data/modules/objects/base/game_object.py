from typing import TYPE_CHECKING

import pygbase

from data.modules.base.constants import TILE_SIZE
from data.modules.entities.entity import Entity

if TYPE_CHECKING:
	import pygame


# TODO: Separate basic game object from base class (more subtypes, like how enemies work)
class GameObject(Entity, tags=("object",)):
	def __init__(
			self,
			name: str,
			pos: pygame.typing.Point,
			use_pixel: bool,
			sprite: pygbase.Image | pygbase.Animation,
			custom_hitbox: pygame.Rect | None = None,
			_is_editor_object: bool = False,
	):
		if use_pixel:
			super().__init__(pos)
			self.tile_pos = int(pos[0] / TILE_SIZE), int(pos[1] / TILE_SIZE)
		else:
			super().__init__(((pos[0] + 0.5) * TILE_SIZE, (pos[1] + 1) * TILE_SIZE))
			self.tile_pos = pos

		self.name = name

		self.sprite = sprite
		self.is_animated = isinstance(self.sprite, pygbase.Animation)
		if self.is_animated:
			self.rect = self.sprite.get_current_image().get_image(0).get_rect(midbottom=self.pos)
		else:
			self.rect = self.sprite.get_image(0).get_rect(midbottom=self.pos)

		if custom_hitbox is None:
			self.hitbox = self.rect.copy()
		else:
			self.hitbox: pygame.Rect = custom_hitbox
			self.hitbox.midbottom = self.pos

	def added(self):
		pass

	def removed(self):
		pass

	def set_sprite(self, sprite: pygbase.Image | pygbase.Animation):
		self.sprite = sprite
		self.is_animated = isinstance(self.sprite, pygbase.Animation)

	def animate(self, frame_time: float):
		if self.is_animated:
			self.sprite.change_frame(frame_time)

	def update(self, delta: float):
		self.animate(delta)

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera, flags=0):
		if self.is_animated:
			self.sprite.draw_at_pos(surface, self.pos, camera, draw_pos="midbottom", flags=flags)
		else:
			self.sprite.draw(surface, camera.world_to_screen(self.pos), draw_pos="midbottom", flags=flags)

		pygbase.Debug.draw_rect(camera.world_to_screen_rect(self.hitbox), "dark green", 2)
