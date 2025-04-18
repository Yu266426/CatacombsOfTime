import json
import logging
import pathlib

import pygame.typing

from data.modules.base.paths import MODEL_DIR
from data.modules.base.registry.loader import Loader
from data.modules.base.registry.registry import Registry
from data.modules.entities.models.character_model import CharacterModel
from data.modules.entities.models.model_part import ModelPart


class ModelLoader(Loader):
	# model_name: (model_type, model_data)
	_model_data: dict[str, tuple[str, dict]] = {}

	@classmethod
	def _get_dir(cls) -> pathlib.Path:
		return MODEL_DIR

	@classmethod
	def _init_file(cls, name: str, file_path: pathlib.Path):
		with open(file_path) as starter_file:
			starter_data = json.load(starter_file)

		# Done in two stages:
		# 1. Fill in the model parts needed to request for their type (static, animated)
		# 2. Fill in the remaining data

		model_type = starter_data["type"]
		required_data = Registry.get_required_data(model_type, CharacterModel)

		if "parts" not in starter_data:
			data_to_save = {}
			data_to_save.update(starter_data)

			data_to_save.update(required_data)

			with open(file_path, "w") as starter_file:
				starter_file.write(json.dumps(data_to_save, indent=2))
		else:
			data_to_save = {"type": model_type, "parts": {}}

			for part, part_type in starter_data["parts"].items():
				if part_type in ("static", "animated"):
					part_data = Registry.get_required_data(part_type, ModelPart)
				else:
					logging.warning(f"Unknown part type {part_type} for {part} in {name}")
					return

				# Custom handling of part data
				if model_type == "humanoid":
					if part == "body":
						part_data["layer"] = 2
					elif part == "leg":
						part_data["parent"] = "body"
						part_data["layer"] = 1

				data_to_save["parts"][part] = part_data

			cls._create_json_from_data(name, file_path, data_to_save)

	@classmethod
	def _load(cls, name: str, file_path: pathlib.Path):
		with open(file_path) as file:
			data = json.load(file)

		model_type = data["type"]

		cls._model_data[name] = (
			model_type,
			data
		)

	@classmethod
	def create_model(cls, model_name: str, pos: pygame.Vector2):
		model_data = cls._model_data[model_name]

		return Registry.get_type(model_data[0])(
			pos,
			model_data[1]
		)
