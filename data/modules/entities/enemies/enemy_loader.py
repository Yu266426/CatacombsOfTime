import json
import pathlib

import pygame

from data.modules.base.paths import ENEMY_DIR
from data.modules.base.registry.loader import Loader
from data.modules.base.registry.registry import Registry
from data.modules.base.utils import to_scaled_sequence
from data.modules.entities.enemies.enemy import Enemy
from data.modules.entities.entity_manager import EntityManager
from data.modules.level.level import Level


class EnemyLoader(Loader):
	# enemy_name: (enemy_type, health, hitbox, dict[animations, states])
	# animations: {animation_name: (sprite_sheet, start_index, length, speed)}
	# states: {state_name: (depends on state)}
	_enemy_data: dict[str, tuple[str, int, tuple[int, int], dict[str, ...]]] = {}

	@classmethod
	def _get_dir(cls) -> pathlib.Path:
		return ENEMY_DIR

	@classmethod
	def _init_file(cls, name: str, file_path: pathlib.Path):
		with open(file_path) as starter_file:
			starter_data = json.load(starter_file)

		enemy_type_name = starter_data["type"]
		required_data = Registry.get_required_data(enemy_type_name)

		data_to_save = {
			"type": enemy_type_name,
			"health": -1,
			"hitbox": [-1, -1],
		}

		data_to_save.update(required_data)

		cls._create_json_from_data(name, file_path, data_to_save)

	@classmethod
	def _load(cls, name: str, file_path: pathlib.Path):
		with open(file_path) as file:
			data = json.load(file)

		enemy_type = data["type"]
		health = data["health"]
		hitbox = to_scaled_sequence(data["hitbox"])
		enemy_data = {}

		# if "animations" in data:
		# 	animations_data = data["animations"]
		# 	animation_data = {}
		# 	for animation_name, animation in animations_data.items():
		# 		animation_data[animation_name] = (
		# 			animation["sprite_sheet"],
		# 			animation["start_index"],
		# 			animation["length"],
		# 			animation["speed"]
		# 		)
		#
		# 	enemy_data["animations"] = animation_data

		if "model" in data:
			enemy_data["model"] = data["model"]

		if "states" in data:
			enemy_data["states"] = data["states"]

		if "item_offset":
			enemy_data["item_offset"] = data["item_offset"]

		if "weapon" in data:
			enemy_data["weapon"] = data["weapon"]

		cls._enemy_data[name] = (
			enemy_type,
			health,
			hitbox,
			enemy_data
		)

	@classmethod
	def create_enemy(cls, enemy_name: str, pos: pygame.typing.Point, level: Level, entity_manager: EntityManager) -> "Enemy":
		enemy_data = cls._enemy_data[enemy_name]
		data_dict = enemy_data[3].copy()

		if "weapon" in data_dict:
			data_dict["weapon"] = Registry.get_type(data_dict["weapon"])(entity_manager, level)

		return Registry.get_type(enemy_data[0])(
			pos,
			level,
			entity_manager,
			enemy_data[2],  # Hitbox
			enemy_data[1],  # Health,
			data_dict  # Data
		)
