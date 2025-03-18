import pygbase

from data.modules.entities.components.circle_collider import CircleCollider
from data.modules.entities.entity import Entity


class Explosion(Entity, tags=("damage",)):
	def __init__(self, pos, radius: float, damage: float):
		super().__init__(pos)
		self.alive = True

		self.collider = CircleCollider(self.pos, radius)
		self.damage = damage

		self.particle_manager: pygbase.ParticleManager = pygbase.Common.get("particle_manager")
		self.explosion_particles = self.particle_manager.add_spawner(pygbase.CircleSpawner(self.pos, 0.05, 150, radius, True, "fire", self.particle_manager, radial_velocity_range=(20, 400)))

		self.lighting_manager: pygbase.LightingManager = pygbase.Common.get("lighting_manager")
		self.light = self.lighting_manager.add_light(pygbase.Light(self.pos, 0.8, radius, radius / 8, 30, tint=(255, 0, 0)))
		self.light2 = self.lighting_manager.add_light(pygbase.Light(self.pos, 0.8, radius * 1.4, radius / 7, 30, tint=(255, 0, 0)))
		self.light3 = self.lighting_manager.add_light(pygbase.Light(self.pos, 0.2, radius * 1.7, radius / 6, 30, tint=(255, 0, 0)))

		self.emit_timer = pygbase.Timer(0.1, False, False)
		self.death_timer = pygbase.Timer(0.3, False, False)

	def is_alive(self):
		return self.alive

	def removed(self):
		self.particle_manager.remove_spawner(self.explosion_particles)

		self.lighting_manager.remove_light(self.light)
		self.lighting_manager.remove_light(self.light2)
		self.lighting_manager.remove_light(self.light3)

	def update(self, delta: float):
		self.emit_timer.tick(delta)
		self.death_timer.tick(delta)

		if self.emit_timer.just_done():
			self.particle_manager.remove_spawner(self.explosion_particles)

		if self.death_timer.just_done():
			self.alive = False

			self.lighting_manager.remove_light(self.light)
			self.lighting_manager.remove_light(self.light2)
			self.lighting_manager.remove_light(self.light3)
