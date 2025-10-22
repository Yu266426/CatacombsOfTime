import json
import logging
import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	import pathlib


class Loader(ABC):
	@classmethod
	@abstractmethod
	def _get_dir(cls) -> pathlib.Path:
		pass

	@classmethod
	def init(cls):
		directory = cls._get_dir()

		for file in os.listdir(directory):
			if "." not in file:
				continue

			name, extension = file.split(".")
			path = directory / file

			# Convert starter data and save into json
			if extension == "start":
				cls._init_file(name, path)

			# Loads the json
			elif extension == "json":
				cls._load(name, path)
			else:
				logging.warning(f'Non .start or .json file "{file}" found in {directory.name} directory')

	@classmethod
	def _create_json_from_data(cls, name: str, file_path: pathlib.Path, data: dict):
		# Save to .json file, and delete starter file
		json_file_path = cls._get_dir() / f"{name}.json"
		with open(json_file_path, "x") as json_file:
			json_file.write(json.dumps(data, indent=2))

		os.remove(file_path)

	@classmethod
	@abstractmethod
	def _init_file(cls, name: str, file_path: pathlib.Path):
		"""
		Processes any .start files in directory into default data to be saved in .json
		"""

	@classmethod
	@abstractmethod
	def _load(cls, name: str, file_path: pathlib.Path):
		"""
		Loads any .json files in directory
		"""
