from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from data.modules.base.registry.registry_data import RegistryData


class Registrable(ABC):
	@staticmethod
	@abstractmethod
	def get_registry_data() -> type[RegistryData]:
		raise NotImplementedError("`get_registry_data` must be defined for Registrable")
