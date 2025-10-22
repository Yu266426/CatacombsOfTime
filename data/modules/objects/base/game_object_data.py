from typing import Any

from data.modules.base.registry.registry_data import RegistryData


class GameObjectData(RegistryData):
	@staticmethod
	def get_name() -> str:
		return "game_object_data"

	@staticmethod
	def get_required_components() -> dict[str, Any]:
		return {
			"hitbox": [0, 0],
			"behaviors": [],
			"tags": [],
		}
