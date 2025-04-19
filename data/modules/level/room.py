import json
import logging
import os
import random
from typing import TYPE_CHECKING

import pygame
import pygbase

from data.modules.base.constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from data.modules.base.paths import ROOM_DIR
from data.modules.base.utils import one_if_even, get_tile_pos
from data.modules.entities.entity_manager import EntityManager
from data.modules.level.battle import Battle
from data.modules.level.tile import Tile
from data.modules.objects.base.game_object import GameObject
from data.modules.objects.object_loader import ObjectLoader

if TYPE_CHECKING:
	from data.modules.level.level import Level


class BaseRoom:
	def __init__(self, name: str, entity_manager: EntityManager, n_rows: int, n_cols: int, offset: tuple = (0, 0)):
		self.name = name

		self.n_rows = n_rows
		self.n_cols = n_cols

		self.tile_offset = offset
		# self.tile_offset = get_tile_pos(self.offset, (TILE_SIZE, TILE_SIZE))
		# self.offset = int(offset[0]), int(offset[1])
		self.offset = offset[0] * TILE_SIZE, offset[1] * TILE_SIZE

		self.objects: list[GameObject] = []

		self.entity_manager = entity_manager

	def check_bounds(self, pos: tuple[int, int]) -> bool:
		return 0 <= pos[0] < self.n_cols and 0 <= pos[1] < self.n_rows

	def get_object(self, pos: tuple, with_hitbox: bool = False):
		if not with_hitbox:
			for game_object in self.objects:
				if game_object.rect.collidepoint(pos[0], pos[1]):
					return game_object
		else:
			for game_object in self.objects:
				if game_object.hitbox.collidepoint(pos[0], pos[1]):
					return game_object

		return None

	def add_object(self, game_object: GameObject, tags: tuple[str, ...]):
		self.entity_manager.add_entity(game_object, tags=tags)
		self.objects.append(game_object)

	def remove_object(self, game_object: GameObject):
		if game_object is not None:
			self.objects.remove(game_object)
			game_object.alive = False

	def remove_objects(self):
		for game_object in self.objects:
			self.remove_object(game_object)


class LevelRoom(BaseRoom):
	def __init__(self, name: str, entity_manager: EntityManager, level: "Level", n_rows: int = 10, n_cols: int = 10, offset: tuple = (0, 0)):
		super().__init__(name, entity_manager, n_rows, n_cols, offset)

		self.level: "Level" = level

	def populate_tiles(self):
		"""
		Overridden by subclasses and called from level
		"""
		pass

	def add_tile(self, layer: int, tile_pos: tuple[int, int], tile: Tile):
		self.level.add_tile(layer, (tile_pos[0] + self.tile_offset[0], tile_pos[1] + self.tile_offset[1]), tile)

	def remove_tile(self, layer: int, tile_pos: tuple[int, int]):
		self.level.remove_tile(layer, (tile_pos[0] + self.tile_offset[0], tile_pos[1] + self.tile_offset[1]))


