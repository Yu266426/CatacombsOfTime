import pygame
import pygbase


class Entity:
	tags: tuple[str, ...] = ()

	def __init_subclass__(cls, **kwargs):
		if "tags" in kwargs:
			tags = kwargs["tags"]
			if not isinstance(tags, tuple):
				raise TypeError("\"tags\" argument in Entity subclass should by of type tuple[str, ...]")

			cls.tags = tags

	def __init__(self, pos: pygame.typing.Point):
		self.pos = pygame.Vector2(pos)
		self.active = True
		self.visible = True

		self.entity_tags = self.tags

		self.alive = True

	def added(self):
		pass

	def removed(self):
		pass

	def interact(self, other: "Entity"):
		pass

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

	def update(self, delta: float):
		pass

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera):
		pass

	def is_alive(self):
		return self.alive
