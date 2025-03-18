import random

import pygame
import pygbase

from data.modules.base.registry.registrable import Registrable
from data.modules.base.utils import to_scaled
from data.modules.objects.game_object import GameObject


class Torch(GameObject, Registrable):
	@staticmethod
	def get_name() -> str:
		return "torch"

	def __init__(self, pos: tuple, use_pixel: bool):
		GameObject.__init__(self, "torch", pos, use_pixel, pygbase.Resources.get_resource("sprite_sheets", "objects").get_image(1))

		offset = to_scaled(pygame.Vector2(0, -14.72))

		self.particle_manager: pygbase.ParticleManager = pygbase.Common.get("particle_manager")
		self.fire = pygbase.CircleSpawner(self.pos + offset, 0.05, 3, to_scaled(3.2), True, "fire", self.particle_manager)

		self.lighting_manager: pygbase.LightingManager = pygbase.Common.get("lighting_manager")
		self.light = pygbase.Light(self.pos + offset, 0.3, to_scaled(8), to_scaled(0.8), random.uniform(1.7, 2.3), tint=(255, 225, 53))

	def added(self):
		self.particle_manager.add_spawner(self.fire)
		self.lighting_manager.add_light(self.light)

	def removed(self):
		self.particle_manager.remove_spawner(self.fire)
		self.lighting_manager.remove_light(self.light)