class Room(LevelRoom):
	def __init__(
			self,
			name: str,
			entity_manager: EntityManager,
			battle_name: str,
			level: "Level",
			gap_radius: int,
			n_rows: int = 10, n_cols: int = 10,
			offset: tuple = (0, 0),
			connections=(False, False, False, False),
			random_floor=True
	):
		self.connections = connections
		self.random_floor = random_floor
		self.gap_radius = gap_radius

		super().__init__(name, entity_manager, level, n_rows, n_cols, offset)

		self.battle_in_progress = False
		self.battle = Battle(battle_name, level, self, self.entity_manager) if battle_name != "" else None

		self.hallway_connection_tiles: list[tuple[int, int]] = []

		self.save_path = ROOM_DIR / f"{name}.json"
		if not os.path.isfile(self.save_path):
			raise ValueError(f"Room not found at: {self.save_path}")

		self.left_hallway_pos: tuple[int, int] | None = None
		self.right_hallway_pos: tuple[int, int] | None = None
		self.top_hallway_pos: tuple[int, int] | None = None
		self.bottom_hallway_pos: tuple[int, int] | None = None

	def populate_tiles(self):
		self.load()

		if self.random_floor:
			self.generate_floor()

		self.generate_walls(self.connections)

	def generate_walls(self, connections):
		"""
		Generates walls with gaps

		:param connections: Up, Down, Left, Right
		"""

		wall_sheet = pygbase.Resources.get_resource("sprite_sheets", "walls")

		# Horizontal
		y_mid_point = self.n_rows // 2 - one_if_even(self.n_rows)  # Slightly different midpoints for odd vs even sized rooms

		self.left_hallway_pos = (
			self.tile_offset[0],
			y_mid_point - self.gap_radius + self.tile_offset[1]
		)
		self.right_hallway_pos = (
			self.n_cols - 1 + self.tile_offset[0],
			y_mid_point - self.gap_radius + self.tile_offset[1]
		)

		# Left and Right
		for row in range(self.n_rows):
			if connections[2]:
				if row < y_mid_point - self.gap_radius or row > y_mid_point + self.gap_radius:
					self.add_tile(
						1, (0, row),
						Tile(
							"walls",
							random.randrange(0, wall_sheet.length),
							(self.offset[0], (row + 1) * TILE_SIZE + self.offset[1])
						)
					)
				else:
					self.remove_tile(1, (0, row))
					self.hallway_connection_tiles.append((0, row))
			else:
				self.add_tile(
					1, (0, row),
					Tile(
						"walls",
						random.randrange(0, wall_sheet.length),
						(self.offset[0], (row + 1) * TILE_SIZE + self.offset[1])
					)
				)

			if connections[3]:
				if row < y_mid_point - self.gap_radius or row > y_mid_point + self.gap_radius:
					self.add_tile(
						1, (self.n_cols - 1, row),
						Tile(
							"walls",
							random.randrange(0, wall_sheet.length),
							((self.n_cols - 1) * TILE_SIZE + self.offset[0], (row + 1) * TILE_SIZE + self.offset[1])
						)
					)
				else:
					self.remove_tile(1, (self.n_cols - 1, row))
					self.hallway_connection_tiles.append((self.n_cols - 1, row))
			else:
				self.add_tile(
					1, (self.n_cols - 1, row),
					Tile(
						"walls",
						random.randrange(0, wall_sheet.length),
						((self.n_cols - 1) * TILE_SIZE + self.offset[0], (row + 1) * TILE_SIZE + self.offset[1])
					)
				)

		# Vertical
		x_mid_point = self.n_cols // 2 - one_if_even(self.n_cols)

		self.top_hallway_pos = (
			x_mid_point - self.gap_radius + self.tile_offset[0],
			self.tile_offset[1]
		)
		self.bottom_hallway_pos = (
			x_mid_point - self.gap_radius + self.tile_offset[0],
			self.n_rows - 1 + self.tile_offset[1]
		)

		# Top and bottom
		for col in range(self.n_cols):
			if connections[0]:
				if col < x_mid_point - self.gap_radius or col > x_mid_point + self.gap_radius:
					self.add_tile(
						1, (col, 0),
						Tile(
							"walls",
							random.randrange(0, wall_sheet.length),
							(col * TILE_SIZE + self.offset[0], TILE_SIZE + self.offset[1])
						)
					)
				else:
					self.remove_tile(1, (col, 0))
					self.hallway_connection_tiles.append((col, 0))
			else:
				self.add_tile(
					1, (col, 0),
					Tile(
						"walls",
						random.randrange(0, wall_sheet.length),
						(col * TILE_SIZE + self.offset[0], TILE_SIZE + self.offset[1])
					)
				)

			if connections[1]:
				if col < x_mid_point - self.gap_radius or col > x_mid_point + self.gap_radius:
					self.add_tile(
						1, (col, self.n_rows - 1),
						Tile(
							"walls",
							random.randrange(0, wall_sheet.length),
							(col * TILE_SIZE + self.offset[0], self.n_rows * TILE_SIZE + self.offset[1])
						)
					)
				else:
					self.remove_tile(1, (col, self.n_rows - 1))
					self.hallway_connection_tiles.append((col, self.n_rows - 1))

			else:
				self.add_tile(
					1, (col, self.n_rows - 1),
					Tile(
						"walls",
						random.randrange(0, wall_sheet.length),
						(col * TILE_SIZE + self.offset[0], self.n_rows * TILE_SIZE + self.offset[1])
					)
				)

	def generate_floor(self):
		tiles_sheet = pygbase.Resources.get_resource("sprite_sheets", "tiles")
		for row in range(self.n_rows):
			for col in range(self.n_cols):
				self.add_tile(0, (col, row), Tile(
					"tiles",
					random.randrange(0, tiles_sheet.length),
					(col * TILE_SIZE + self.offset[0], (row + 1) * TILE_SIZE + self.offset[1])
				))

	def load(self):
		with open(self.save_path) as file:
			room_data: dict = json.load(file)

		self.n_rows = room_data["rows"]
		self.n_cols = room_data["cols"]

		# self.tiles = generate_3d_list(3, self.n_rows, self.n_cols)

		for layer, tiles in enumerate(room_data["tiles"]):
			for tile in tiles:
				row = tile["pos"][0] + self.offset[0]
				col = tile["pos"][1] + self.offset[1]
				self.add_tile(
					layer, (col, row),
					Tile(
						tile["image_info"][0],
						tile["image_info"][1],
						(col * TILE_SIZE + self.offset[0], (row + 1) * TILE_SIZE + self.offset[1])
					)
				)

		for object_data in room_data["objects"]:
			object_name = object_data["name"]
			pos = object_data["pos"]

			game_object, tags = ObjectLoader.create_object(object_name, (pos[0] + self.tile_offset[0], pos[1] + self.tile_offset[1]))

			self.add_object(game_object, tags=tags)

	def is_valid_spawn(self, tile_pos: tuple[int, int]):
		# TODO: Replace with a list of valid spawns that room tracks?
		return not self.level.check_is_tile(1, (tile_pos[0] + self.offset[0], tile_pos[1] + self.offset[1]))

	def generate_spawn_pos(self) -> tuple[float, float]:
		# Generate initial guess for spawn position
		spawn_pos = random.randrange(1, self.n_cols - 1), random.randrange(1, self.n_rows - 1)
		found = self.is_valid_spawn(spawn_pos)

		directions = ((0, 1), (1, 0), (0, -1), (-1, 0))
		steps_taken = 0
		step_size = 1

		# Find the nearest valid position
		while not found:
			for _ in range(2):  # Increase step size every 2 steps
				direction = directions[steps_taken % 4]
				spawn_pos = spawn_pos[0] + direction[0], spawn_pos[1] + direction[1]

				if self.is_valid_spawn(spawn_pos):
					found = True
					break

			step_size += 1

		return (spawn_pos[0] + random.uniform(0.45, 0.55)) * TILE_SIZE + self.offset[0], (spawn_pos[1] + random.uniform(0.5, 0.7)) * TILE_SIZE + self.offset[1]

	def activate_walls(self):
		wall_sheet = pygbase.Resources.get_resource("sprite_sheets", "walls")

		for tile_pos in self.hallway_connection_tiles:
			self.add_tile(1, tile_pos, Tile("walls", random.randrange(0, wall_sheet.length), (tile_pos[0] * TILE_SIZE + self.offset[0], (tile_pos[1] + 1) * TILE_SIZE + self.offset[1])))

	def deactivate_walls(self):
		for tile_pos in self.hallway_connection_tiles:
			self.remove_tile(1, tile_pos)

	def entered(self):
		"""
		Run when player enters more than 1 tile into the room (outer tiles are walls)
		"""

		if self.battle is not None and not self.battle.completed:
			if not self.battle.completed:
				self.battle_in_progress = True

				self.activate_walls()

	def exited(self):
		pass

	def update(self, delta: float):
		for game_object in self.objects:
			game_object.update(delta)

		if self.battle_in_progress:
			battle_done = self.battle.update()

			if battle_done:
				self.battle_in_progress = False
				self.deactivate_walls()


