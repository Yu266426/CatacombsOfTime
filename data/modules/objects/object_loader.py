import json
from typing import TYPE_CHECKING, ClassVar

import pygbase

from data.modules.base.paths import OBJECT_DIR
from data.modules.base.registry.loader import Loader
from data.modules.base.registry.registry import Registry
from data.modules.objects.base.game_object import GameObject

if TYPE_CHECKING:
	import pathlib

	import pygame


class ObjectLoader(Loader):
	# object_name: (object_type, sprite, hitbox, behaviour, tags) for static and animated
	# object_name: (object_type, object_class, tags) for custom
	object_data: ClassVar[dict[str, tuple]] = {}

	@classmethod
	def _get_dir(cls) -> pathlib.Path:
		return OBJECT_DIR

	@classmethod
	def _init_file(cls, _name: str, file_path: pathlib.Path):
		with open(file_path) as starter_file:
			starter_data = json.load(starter_file)

		object_type_name = starter_data["type"]
		object_required_data = Registry.get_required_data("game_object_data")

		data_to_save = {"type": object_type_name}
		data_to_save.update(object_required_data)

		if object_type_name == "static":
			image_required_data = Registry.get_required_data("image_data")
			data_to_save.update(image_required_data)

		elif object_type_name == "animated":
			animation_required_data = Registry.get_required_data("animation_data")
			data_to_save.update(animation_required_data)

		elif object_type_name == "custom":
			# No further processing
			pass

		else:
			raise ValueError(f"{file_path.name} has unsupported object type: {object_type_name}")

	@classmethod
	def _load(cls, _name: str, file_path: pathlib.Path):
		with open(file_path) as file:
			data = json.load(file)

		# Shared optional data
		hitbox = None
		behaviour = None
		tags = ()

		if "hitbox" in data and data["hitbox"] != [0, 0]:
			hitbox = data["hitbox"]

		# TODO: Make behavior do something
		if "behaviors" in data and data["behaviors"] != []:
			behaviour = data["behaviors"]

		if "tags" in data and data["tags"] != []:
			tags = tuple(data["tags"])

		# Type-dependent data
		object_name = file_path.stem
		object_type: str = data["type"]
		if object_type == "static":
			sprite_sheet_name = data["sprite_sheet"]

			cls.object_data[object_name] = (
				object_type,
				pygbase.Resources.get_resource("sprite_sheets", sprite_sheet_name).get_image(data["image_index"]),
				hitbox,
				behaviour,
				tags,
			)
		elif object_type == "animated":
			sprite_sheet_name = data["sprite_sheet"]

			cls.object_data[object_name] = (
				object_type,
				("sprite_sheets", sprite_sheet_name, data["animation_start_index"], data["animation_length"], data["animation_looping"]),
				hitbox,
				behaviour,
				tags,
			)
		elif object_type == "custom":
			cls.object_data[data["name"]] = (
				object_type,
				Registry.get_type(data["name"]),
				tags,
			)
		else:
			raise ValueError(f"{object_name} object file has invalid type <{type}>")

	@classmethod
	def create_object(cls, name: str, pos: pygame.typing.Point, is_pixel: bool = False) -> tuple[GameObject, tuple]:
		"""
		Creates an object based on inputs

		:param name: Name of object
		:param pos: Position to spawn object at
		:param is_pixel: If position is in tiles or pixels
		:return: tuple[object, tags]
		"""
		object_data = cls.object_data[name]
		if object_data[0] == "static":
			return GameObject(
				name,
				pos,
				is_pixel,
				object_data[1],  # Sprite
				custom_hitbox=object_data[2],
			), object_data[4]

		if object_data[0] == "animated":
			return (GameObject(
				name,
				pos,
				is_pixel,
				pygbase.Animation(*object_data[1]),  # Animation data
				custom_hitbox=object_data[2],
			), object_data[4])

		if object_data[0] == "custom":
			return object_data[1](pos, is_pixel), object_data[2]
		raise RuntimeError(f"Invalid object type for: {name}")

# class ObjectLoader:
# 	# object_name: (object_type, sprite, hitbox, behaviour, tags) for static and animated
# 	# object_name: (object_type, object_class, tags) for custom
# 	object_data: dict[str, tuple] = {}
#
# 	@classmethod
# 	def init(cls):
# 		for object_file in os.listdir(OBJECT_DIR):
# 			name, extension = object_file.split(".")
#
# 			if extension == "json":
# 				cls._load_object(name)
# 			else:
# 				logging.warning(f"Non .json file \"{object_file}\" found in objects directory")
#
# 		logging.info(f"Loaded {len(cls.object_data)} objects")
#
# 	@classmethod
# 	def _load_object(cls, object_name: str):
# 		json_path = OBJECT_DIR / f"{object_name}.json"
#
# 		with open(json_path) as json_file:
# 			data = json.load(json_file)
#
# 		# Shared optional data
# 		hitbox = None
# 		behaviour = None
# 		tags = ()
#
# 		if "hitbox" in data:
# 			hitbox = data["custom_hitbox"]
#
# 		# TODO: Make behavior do something
# 		if "behaviors" in data:
# 			behaviour = data["behaviors"]
#
# 		if "tags" in data:
# 			tags = tuple(data["tags"])
#
# 		# Type-dependent data
# 		object_type: str = data["type"]
# 		if object_type == "static":
# 			sprite_sheet_name = data["sprite_sheet"]
#
# 			cls.object_data[object_name] = (
# 				object_type,
# 				pygbase.Resources.get_resource("sprite_sheets", sprite_sheet_name).get_image(data["image_index"]),
# 				hitbox,
# 				behaviour,
# 				tags
# 			)
# 		elif object_type == "animated":
# 			sprite_sheet_name = data["sprite_sheet"]
#
# 			cls.object_data[object_name] = (
# 				object_type,
# 				("sprite_sheets", sprite_sheet_name, data["animation_start_index"], data["animation_length"], data["animation_looping"]),
# 				hitbox,
# 				behaviour,
# 				tags
# 			)
# 		elif object_type == "custom":
# 			cls.object_data[data["name"]] = (
# 				object_type,
# 				Registry.get_type(data["name"]),
# 				tags
# 			)
# 		else:
# 			raise ValueError(f"{object_name} object file has invalid type <{type}>")
#
# 	@classmethod
# 	def create_object(cls, name: str, pos: pygame.typing.Point, is_pixel: bool = False) -> tuple[GameObject, tuple[str, ...]]:
# 		"""
# 		Creates an object based on inputs
#
# 		:param name: Name of object
# 		:param pos: Position to spawn object at
# 		:param is_pixel: If position is in tiles or pixels
# 		:return: tuple[object, tags]
# 		"""
# 		object_data = cls.object_data[name]
# 		if object_data[0] == "static":
# 			return GameObject(
# 				name,
# 				pos,
# 				is_pixel,
# 				object_data[1],  # Sprite
# 				custom_hitbox=object_data[2]
# 			), object_data[4]
#
# 		elif object_data[0] == "animated":
# 			return (GameObject(
# 				name,
# 				pos,
# 				is_pixel,
# 				pygbase.Animation(*object_data[1]),  # Animation data
# 				custom_hitbox=object_data[2]
# 			), object_data[4])
#
# 		elif object_data[0] == "custom":
# 			return object_data[1](pos, is_pixel), object_data[2]
