import pygame
from pygbase import Camera


class Entity:
	def __init__(self, pos):
		self.pos = pygame.Vector2(pos)

	def update(self, delta: float):
		pass

	def draw(self, screen: pygame.Surface, camera: Camera):
		pass

	def is_alive(self):
		return True
