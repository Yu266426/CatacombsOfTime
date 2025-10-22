import logging
from collections import deque
from typing import TYPE_CHECKING

from data.modules.entities.models.model_part import ImageModelPart

if TYPE_CHECKING:
	import pygame
	import pygbase


class CharacterModel:
	def __init__(self, pos: pygame.Vector2, data: dict):
		self.pos = pos  # Reference

		self.parts: dict[str, ImageModelPart] = {}

		part_queue = deque(data["parts"].keys())
		while len(part_queue) > 0:
			part = part_queue.popleft()
			part_data = data["parts"][part]
			part_type = part_data["type"]
			parent = part_data["parent"]

			if parent != "" and part_data["parent"] not in self.parts:
				part_queue.append(part)
				continue

			parent_pos = self.pos if parent == "" else self.parts[part_data["parent"]].pos

			if part_type == "static":
				part_object = ImageModelPart(parent_pos, part_data)
			elif part_type == "animated":
				continue
			else:
				logging.warning(f"Unknown part type {part} -> {part_type} in character model")
				continue

			self.parts[part] = part_object

		# Sort body parts
		self.parts = {key: value for key, value in sorted(self.parts.items(), key=self._part_sort_key)}

	@staticmethod
	def _part_sort_key(element) -> int:
		return element[1].layer

	def update(self, _delta: float):
		for part in self.parts.values():
			part.update()

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera):
		for part in self.parts.values():
			part.draw(surface, camera)
