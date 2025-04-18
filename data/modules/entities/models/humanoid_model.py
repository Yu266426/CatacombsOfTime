import math
from typing import Literal, Any, Type

import pygame
import pygbase

from data.modules.base.registry.registrable import Registrable
from data.modules.base.registry.registry_data import RegistryData
from data.modules.entities.models.character_model import CharacterModel


class HumanoidModelData(RegistryData):
	@staticmethod
	def get_name() -> str:
		return "humanoid"

	@staticmethod
	def get_required_components() -> dict[str, Any]:
		return {
			"parts": ["body", "leg"],
		}


class HumanoidModel(CharacterModel, Registrable):
	@staticmethod
	def get_registry_data() -> Type[RegistryData]:
		return HumanoidModelData

	def __init__(self, pos: pygame.Vector2, data: dict):
		# TODO: So many pitfalls here, revise to be safer (although deepcopy is too slow).
		#  Maybe make a data transform class that handles this for me

		# Modify data from model to fit humanoid
		data_copy = data.copy()

		parts = data["parts"].copy()

		# Base right leg on "leg"
		parts["right_leg"] = parts["leg"].copy()
		# Mirror for left leg
		parts["left_leg"] = parts["leg"].copy()
		parts["left_leg"]["offset"] = (-parts["leg"]["offset"][0], parts["leg"]["offset"][1])

		del parts["leg"]

		data_copy["parts"] = parts

		super().__init__(pos, data_copy)

		self.body_part = self.parts["body"]
		self.right_leg = self.parts["right_leg"]
		self.left_leg = self.parts["left_leg"]

		self.height_offset = self.body_part.offset.y

		self.flipped = False
		self.direction = 1

		self.state = "idle"
		self.state_switch_time = pygame.time.get_ticks()

		self.max_leg_angle = 40
		self.run_anim_speed = 12
		self.right_tween = pygbase.LinearTween((-self.max_leg_angle, 0, self.max_leg_angle, -self.max_leg_angle), 2 * (2 * math.pi) / self.run_anim_speed)
		self.left_tween = pygbase.LinearTween((-self.max_leg_angle, 0, self.max_leg_angle, -self.max_leg_angle), 2 * (2 * math.pi) / self.run_anim_speed)

	def switch_state(self, new_state: Literal["idle", "run"]):
		if new_state != self.state:
			self.state = new_state
			self.state_switch_time = pygame.time.get_ticks()

			if new_state == "run":
				self.right_tween.progress = 0
				self.left_tween.progress = 0.5

	@staticmethod
	def _lerp(start, end, delta: float, lerp_speed: int = 8):
		return pygame.math.lerp(start, end, delta * lerp_speed)

	@staticmethod
	def _move_lerp(start, end, delta: float, speed: int = 20):
		offset = (end - start)

		if offset != 0:
			offset /= offset

		return start + offset * min(speed * delta, abs(end - start))

	def _idle_animate(self, delta: float):
		self.body_part.offset.y = self._lerp(self.body_part.offset.y, self.height_offset, delta * 8)
		self.body_part.part_offset.y = (math.sin((pygame.time.get_ticks() - self.state_switch_time) / 120)) * 0.2

		self.left_leg.angle = self._lerp(self.left_leg.angle, 0, delta, lerp_speed=20)
		self.right_leg.angle = self._lerp(self.right_leg.angle, 0, delta, lerp_speed=20)

	def _run_animate(self, delta: float):
		self.right_tween.tick(delta)
		self.left_tween.tick(delta)

		if self.right_tween.progress == 1:
			self.right_tween.progress = 0
		if self.left_tween.progress == 1:
			self.left_tween.progress = 0

		self.body_part.part_offset.y = self._lerp(self.body_part.part_offset.y, 0, delta * 8)
		self.body_part.offset.y = self.height_offset - (math.sin((pygame.time.get_ticks() - self.state_switch_time) / 1000 * self.run_anim_speed)) * 0.8

		# TODO: Fix animation
		#  If the player goes up, I think it should also reverse itself (down is like running "forwards")
		self.right_leg.angle = self.right_tween.value() * self.direction
		self.left_leg.angle = self.left_tween.value() * self.direction

	def update(self, delta: float):
		if self.state == "idle":
			self._idle_animate(delta)
		elif self.state == "run":
			self._run_animate(delta)

		self.body_part.flipped = self.flipped

		CharacterModel.update(self, delta)
