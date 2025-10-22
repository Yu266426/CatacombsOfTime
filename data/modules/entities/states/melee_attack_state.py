import random
from typing import TYPE_CHECKING, Any

import pygame
import pygbase.utils

from data.modules.base.constants import PIXEL_SCALE
from data.modules.base.registry.registrable import Registrable
from data.modules.base.registry.registry_data import RegistryData
from data.modules.entities.attacks.sword_swing import SwordSwing
from data.modules.entities.states.entity_state import EntityState

if TYPE_CHECKING:
	from data.modules.entities.components.item_slot import ItemSlot
	from data.modules.entities.components.movement import Movement
	from data.modules.entities.entity_manager import EntityManager


class MeleeAttackStateData(RegistryData):
	@staticmethod
	def get_name() -> str:
		return "melee_attack"

	@staticmethod
	def get_required_components() -> dict[str, Any]:
		return {
			"max_radius": 0.0,
			"attack_cooldown": 0.0,
			"attack_range": 0,
		}


class MeleeAttackState(EntityState, Registrable):
	@staticmethod
	def get_registry_data() -> type[RegistryData]:
		return MeleeAttackStateData

	def __init__(
			self,
			pos: pygame.Vector2,
			movement: Movement,
			entity_manager: EntityManager,
			item_slot: ItemSlot,
			data: dict[str, ...],
	):
		self.pos = pos
		self.movement = movement

		self.entity_manger = entity_manager

		self.item_slot = item_slot

		self.player_pos = entity_manager.get_entities_of_tag("player")[0].pos

		self.max_radius = data["max_radius"] * PIXEL_SCALE
		self.attack_range = data["attack_range"] * PIXEL_SCALE

		self.attack = SwordSwing
		self.attack_cooldown = pygbase.Timer(data["attack_cooldown"], True, False)

		self.current_direction = pygame.Vector2(self.movement.velocity)
		if self.current_direction.length() == 0:
			self.current_direction.update(1, 0)
			self.current_direction.rotate_ip(random.uniform(0, 360))

	def update(self, delta: float):
		self.attack_cooldown.tick(delta)

		# Attack
		if self.attack_cooldown.done():
			self.item_slot.use_item()
			self.attack_cooldown.start()

		# Movement
		offset_to_player = self.player_pos - self.pos
		dist_to_player = offset_to_player.length()

		if offset_to_player.length() != 0:
			offset_to_player.normalize_ip()

		if dist_to_player < self.attack_range:
			angle = self.current_direction.angle_to(-offset_to_player)
			if angle > 180:
				angle -= 380
			self.current_direction.rotate_ip(angle * delta)
		else:
			angle = self.current_direction.angle_to(offset_to_player)
			if angle > 180:
				angle -= 380
			self.current_direction.rotate_ip(angle * delta)

		self.movement.move_in_direction(self.pos, self.current_direction, delta)

	def next_state(self) -> str:
		if self.pos.distance_to(self.player_pos) > self.max_radius:
			return "wander"

		return ""
