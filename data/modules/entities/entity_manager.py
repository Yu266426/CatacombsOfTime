from collections import defaultdict
from typing import TYPE_CHECKING

from data.modules.base.constants import TILE_SIZE
from data.modules.base.utils import get_1d_tile_pos

if TYPE_CHECKING:
	from data.modules.entities.entity import Entity


class EntityManager:
	def __init__(self):
		self.entities: list[Entity] = []
		self.sorted_entities: dict[int, list[Entity]] = {}
		self.tagged_entities: dict[str, list[Entity]] = {}

		self.entities_to_remove = set()

	def clear_entities(self):
		for entity in self.entities:
			entity.removed()

			for tag in entity.tags:
				self.tagged_entities[tag].remove(entity)

				if len(self.tagged_entities[tag]) == 0:
					del self.tagged_entities[tag]

		self.entities.clear()
		self.sorted_entities.clear()

	def add_entity(self, entity: Entity, tags: tuple[str, ...] | None = None):
		self.entities.append(entity)
		entity.added()

		if tags is not None:
			entity.entity_tags += tags

		for tag in entity.entity_tags:
			self.tagged_entities.setdefault(tag, []).append(entity)

	def get_entities_of_tag(self, tag: str) -> list[Entity]:
		if tag in self.tagged_entities:
			return self.tagged_entities[tag]

		return []

	def get_entities(self, y_pos: int) -> list[Entity]:
		if y_pos in self.sorted_entities:
			return [entity for entity in self.sorted_entities[y_pos]]

		return []

	def update(self, delta: float):
		active_entities = []
		new_sorted_entities = defaultdict(list)

		for entity in self.entities:
			if not entity.is_alive():
				entity.removed()

				for tag in entity.tags:
					self.tagged_entities[tag].remove(entity)

					if len(self.tagged_entities[tag]) == 0:
						del self.tagged_entities[tag]
			else:
				if entity.active:
					entity.update(delta)

				y_pos = get_1d_tile_pos(entity.pos.y, TILE_SIZE)
				new_sorted_entities[y_pos].append(entity)

				active_entities.append(entity)

		for entities in new_sorted_entities.values():
			entities.sort(key=lambda e: e.pos.y * 7 + e.pos.x)

		self.entities[:] = active_entities[:]
		self.sorted_entities.clear()
		self.sorted_entities.update(new_sorted_entities)
