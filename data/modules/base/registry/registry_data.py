from abc import ABC, abstractmethod
from typing import Any


class RegistryData(ABC):
	@staticmethod
	@abstractmethod
	def get_name() -> str:
		raise NotImplementedError("`get_name` must be defined for RegistryData")

	@staticmethod
	@abstractmethod
	def get_required_components() -> dict[str, Any]:
		raise NotImplementedError("`get_required_component` must be defined for RegistryData")
