import math
from typing import TYPE_CHECKING

import pygame
import pygbase

from data.modules.base.utils import to_scaled
from data.modules.entities.components.box_collider import BoxCollider
from data.modules.entities.components.health import Health
from data.modules.entities.components.movement import Movement
from data.modules.entities.entity import Entity

if TYPE_CHECKING:
	from data.modules.entities.entity_manager import EntityManager
	from data.modules.level.level import Level


class Enemy(Entity, tags=("enemy",)):
	def __init__(
			self,
			pos: pygame.typing.Point,
			level: Level,
			entity_manager: EntityManager,
			collider_size: tuple[int, int],
			health: int,
			data: dict[str, ...],  # NoQA: Used by subclasses
	):
		super().__init__(pos)

		self.collider = BoxCollider(collider_size).link_pos(self.pos)
		self.movement = Movement(480, 10, level, self.collider)

		self.health = Health(health)
		self.damage_timer = pygbase.Timer(0.6, True, False)

		self.entity_manager = entity_manager
		self._data = data

	def damaged(self):
		pass

	def update(self, delta: float):
		self.damage_timer.tick(delta)

		if self.damage_timer.done():
			damage_entities = self.entity_manager.get_entities_of_tag("damage")
			for entity in damage_entities:
				if "from_enemy" in entity.entity_tags:
					continue

				if self.collider.collides_with(entity.collider):
					# print(entity)
					self.health.damage(entity.damage)

					dir_vec = entity.pos - self.pos
					if dir_vec.length() != 0:
						dir_vec.normalize_ip()

					self.movement.velocity -= dir_vec * to_scaled(320)

					self.damage_timer.start()

					self.damaged()
					break

		# Flashing hit effect
		self.visible = self.damage_timer.done() or not math.sin(pygame.time.get_ticks() / 25) > 0

	def is_alive(self):
		return self.health.is_alive()
