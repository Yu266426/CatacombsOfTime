from typing import Optional

import pygame
import pygbase
# from pygame.examples.multiplayer_joystick import player
from pygbase.utils import get_angle_to

from data.modules.entities.items.item import Item
from data.modules.entities.entity_manager import EntityManager


class ItemSlot:
	def __init__(
			self,
			pos: pygame.Vector2,
			offset: tuple,
			entities: EntityManager,
			is_player: bool
	):
		self.pos = pos
		self.offset = pygame.Vector2(offset)
		self.offset_pos = self.pos + self.offset

		self.flip_x = False

		self.item: Optional[Item] = None

		self.entity_manager = entities

		self.is_player = is_player

	def removed(self):
		if self.item is not None:
			self.entity_manager.add_entity_to_remove(self.item)
			self.item = None

	def equip_item(self, item: Item):
		self.item = item
		self.item.added_to_slot(self.offset_pos)

		tags = ()
		if self.is_player:
			tags += ("from_player",)
		else:
			tags += ("from_enemy",)

		self.entity_manager.add_entity(self.item, tags=tags)

	def use_item(self):
		if self.item is not None:
			self.item.use()

	def update(self, target_pos: pygame.Vector2):
		if target_pos.x < self.pos.x:
			self.flip_x = True
			self.offset_pos.update(self.pos.x - self.offset.x, self.pos.y + self.offset.y)
		else:
			self.flip_x = False
			self.offset_pos.update(self.pos + self.offset)

		if self.item is not None:
			self.item.angle = get_angle_to(self.offset_pos, target_pos) % 360
			self.item.flip_x = self.flip_x

			if not self.item.check_durability():
				self.entity_manager.add_entity_to_remove(self.item)
				self.item = None

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera):
		if self.item is not None:
			self.item.draw(surface, camera)
