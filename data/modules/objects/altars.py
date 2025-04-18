from typing import Type

import pygame
import pygbase

from data.modules.base.registry.registrable import Registrable
from data.modules.base.registry.registry_data import RegistryData
from data.modules.base.utils import to_scaled
from data.modules.entities.entity import Entity
from data.modules.objects.base.game_object import GameObject
from data.modules.objects.base.game_object_data import GameObjectData


class RuneAlterData(GameObjectData):
	@staticmethod
	def get_name() -> str:
		return "rune_altar"


class RuneAltar(GameObject, Registrable):
	@staticmethod
	def get_registry_data() -> Type[RegistryData]:
		return RuneAlterData

	def __init__(self, pos: tuple, use_pixel: bool):
		self.inactive_image = pygbase.Resources.get_resource("sprite_sheets", "rune_altar").get_image(0)
		self.transition_animation = pygbase.Animation("sprite_sheets", "rune_altar", 1, 2, looping=False)
		self.active_image = pygbase.Resources.get_resource("sprite_sheets", "rune_altar").get_image(3)

		super().__init__("rune_altar", pos, use_pixel, self.inactive_image)

		self.state = 0

		self.dialogue_manager: pygbase.DialogueManager = pygbase.Common.get("dialogue_manager")
		self.dialogue_manager.add_node(pygbase.DialogueNode("rune_altar_start", "The altar shakes violently, and lights up..."))

		offset = + to_scaled(pygame.Vector2(0, -28.16))

		self.particle_manager: pygbase.ParticleManager = pygbase.Common.get("particle_manager")
		self.altar_flames = pygbase.CircleSpawner(self.pos + offset, 0.05, 8, to_scaled(4.8), True, "rune_altar", self.particle_manager)

		self.lighting_manager: pygbase.LightingManager = pygbase.Common.get("lighting_manager")
		self.light = pygbase.Light(self.pos + offset, 0.6, to_scaled(12.8), to_scaled(0.8), 0.5, tint=(0, 100, 255))

		self.activate()

	def interact(self, other: "Entity"):
		if self.state == 0:
			self.dialogue_manager.set_current_node("rune_altar_start")
			self.state = 1
			self.set_sprite(self.transition_animation)

		if self.state == 2:
			pygbase.Events.post_event("start_game")

	def activate(self):
		self.state = 2
		self.set_sprite(self.active_image)

		self.particle_manager.add_spawner(self.altar_flames)
		self.lighting_manager.add_light(self.light)

	def removed(self):
		self.particle_manager.remove_spawner(self.altar_flames)
		self.lighting_manager.remove_light(self.light)

	def update(self, delta: float):
		if self.state == 1:
			self.transition_animation.change_frame(1 * delta)
			if self.transition_animation.done():
				self.activate()
