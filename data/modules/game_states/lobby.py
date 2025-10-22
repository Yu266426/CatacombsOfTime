import pygame
import pygbase

from data.modules.base.constants import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE
from data.modules.entities.entity_manager import EntityManager
from data.modules.entities.player import Player
from data.modules.level.level import Level


class Lobby(pygbase.GameState, name="lobby"):
	def __init__(self):
		super().__init__()

		self.entity_manager = EntityManager()
		self.particle_manager: pygbase.ParticleManager = pygbase.Common.get("particle_manager")
		self.lighting_manager: pygbase.LightingManager = pygbase.Common.get("lighting_manager")
		self.dialogue_manager: pygbase.DialogueManager = pygbase.Common.get("dialogue_manager")

		self.camera = pygbase.Camera()

		self.level = Level(self.entity_manager, 30, 0)
		self.level.add_room((0, 0), "lobby")

		self.player = Player((4.5 * TILE_SIZE, 6 * TILE_SIZE), self.camera, self.entity_manager, self.level)
		self.entity_manager.add_entity(self.player)

		pygbase.Events.add_handler("lobby", "start_game", self.start_game_callback)

	def enter(self):
		self.particle_manager.clear()

	def exit(self):
		self.level.cleanup()
		self.entity_manager.clear_entities()

		pygbase.Events.remove_handler(self.start_game_callback, "lobby", "start_game")

	def start_game_callback(self, _event: pygame.Event):
		from data.modules.game_states.game import Game
		self.set_next_state(Game())

	def update(self, delta: float):
		self.particle_manager.update(delta)
		self.lighting_manager.update(delta)
		self.dialogue_manager.update(delta)
		self.entity_manager.update(delta)

		self.level.update(delta, self.player.pos)

		if self.dialogue_manager.current_node != "":
			self.player.disable()
		else:
			self.player.enable()

		self.camera.lerp_to_target(self.player.collider.rect.center - pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), delta * 5)

		if pygbase.Input.key_just_pressed(pygame.K_ESCAPE):
			from data.modules.game_states.main_menu import MainMenu
			self.set_next_state(MainMenu())

	def draw(self, surface: pygame.Surface):
		surface.fill((0, 0, 0))

		self.level.draw(surface, self.camera)

		self.particle_manager.draw(surface, self.camera)
		self.dialogue_manager.draw(surface)
