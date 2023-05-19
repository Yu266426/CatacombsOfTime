import pygame
from pygbase import Camera, InputManager
from pygbase.graphics.animation import AnimationManager, Animation

from data.modules.entities.attacks.sword_swing import SwordSwing
from data.modules.entities.components.items.item import Item
from data.modules.entities.entity_manager import EntityManager


class EnergySword(Item):
	def __init__(self, entities: EntityManager):
		super().__init__(100)

		self.animations = AnimationManager([
			("active", Animation("energy_sword", 0, 1), 1)
		], "active")

		self.angle = -30
		self.attack_length = 100
		self.attack_damage = 1

		self.entity_manager: EntityManager = entities

	def added_to_slot(self, pos: pygame.Vector2):
		super().added_to_slot(pos)

	def update(self, delta: float):
		self.animations.update(delta)

		if InputManager.get_mouse_just_pressed(0):
			self.entity_manager.add_entity(SwordSwing(self.pos, self.angle * (1 if self.flip_x else -1), self.attack_length, self.attack_damage), tags=("damage",))

	def draw(self, screen: pygame.Surface, camera: Camera):
		self.animations.draw_at_pos(
			screen,
			self.pos,
			camera,
			angle=self.angle * (-1 if self.flip_x else 1),
			draw_pos="midbottom"
		)
