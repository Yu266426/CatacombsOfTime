from typing import TYPE_CHECKING

import pygame
import pygbase

from data.modules.base.utils import to_scaled, to_scaled_sequence
from data.modules.entities.entity import Entity

if TYPE_CHECKING:
	from data.modules.entities.entity_manager import EntityManager


class EntitySpawn(Entity):
	def __init__(self, pos: pygame.typing.Point, entity_manager: EntityManager, time_to_spawn: float, entity_to_spawn: Entity):
		super().__init__(pos)

		self.entity_manager = entity_manager
		self.spawn_timer = pygbase.Timer(time_to_spawn, False, False)

		self.entity_to_spawn = entity_to_spawn

		self.rect = pygame.Rect((0, 0), to_scaled_sequence((10, 10)))
		self.rect.center = pos

		self.lerp = pygbase.LinearTween((to_scaled(2), 1), time_to_spawn)

	def update(self, delta: float):
		self.spawn_timer.tick(delta)
		self.lerp.tick(delta)

		if self.spawn_timer.just_done():
			self.entity_manager.add_entity(self.entity_to_spawn)

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera):
		pygame.draw.rect(surface, (255, 255, 255), camera.world_to_screen_rect(self.rect), width=int(self.lerp.value()))

	def is_alive(self):
		return not self.spawn_timer.done()
