import pygame
import pygbase

from data.modules.entities.components.boxcollider import BoxCollider
from data.modules.entities.components.item_slot import ItemSlot
from data.modules.entities.components.items.energy_sword import EnergySword
from data.modules.entities.components.movement import Movement
from data.modules.entities.entity import Entity
from data.modules.entities.entity_manager import EntityManager
from data.modules.map.level import Level


class Player(Entity):
	def __init__(self, pos, level: Level, entities: EntityManager, camera: pygbase.Camera):
		super().__init__(pos)

		self.current_state = "idle"

		self.animations = pygbase.AnimationManager([
			("idle", pygbase.Animation("player_idle_animation", 0, 1), 8),
			("run", pygbase.Animation("player_run_animation", 0, 2), 8)
		], "player_idle")

		self.collider = BoxCollider((70, 50)).link_pos(self.pos)

		self.input = pygame.Vector2()
		self.movement = Movement(5000, 10, level, self.collider)

		self.entities = entities

		self.item_slot = ItemSlot(self.pos, (25, -36), entities, camera)
		self.item_slot.equip_item(EnergySword(entities))

		self.camera = camera

	def get_inputs(self):
		self.input.x = pygbase.InputManager.get_key_pressed(pygame.K_d) - pygbase.InputManager.get_key_pressed(pygame.K_a)
		self.input.y = pygbase.InputManager.get_key_pressed(pygame.K_s) - pygbase.InputManager.get_key_pressed(pygame.K_w)
		if self.input.length() != 0:
			self.input.normalize_ip()
			self.animations.switch_state("run")
		else:
			self.animations.switch_state("idle")

	# if pygbase.InputManager.check_modifiers(pygame.KMOD_SHIFT):
	# 	self.movement.speed = 10000 * 2
	# else:
	# 	self.movement.speed = 10000

	def update(self, delta: float):
		self.get_inputs()

		self.movement.move_in_direction(self.pos, self.input, delta)

		self.animations.update(delta)

		self.item_slot.update(delta)

	def draw(self, screen: pygame.Surface, camera: pygbase.Camera):
		self.animations.draw_at_pos(screen, self.pos, camera, draw_pos="midbottom")
		self.item_slot.draw(screen, camera)
