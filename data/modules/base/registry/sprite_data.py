from typing import Any

from data.modules.base.registry.registry_data import RegistryData


class AnimationData(RegistryData):
	@staticmethod
	def get_name() -> str:
		return "animation_data"

	@staticmethod
	def get_required_components() -> dict[str, Any]:
		return {
			"sprite_sheet": "",
			"start_index": 0,
			"length": 0,
			"speed": 0,
		}


class ImageData(RegistryData):
	@staticmethod
	def get_name() -> str:
		return "image_data"

	@staticmethod
	def get_required_components() -> dict[str, Any]:
		return {
			"sprite_sheet": "",
			"index": 0,
		}
