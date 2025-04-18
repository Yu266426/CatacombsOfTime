from typing import Any, Type

import pygame
import pygbase

from data.modules.base.registry.registrable import Registrable
from data.modules.base.registry.registry_data import RegistryData
from data.modules.base.utils import to_scaled
from data.modules.entities.components.item_slot import ItemSlot
from data.modules.entities.enemies.enemy import Enemy
from data.modules.entities.entity_manager import EntityManager
from data.modules.entities.models.humanoid_model import HumanoidModel
from data.modules.entities.models.model_loader import ModelLoader
from data.modules.entities.states.entity_state import EntityState
from data.modules.entities.states.entity_state_manager import EntityStateManager
from data.modules.entities.states.melee_attack_state import MeleeAttackState
from data.modules.entities.states.stunned_state import StunnedState
from data.modules.entities.states.wander_state import WanderState
from data.modules.level.level import Level


class MeleeEnemyData(RegistryData):
	@staticmethod
	def get_name() -> str:
		return "melee"

	@staticmethod
	def get_required_components() -> dict[str, Any]:
		return {
			"model": "",
			"states": ["wander", "stunned", "melee_attack"],
			"item_offset": [0, 0],
			"weapon": ""
		}


class MeleeEnemy(Enemy, Registrable):
	@staticmethod
	def get_registry_data() -> Type[RegistryData]:
		return MeleeEnemyData

	def __init__(
			self,
			pos: pygame.typing.Point,
			level: Level,
			entity_manager: EntityManager,
			collider_size: tuple[int, int],
			health: int,
			data: dict[str, ...]
	):
		Enemy.__init__(self, pos, level, entity_manager, collider_size, health, data)

		self.flip_x = False
		self.model: HumanoidModel = ModelLoader.create_model(data["model"], self.pos)

		self.item_slot = ItemSlot(self.model.body_part.pos, data["item_offset"], entity_manager, False)

		state_data = data["states"]
		self.state_manager = EntityStateManager({
			"wander": WanderState(self.pos, self.movement, level, self.entity_manager, self.model, state_data["wander"]),
			"stunned": StunnedState(self.pos, self.movement, "wander", state_data["stunned"]),
			"attack": MeleeAttackState(self.pos, self.movement, self.entity_manager, self.item_slot, state_data["melee_attack"])
		}, "wander")

		self.player_pos = entity_manager.get_entities_of_tag("player")[0].pos

		self.lighting_manager: pygbase.LightingManager = pygbase.Common.get("lighting_manager")
		self.shadow = pygbase.Shadow(self.pos, to_scaled(3.5))

	def added(self):
		self.lighting_manager.add_shadow(self.shadow)
		self.item_slot.equip_item(self._data["weapon"])

	def removed(self):
		Enemy.removed(self)

		self.lighting_manager.remove_shadow(self.shadow)
		self.item_slot.removed()

	def damaged(self):
		self.state_manager.change_state("stunned")
		self.model.switch_state("idle")

	def update(self, delta: float):
		Enemy.update(self, delta)
		self.state_manager.update(delta)

		self.model.update(delta)

		self.flip_x = self.player_pos.x < self.pos.x
		self.item_slot.flip_x = self.flip_x
		self.model.flipped = self.flip_x
		self.model.direction = -1 if self.model.flipped else 1

		self.item_slot.update(self.player_pos)

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera):
		self.model.draw(surface, camera)
		self.item_slot.draw(surface, camera)

		pygbase.Debug.draw_rect(camera.world_to_screen_rect(self.collider.rect), "yellow")
