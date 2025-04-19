from typing import Optional

import pygame
import pygbase
from pygbase.utils import get_angle_to

from data.modules.base.utils import to_scaled
from data.modules.entities.entity_manager import EntityManager
from data.modules.entities.items.item import Item


class ItemSlot:
	def __init__(
			self,
			pos: pygame.Vector2,
			offset: tuple,
			entities: EntityManager,
			is_player: bool
	):
		self.pos = pos
		self.offset = to_scaled(pygame.Vector2(offset))
		self.offset_pos = self.pos + self.offset

		self.flip_x = False
		self.item_flip_x = False

		self.item: Optional[Item] = None

		self.entity_manager = entities

		self.is_player = is_player

	def removed(self):
		self.unequip_item()

	def equip_item(self, item: Item):
		self.item = item
		self.item.added_to_slot(self.offset_pos)

		tags = ()
		if self.is_player:
			tags += ("from_player",)
		else:
			tags += ("from_enemy",)

		self.entity_manager.add_entity(self.item, tags=tags)

	def unequip_item(self):
		if self.item is not None:
			self.item.alive = False
			self.item = None

	def use_item(self):
		if self.item is not None:
			self.item.use()

	def update(self, target_pos: pygame.Vector2):
		# Update offsets if we are flipped (set externally)
		if self.flip_x:
			self.offset_pos.update(self.pos.x - self.offset.x, self.pos.y + self.offset.y)
		else:
			self.offset_pos.update(self.pos + self.offset)

		# Flip item depending on target
		if target_pos.x < self.pos.x:
			self.item_flip_x = True
		else:
			self.item_flip_x = False

		# Update item
		if self.item is not None:
			self.item.angle = get_angle_to(self.offset_pos, target_pos) % 360
			self.item.flip_x = self.item_flip_x

			if not self.item.check_durability():
				self.unequip_item()

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera):
		if self.item is not None:
			self.item.draw(surface, camera)
