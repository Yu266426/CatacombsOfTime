from abc import ABC, abstractmethod
from typing import Type

from data.modules.base.registry.registry_data import RegistryData


class Registrable(ABC):
	@staticmethod
	@abstractmethod
	def get_registry_data() -> Type[RegistryData]:
		raise NotImplementedError("`get_registry_data` must be defined for Registrable")
