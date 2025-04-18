from typing import Any

from data.modules.base.registry.registrable import Registrable
from data.modules.base.registry.registry_data import RegistryData


class Registry[T: Registrable | RegistryData]:
	# name: (type, data)
	_required_data: dict[str, tuple[type, dict[str, Any]]] = {}

	@classmethod
	def register_type(cls, type_to_register: type[T]):
		if issubclass(type_to_register, Registrable):
			registry_data = type_to_register.get_registry_data()

			name = registry_data.get_name()
			required_components = registry_data.get_required_components()
		elif issubclass(type_to_register, RegistryData):
			name = type_to_register.get_name()
			required_components = type_to_register.get_required_components()
		else:
			raise ValueError(f"Type <{type_to_register}> cannot be registered")

		cls._required_data[name] = (type_to_register, required_components)

		# TODO: A little more handling of the "" and recursive cases
		pass

	@classmethod
	def get_required_data(cls, type_name: str) -> dict[str, ...]:
		"""
		:return: Shallow copy of data
		"""
		return cls._required_data[type_name][1].copy()

	@classmethod
	def get_type[B](cls, type_name: str) -> type[B]:
		if type_name not in cls._required_data:
			raise ValueError(f"Type <{type_name}> not in registered types")

		return cls._required_data[type_name][0]