class EditorRoom(BaseRoom):
	def __init__(self, name: str, entity_manager: EntityManager, n_rows: int = 10, n_cols: int = 10):
		super().__init__(name, entity_manager, n_rows, n_cols)

		# layer[0: Ground, 1: Player | Walls, 2: Above]
		self.tiles: dict[int, dict[tuple[int, int], Tile]] = {}

		# New room
		self.save_path = os.path.join(ROOM_DIR, f"{name}.json")
		if not os.path.isfile(self.save_path):
			logging.debug("Creating new editor room")
		else:
			self.load()

	def check_is_tile(self, layer: int, pos: tuple[int, int]) -> bool:
		return layer in self.tiles and pos in self.tiles[layer]

	def get_tile(self, layer: int, pos: tuple[int, int], with_offset: bool = True) -> Tile | None:
		if with_offset:
			pos = pos[0] - self.tile_offset[0], pos[1] - self.tile_offset[1]

		if self.check_is_tile(layer, pos):
			return self.tiles[layer][pos]

		return None

	def add_tile(self, layer: int, pos: tuple[int, int], tile: Tile):
		assert tile is not None

		if self.check_bounds(pos):
			self.tiles.setdefault(layer, {})[pos] = tile

	def remove_tile(self, layer: int, pos: tuple[int, int]):
		if self.check_is_tile(layer, pos):
			del self.tiles[layer][pos]

			if len(self.tiles[layer].values()) == 0:
				del self.tiles[layer]

	def load(self):
		with open(self.save_path) as file:
			room_data: dict = json.load(file)

		self.n_rows = room_data["rows"]
		self.n_cols = room_data["cols"]

		# self.tiles = generate_3d_list(3, self.n_rows, self.n_cols)

		for level, tiles in enumerate(room_data["tiles"]):
			for tile in tiles:
				row = tile["pos"][0]
				col = tile["pos"][1]
				self.add_tile(level, (col, row), Tile(tile["image_info"][0], tile["image_info"][1], (col * TILE_SIZE, (row + 1) * TILE_SIZE)))

		for game_object in room_data["objects"]:
			object_type = game_object["name"]
			pos = game_object["pos"]

			game_object, tags = ObjectLoader.create_object(object_type, pos)
			self.add_object(game_object, tags)

	def save(self):
		data = {
			"rows": self.n_rows,
			"cols": self.n_cols,
			"tiles": [[], [], []],
			"objects": []
		}

		for level, level_data in self.tiles.items():
			for pos, tile in level_data.items():
				tile_data = {
					"pos": pos,
					"image_info": [tile.sprite_sheet_name, tile.image_index],
				}
				data["tiles"][level].append(tile_data)

		for game_object in self.objects:
			data["objects"].append({
				"name": game_object.name,
				"pos": game_object.tile_pos
			})

		with open(self.save_path, "w") as file:
			file.write(json.dumps(data))

		logging.info("Level Saved")

	def draw_tile(self, layer: int, pos: tuple[int, int], display: pygame.Surface, camera: pygbase.Camera, with_offset: bool = False):
		if with_offset:
			pos = pos[0] - self.tile_offset[0], pos[1] - self.tile_offset[1]

		# print(pos, self.check_is_tile(layer, pos), self.get_tile(layer, pos))
		if self.check_is_tile(layer, pos):
			self.get_tile(layer, pos, with_offset=False).draw(display, camera)

	def draw_room_to_surface(self, surface: pygame.Surface):
		surface_size = surface.get_size()

		room_surface = pygame.Surface((self.n_cols * TILE_SIZE, self.n_rows * TILE_SIZE), flags=pygame.SRCALPHA)
		temp_camera = pygbase.Camera()

		for layer in range(len(self.tiles)):
			for row in range(self.n_rows):
				for col in range(self.n_cols):
					self.draw_tile(layer, (col, row), room_surface, temp_camera)

		for game_object in self.objects:
			game_object.draw(room_surface, temp_camera)

		pygame.transform.scale(room_surface, surface_size, surface)

	def draw(self, screen: pygame.Surface, camera: pygbase.Camera):
		top_left: tuple[int, int] = get_tile_pos((camera.pos.x - self.offset[0], camera.pos.y - self.offset[1]), (TILE_SIZE, TILE_SIZE))
		bottom_right: tuple[int, int] = get_tile_pos((camera.pos.x + SCREEN_WIDTH - self.offset[0], camera.pos.y + SCREEN_HEIGHT - self.offset[1]), (TILE_SIZE, TILE_SIZE))

		top_left = top_left[0], top_left[1]
		bottom_right = bottom_right[0] + 1, bottom_right[1] + 2

		for layer in self.tiles.keys():
			for row in range(top_left[1], bottom_right[1]):
				for col in range(top_left[0], bottom_right[0]):
					self.draw_tile(layer, (col, row), screen, camera)

		for game_object in self.objects:
			game_object.draw(screen, camera)


