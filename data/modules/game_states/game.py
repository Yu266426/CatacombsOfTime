import pygame
import pygbase

from data.modules.base.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from data.modules.entities.entity_manager import EntityManager
from data.modules.entities.player import Player
from data.modules.level.level import Level, LevelGenerator


class Game(pygbase.GameState, name="game"):
	def __init__(self):
		super().__init__()
		self.entity_manager = EntityManager()
		self.particle_manager: pygbase.ParticleManager = pygbase.Common.get("particle_manager")
		self.lighting_manager: pygbase.LightingManager = pygbase.Common.get("lighting_manager")

		self.camera = pygbase.Camera(pos=(-SCREEN_WIDTH / 2, -SCREEN_HEIGHT / 2))

		room_separation = 21
		self.level: Level = LevelGenerator(20, self.entity_manager, room_separation, 1).generate_level()

		self.player = Player(((int(room_separation / 2) + 0.5) * TILE_SIZE, room_separation / 2 * TILE_SIZE), self.camera, self.entity_manager, self.level)
		self.entity_manager.add_entity(self.player)

		self.camera.set_pos(self.player.pos + (-SCREEN_WIDTH / 2, -SCREEN_HEIGHT / 2))

	def enter(self):
		pygbase.Common.set("camera", self.camera)

		self.particle_manager.clear()

	def exit(self):
		pygbase.Common.remove("camera")

		self.level.cleanup()
		self.entity_manager.clear_entities()

	def update(self, delta: float):
		self.entity_manager.update(delta)
		self.particle_manager.update(delta)
		self.lighting_manager.update(delta)

		self.camera.lerp_to_target(
			self.player.collider.rect.center
			- pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
			+ self.player.movement.velocity * 0.09
			, 8 * (delta ** 0.95)
		)
		# self.camera.set_pos(
		# 	self.player.collider.rect.center
		# 	- pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
		# )

		self.level.update(delta, self.player.pos)

		if pygbase.Input.key_just_pressed(pygame.K_ESCAPE):
			from data.modules.game_states.main_menu import MainMenu
			self.set_next_state(MainMenu())

	# pygbase.Events.post_event(pygame.QUIT)

	def draw(self, surface: pygame.Surface):
		surface.fill((0, 0, 0))

		self.level.draw(surface, self.camera)
		self.particle_manager.draw(surface, self.camera)
