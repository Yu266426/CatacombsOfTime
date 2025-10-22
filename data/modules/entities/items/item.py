from typing import TYPE_CHECKING

from data.modules.entities.entity import Entity

if TYPE_CHECKING:
	import pygame
	from pygbase import Camera


class Item(Entity, tags=("item",)):
	def __init_subclass__(cls, **kwargs):
		if "tags" in kwargs:
			tags = kwargs["tags"]
			if not isinstance(tags, tuple):
				raise TypeError('"tags" argument in Item subclass should by of type tuple[str, ...]')

			cls.tags = cls.tags + tags

	def __init__(self, durability: int):
		super().__init__((0, 0))

		self.durability: int = durability

		self.flip_x = False  # Updated by ItemSlot
		self.angle = 0  # Updated by ItemSlot

	def added_to_slot(self, pos: pygame.Vector2):
		self.pos = pos

	def check_durability(self):
		if self.durability != -1:
			return self.durability > 0
		return True

	def reduce_durability(self, amount):
		if self.durability != -1:
			self.durability -= amount
			if self.durability < 0:
				self.durability = 0

	def convert_flip(self):
		return -1 if self.flip_x else 1

	def use(self):
		pass

	def update(self, delta: float):
		pass

	def draw(self, surface: pygame.Surface, camera: Camera):
		pass