class Hallway(LevelRoom):
	def __init__(self, entity_manager: EntityManager, level: "Level", n_rows: int, n_cols: int, horizontal: bool, offset: tuple = (0, 0)):
		super().__init__("", entity_manager, level, n_rows, n_cols, offset)

		self.horizontal = horizontal

	def populate_tiles(self):
		self.create()

	def create(self):
		tiles_sheet = pygbase.Resources.get_resource("sprite_sheets", "tiles")
		walls_sheet = pygbase.Resources.get_resource("sprite_sheets", "walls")

		if self.horizontal:
			# Create floor
			for row in range(self.n_rows - 2):
				row = row + 1
				for col in range(self.n_cols):
					self.add_tile(0, (col, row), Tile(
						"tiles",
						random.randrange(0, tiles_sheet.length),
						(col * TILE_SIZE + self.offset[0], (row + 1) * TILE_SIZE + self.offset[1])
					))

			# Create walls
			for col in range(self.n_cols):
				self.add_tile(1, (col, 0), Tile(
					"walls",
					random.randrange(0, walls_sheet.length),
					(col * TILE_SIZE + self.offset[0], TILE_SIZE + self.offset[1])
				))

				self.add_tile(1, (col, self.n_rows - 1), Tile(
					"walls",
					random.randrange(0, walls_sheet.length),
					(col * TILE_SIZE + self.offset[0], self.n_rows * TILE_SIZE + self.offset[1])
				))


		else:
			# Create floor
			for row in range(self.n_rows):
				for col in range(self.n_cols - 2):
					col = col + 1

					self.add_tile(0, (col, row), Tile(
						"tiles",
						random.randrange(0, tiles_sheet.length),
						(col * TILE_SIZE + self.offset[0], (row + 1) * TILE_SIZE + self.offset[1])
					))

			# Create walls
			for row in range(self.n_rows):
				self.add_tile(1, (0, row), Tile(
					"walls",
					random.randrange(0, walls_sheet.length),
					(self.offset[0], (row + 1) * TILE_SIZE + self.offset[1])
				))

				self.add_tile(1, (self.n_cols - 1, row), Tile(
					"walls",
					random.randrange(0, walls_sheet.length),
					((self.n_cols - 1) * TILE_SIZE + self.offset[0], (row + 1) * TILE_SIZE + self.offset[1])
				))
