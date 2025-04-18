import random
from typing import TYPE_CHECKING, Any, Type

import pygame

from data.modules.base.constants import PIXEL_SCALE
from data.modules.base.registry.registrable import Registrable
from data.modules.base.registry.registry_data import RegistryData
from data.modules.entities.components.movement import Movement
from data.modules.entities.entity_manager import EntityManager
from data.modules.entities.models.humanoid_model import HumanoidModel
from data.modules.entities.states.entity_state import EntityState

if TYPE_CHECKING:
	from data.modules.level.level import Level


class WanderStateData(RegistryData):
	@staticmethod
	def get_name() -> str:
		return "wander"

	@staticmethod
	def get_required_components() -> dict[str, Any]:
		return {
			"range": 0,
			"detection_radius": 0
		}


class WanderState(EntityState, Registrable):
	@staticmethod
	def get_registry_data() -> Type[RegistryData]:
		return WanderStateData

	def __init__(
			self,
			pos: pygame.Vector2,
			movement: Movement,
			level: "Level",
			entity_manager: EntityManager,
			model: HumanoidModel,
			data: dict[str, ...]
	):
		self.pos = pos
		self.level = level

		self.movement = movement

		self.wander_range = (int(-data["range"] * PIXEL_SCALE), int(data["range"] * PIXEL_SCALE))
		self.player_detection_radius = data["detection_radius"] * PIXEL_SCALE

		self.target = None
		self.find_target()

		self.time_since_target = 0.0
		self.time_to_new_target = 2.0

		self.model = model

		self.player_pos = entity_manager.get_entities_of_tag("player")[0].pos

	def find_target(self):
		random_target = (
			self.pos.x + random.randint(*self.wander_range),
			self.pos.y + random.randint(*self.wander_range)
		)

		tile = self.level.get_tile(random_target)
		if tile is not None:
			# if tile.sprite_sheet_name != "walls":
			self.target = pygame.Vector2(random_target)
			self.time_since_target = 0
		else:
			if self.level.get_room(random_target) is not None:
				self.target = pygame.Vector2(random_target)
				self.time_since_target = 0

	def update(self, delta: float):
		if self.target is not None:
			self.movement.move_in_direction(self.pos, self.target - self.pos, delta)
			self.model.switch_state("run")

			if self.pos.distance_to(self.target) < 20 or self.time_since_target > self.time_to_new_target:
				self.find_target()
				self.time_since_target = 0
				self.time_to_new_target = random.uniform(2, 4)
		else:
			self.find_target()

		self.time_since_target += delta

	def next_state(self) -> str:
		if self.pos.distance_to(self.player_pos) < self.player_detection_radius:
			return "attack"

		return ""
