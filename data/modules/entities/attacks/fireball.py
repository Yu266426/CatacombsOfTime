import pygame
import pygbase

from data.modules.entities.attacks.explosion import Explosion
from data.modules.entities.entity import Entity
from data.modules.entities.entity_manager import EntityManager
from data.modules.level.level import Level


class Fireball(Entity):
	def __init__(self, pos, direction: float, speed: float, projectile_range: float, radius: float, explosion_radius: float, damage: float, level: Level, entity_manager: EntityManager):
		super().__init__(pos)
		self.alive = True

		self.movement = pygame.Vector2(speed, 0).rotate(-direction)
		self.radius = radius

		self.distance = 0
		self.projectile_range = projectile_range

		self.explosion_radius = explosion_radius
		self.damage = damage

		self.level = level
		self.entity_manager = entity_manager
		self.particle_manager = pygbase.Common.get("particle_manager")
		self.fire_particles = self.particle_manager.add_spawner(
			pygbase.CircleSpawner(
				self.pos,
				0.05,
				50,
				self.radius,
				True,
				"fire",
				self.particle_manager,
				linear_velocity_range=((0, self.movement.x / 4), (0, self.movement.y / 4))
			)
		)

		self.lighting_manager = pygbase.Common.get("lighting_manager")
		self.light = self.lighting_manager.add_light(pygbase.Light(self.pos, 0.8, self.radius, self.radius / 8, 2, tint=(255, 0, 0)))
		self.light2 = self.lighting_manager.add_light(pygbase.Light(self.pos, 0.8, self.radius * 2, self.radius / 7, 2, tint=(255, 0, 0)))
		self.light3 = self.lighting_manager.add_light(pygbase.Light(self.pos, 0.2, self.radius * 3, self.radius / 6, 2, tint=(255, 0, 0)))

	def is_alive(self):
		return self.alive

	def removed(self):
		self.particle_manager.remove_spawner(self.fire_particles)
		self.lighting_manager.remove_light(self.light)
		self.lighting_manager.remove_light(self.light2)
		self.lighting_manager.remove_light(self.light3)

	def update(self, delta: float):
		next_move = self.movement * delta

		self.pos += next_move
		self.distance += next_move.length()

		if self.alive and (self.distance > self.projectile_range or self.level.get_tile(self.pos) is not None):
			self.alive = False

			self.particle_manager.remove_spawner(self.fire_particles)
			self.lighting_manager.remove_light(self.light)
			self.lighting_manager.remove_light(self.light2)
			self.lighting_manager.remove_light(self.light3)

			self.entity_manager.add_entity(Explosion(self.pos, self.explosion_radius, self.damage), tags=self.entity_tags)
