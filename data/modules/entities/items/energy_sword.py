import pygame
import pygbase

from data.modules.base.registry.registrable import Registrable
from data.modules.base.utils import to_scaled
from data.modules.entities.attacks.sword_swing import SwordSwing
from data.modules.entities.entity_manager import EntityManager
from data.modules.entities.items.item import Item
from data.modules.level.level import Level


class EnergySword(Item, Registrable):
	@staticmethod
	def get_name() -> str:
		return "energy_sword"

	def __init__(self, entity_manager: EntityManager, level: Level):
		super().__init__(100)

		self.animations = pygbase.AnimationManager([
			("active", pygbase.Animation("sprite_sheets", "energy_sword", 0, 1), 1)
		], "active")

		self.starting_angle_offset = -60

		self.attack_angle = 0
		self.attack_flip = 1

		self.angle_offset = 0
		self.swinging_down = True

		self.attack_length = to_scaled(23)
		self.attack_damage = 5

		self.level = level
		self.entity_manager: EntityManager = entity_manager
		self.particle_manager: pygbase.ParticleManager = pygbase.Common.get("particle_manager")
		self.lighting_manager: pygbase.LightingManager = pygbase.Common.get("lighting_manager")

		self.attack_cooldown = pygbase.Timer(0.5, True, False)

	def use(self):
		if self.attack_cooldown.done():
			self.entity_manager.add_entity(SwordSwing(self.pos, self.angle + (180 if self.flip_x else 0), self.attack_length, self.attack_damage, self.convert_flip()), tags=self.entity_tags)
			self.attack_cooldown.start()

			self.swinging_down = True

	def update(self, delta: float):
		self.animations.update(delta)
		self.attack_cooldown.tick(delta)

		if not self.attack_cooldown.done():
			if self.swinging_down:
				self.angle_offset += 800 * delta
				if self.angle_offset >= 70:
					self.angle_offset = 70
					self.swinging_down = False
			else:
				self.angle_offset -= 400 * delta
				if self.angle_offset <= 0:
					self.angle_offset = 0
		else:
			self.angle_offset = 0

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera):
		draw_angle = self.angle + (self.starting_angle_offset - self.angle_offset) * self.convert_flip() + (180 if self.flip_x else 0)

		self.animations.draw_at_pos(
			surface,
			self.pos,
			camera,
			angle=draw_angle,
			pivot_point=(0, 30),
			draw_pos="midbottom"
		)
