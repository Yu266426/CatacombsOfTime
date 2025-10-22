import math
from typing import TYPE_CHECKING

import pygame
import pygbase

from data.modules.base.utils import to_scaled, to_scaled_sequence
from data.modules.entities.attacks.fireball import Fireball
from data.modules.entities.components.box_collider import BoxCollider
from data.modules.entities.components.health import Health
from data.modules.entities.components.interaction_controller import InteractionController
from data.modules.entities.components.item_slot import ItemSlot
from data.modules.entities.components.movement import Movement
from data.modules.entities.entity import Entity
from data.modules.entities.items.energy_sword import EnergySword
from data.modules.entities.models.model_loader import ModelLoader

if TYPE_CHECKING:
	from data.modules.entities.entity_manager import EntityManager
	from data.modules.entities.models.humanoid_model import HumanoidModel
	from data.modules.level.level import Level


class Player(Entity, tags=("player",)):
	def __init__(self, pos, camera: pygbase.Camera, entity_manager: EntityManager, level: Level):
		super().__init__(pos)
		self.entity_manager = entity_manager
		self.level = level

		self.flip_x = False

		self.y_offset = 0
		self.run_start_time = 0

		self.character_model: HumanoidModel = ModelLoader.create_model("player", self.pos)

		self.collider = BoxCollider(to_scaled_sequence((11.2, 8))).link_pos(self.pos)

		self.input = pygame.Vector2()
		self.movement = Movement(800, 10, level, self.collider)

		self.camera = camera

		self.lighting_manager: pygbase.LightingManager = pygbase.Common.get("lighting_manager")
		self.light = pygbase.Light(self.pos, 0.2, 300, 10, 1.2)
		self.light2 = pygbase.Light(self.pos, 0.5, 500, 20, 1.2)
		self.shadow = pygbase.Shadow(self.pos, to_scaled(3.26))

		self.interaction_controller = InteractionController(40, self)

		self.health = Health(10000)
		self.damage_timer = pygbase.Timer(0.6, True, False)

		self.item_slot = ItemSlot(self.character_model.body_part.pos, (4, 4.8), entity_manager, True)
		self.item_slot.equip_item(EnergySword(entity_manager, level))

	def added(self):
		self.lighting_manager.add_light(self.light)
		self.lighting_manager.add_light(self.light2)
		self.lighting_manager.add_shadow(self.shadow)

	def removed(self):
		self.lighting_manager.remove_light(self.light)
		self.lighting_manager.remove_light(self.light2)
		self.lighting_manager.remove_shadow(self.shadow)

	def damaged(self):
		pass

	def get_inputs(self):
		self.input.x = pygbase.Input.pressed("right") - pygbase.Input.pressed("left")
		self.input.y = pygbase.Input.pressed("down") - pygbase.Input.pressed("up")
		if self.input.length() != 0:
			self.input.normalize_ip()
			self.character_model.switch_state("run")
			self.run_start_time = pygame.time.get_ticks()

		else:
			self.character_model.switch_state("idle")

	def check_damaged(self):
		if self.damage_timer.done():
			damage_entities = self.entity_manager.get_entities_of_tag("damage")
			for entity in damage_entities:
				if "from_player" in entity.entity_tags:
					continue

				# TODO: Is NoQA really the answer?
				if self.collider.collides_with(entity.collider):
					# print(entity)
					self.health.damage(entity.damage)

					dir_vec = entity.pos - self.pos
					if dir_vec.length() != 0:
						dir_vec.normalize_ip()

					self.movement.velocity -= dir_vec * 2000

					self.damage_timer.start()

					self.damaged()
					break

		self.visible = self.damage_timer.done() or not math.sin(pygame.time.get_ticks() / 25) > 0

	def update(self, delta: float):
		self.damage_timer.tick(delta)

		self.get_inputs()

		# Debug
		if pygbase.Input.key_just_pressed(pygame.K_SPACE):
			self.movement.add_force(self.input, 5000)
		if pygbase.Input.mouse_just_pressed(2):
			mouse_world_pos = self.camera.screen_to_world(pygame.mouse.get_pos())
			angle = pygbase.utils.get_angle_to(self.pos - (0, 30), mouse_world_pos)
			self.entity_manager.add_entity(Fireball(
				self.pos - (0, 30),
				angle,
				to_scaled(128),
				min(400, self.pos.distance_to(mouse_world_pos)),
				30,
				90,
				10,
				self.level,
				self.entity_manager,
			), tags=("from_player",))
		# Debug end

		self.movement.move_in_direction(self.pos, self.input, delta)

		self.character_model.update(delta)
		if self.character_model.state == "run":
			self.y_offset = (math.sin(pygame.time.get_ticks() / 60) + 1) * 5
		else:
			self.y_offset = 0

		self.flip_x = pygame.mouse.get_pos()[0] < self.camera.world_to_screen(self.pos)[0]
		self.item_slot.flip_x = self.flip_x
		self.character_model.flipped = self.flip_x
		self.character_model.direction = math.copysign(1, self.input.x) if self.input.x != 0 else (-1 if self.flip_x else 1)

		if pygbase.Input.pressed("attack"):
			self.item_slot.use_item()

		self.item_slot.update(self.camera.screen_to_world(pygame.mouse.get_pos()))

		self.interaction_controller.update(self.entity_manager)

		self.check_damaged()

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera):
		self.character_model.draw(surface, camera)
		self.item_slot.draw(surface, camera)

		pygbase.Debug.draw_rect(camera.world_to_screen_rect(self.collider.rect), "yellow")

	def is_alive(self):
		return self.health.is_alive()
