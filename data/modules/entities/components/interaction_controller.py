from typing import TYPE_CHECKING

import pygbase

from data.modules.base.utils import to_scaled

if TYPE_CHECKING:
	import pygame

	from data.modules.entities.entity import Entity
	from data.modules.entities.entity_manager import EntityManager


class InteractionController:
	def __init__(self, interaction_distance: float, parent: Entity):
		self.interaction_distance = to_scaled(interaction_distance)
		self.parent = parent

		self.interactable_entity: Entity | None = None

	def has_interactable(self) -> bool:
		return self.interactable_entity is not None

	def get_interactable(self) -> Entity | None:
		return self.interactable_entity

	def update(self, entity_manager: EntityManager):
		interactable_entities = entity_manager.get_entities_of_tag("interactable")
		if len(interactable_entities) > 0:
			closest_entity = interactable_entities[0]
			closest_distance = closest_entity.pos.distance_to(self.parent.pos)

			for interactable_entity in interactable_entities:
				distance = interactable_entity.pos.distance_to(self.parent.pos)

				if distance < closest_distance:
					closest_entity = interactable_entity
					closest_distance = distance

			if closest_distance < self.interaction_distance:
				self.interactable_entity = closest_entity
			else:
				self.interactable_entity = None

		if self.has_interactable():
			if pygbase.Input.pressed("interact"):
				self.get_interactable().interact(self.parent)

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera):
		# TODO: Draw indicator when an entity is interactable
		pass
