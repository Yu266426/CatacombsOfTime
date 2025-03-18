import gc
import json
import logging
import os
import random
from collections import deque

import pygame
import pygbase

from data.modules.base.constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from data.modules.base.paths import ROOM_DIR, BATTLE_DIR
from data.modules.base.utils import get_tile_pos, one_if_even
from data.modules.entities.entity_manager import EntityManager
from data.modules.level.room import Room, Hallway
from data.modules.level.tile import Tile


class Level:
	def __init__(self, entity_manager: EntityManager, room_separation: int, wall_gap_radius: int):
		self.entity_manager = entity_manager
		self.particle_manager: pygbase.ParticleManager = pygbase.Common.get("particle_manager")
		self.lighting_manager: pygbase.LightingManager = pygbase.Common.get("lighting_manager")

		# TODO: Rework to separate tiles from rooms
		# A game room is responsible for its location, loading the tiles, and special tiles
		# The level is responsible for feeding collision data, rendering tiles, etc.

		# layer[0: Ground, 1: Player | Walls, 2: Above]
		self.tiles: dict[int, dict[tuple[int, int], Tile]] = {}

		self.rooms: dict[tuple[int, int], Room] = {}
		self.connections = {}

		self.room_separation = room_separation
		self.wall_gap_radius = wall_gap_radius

		self.prev_player_room_pos = None

	def cleanup(self):
		"""
		Removes objects from rooms
		"""

		for room in self.rooms.values():
			room.remove_objects()

	def check_is_tile(self, layer: int, pos: tuple[int, int]) -> bool:
		return layer in self.tiles and pos in self.tiles[layer]

	def add_tile(self, layer: int, tile_pos: tuple[int, int], tile: Tile):
		assert tile is not None
		# logging.debug(f"Adding tile at {layer}, {tile_pos} with position {tile.rect}")
		self.tiles.setdefault(layer, {})[tile_pos] = tile

	def remove_tile(self, layer: int, tile_pos: tuple[int, int]):
		if self.check_is_tile(layer, tile_pos):
			del self.tiles[layer][tile_pos]

			if len(self.tiles[layer].values()) == 0:
				del self.tiles[layer]

	def get_tile(self, pos: pygame.Vector2 | tuple[float, float], layer: int = 1) -> Tile | None:
		tile_pos = get_tile_pos(pos, (TILE_SIZE, TILE_SIZE))

		if not self.check_is_tile(layer, tile_pos):
			return None

		return self.tiles[layer][tile_pos]

	def get_tile_at_tile_pos(self, tile_pos: tuple[int, int], layer: int = 1) -> Tile | None:
		if not self.check_is_tile(layer, tile_pos):
			return None

		return self.tiles[layer][tile_pos]

	def add_room(self, room_pos: tuple[int, int], room_name: str, battle_name: str = ""):
		room = Room(
			room_name,
			self.entity_manager,
			battle_name,
			self, self.wall_gap_radius,
			offset=(
				room_pos[0] * self.room_separation,
				room_pos[1] * self.room_separation
			)
		)

		self.rooms[room_pos] = room
		room.populate_tiles()
		return room

	def add_room_ex(self, room_pos: tuple[int, int], room_name: str, connections: tuple[bool, bool, bool, bool], battle_name: str, room_data: dict):
		offset = (
			(self.room_separation - room_data["cols"]) // 2,
			(self.room_separation - room_data["rows"]) // 2
		)

		odd_sep_offset = (0, 0)
		if self.room_separation % 2 != 0:
			odd_sep_offset = (
				one_if_even(room_data["cols"]),
				one_if_even(room_data["rows"])
			)

		room = Room(
			room_name,
			self.entity_manager,
			battle_name,
			self, self.wall_gap_radius,
			offset=(
				room_pos[0] * self.room_separation + offset[0] + odd_sep_offset[0],
				room_pos[1] * self.room_separation + offset[1] + odd_sep_offset[1]
			),
			connections=connections
		)

		self.rooms[room_pos] = room
		room.populate_tiles()
		return room

	def add_hallway(self, room_pos: tuple[int, int], connected_room_pos: tuple[int, int], room: Room, connecting_room: Room):
		"""

		:param room_pos: Current room tile position
		:param connected_room_pos: Room tile position of connecting room
		:param room: Current Room object
		:param connecting_room: Connecting Room object
		"""

		# logging.debug(f"{room_pos} {room.n_cols, room.n_rows} -> {connected_room_pos} {connecting_room.n_cols, connecting_room.n_rows}:")
		# logging.debug(f"{room.tile_offset} | {connecting_room.tile_offset}")
		# logging.debug(f"{room.left_hallway_pos}, {room.right_hallway_pos}, {room.top_hallway_pos}, {room.bottom_hallway_pos}")
		# logging.debug(f"{connecting_room.left_hallway_pos}, {connecting_room.right_hallway_pos}, {connecting_room.top_hallway_pos}, {connecting_room.bottom_hallway_pos}")

		# Horizontal connection
		if room_pos[1] == connected_room_pos[1]:
			wall_gap = self.wall_gap_radius * 2 + 1

			# Left
			if connected_room_pos[0] < room_pos[0]:
				width = room.left_hallway_pos[0] - connecting_room.right_hallway_pos[0] - 1
				offset = (
					connecting_room.right_hallway_pos[0] + 1,
					connecting_room.right_hallway_pos[1] - 1
				)
				# logging.debug(f"Spawning left hallway size {width}, {wall_gap} at {offset}")
				Hallway(
					self.entity_manager, self,
					wall_gap + 2,
					width,
					True,
					offset
				).populate_tiles()

			# Right
			if room_pos[0] < connected_room_pos[0]:
				width = connecting_room.left_hallway_pos[0] - room.right_hallway_pos[0] - 1
				offset = (
					room.right_hallway_pos[0] + 1,
					room.right_hallway_pos[1] - 1
				)
				# logging.debug(f"Spawning right hallway size {width}, {wall_gap} at {offset}")
				Hallway(
					self.entity_manager, self,
					wall_gap + 2,
					width,
					True,
					offset
				).populate_tiles()

		# Vertical Connection
		if room_pos[0] == connected_room_pos[0]:
			wall_gap = self.wall_gap_radius * 2 + 1

			# Top
			if connected_room_pos[1] < room_pos[1]:
				height = room.top_hallway_pos[1] - connecting_room.bottom_hallway_pos[1] - 1
				offset = (
					connecting_room.bottom_hallway_pos[0] - 1,
					connecting_room.bottom_hallway_pos[1] + 1
				)
				# logging.debug(f"Spawning top hallway size {height}, {wall_gap} at {offset}")
				Hallway(
					self.entity_manager, self,
					height,
					wall_gap + 2,
					False,
					offset
				).populate_tiles()

			# Bottom
			if room_pos[1] < connected_room_pos[1]:
				height = connecting_room.top_hallway_pos[1] - room.bottom_hallway_pos[1] - 1
				offset = (
					room.bottom_hallway_pos[0] - 1,
					room.bottom_hallway_pos[1] + 1
				)
				# logging.debug(f"Spawning bottom hallway size {height}, {wall_gap} at {offset}")
				Hallway(
					self.entity_manager, self,
					height,
					wall_gap + 2,
					False,
					offset
				).populate_tiles()

	def get_room(self, pos: tuple[float, float] | pygame.Vector2) -> Room | None:
		"""
		:param pos: Position in pixels
		:return: Room | None
		"""
		room_pos = get_tile_pos(pos, (self.room_separation * TILE_SIZE, self.room_separation * TILE_SIZE))

		return self.rooms.get(room_pos)

	def get_room_from_room_pos(self, room_pos: tuple[int, int]) -> Room | None:
		return self.rooms.get(room_pos)

	def update(self, delta: float, player_pos: pygame.Vector2):
		player_room_pos = get_tile_pos(player_pos, (self.room_separation * TILE_SIZE, self.room_separation * TILE_SIZE))
		current_room = self.get_room_from_room_pos(player_room_pos)
		if current_room is None:
			return

		player_room_tile_pos = get_tile_pos(player_pos, (TILE_SIZE, TILE_SIZE))
		player_room_tile_pos = player_room_tile_pos[0] - current_room.tile_offset[0], player_room_tile_pos[1] - current_room.tile_offset[1]

		# print(player_room_tile_pos, current_room.n_cols, current_room.n_rows)

		# Call enter or exit for the respective rooms
		if not self.prev_player_room_pos and 1 <= player_room_tile_pos[0] < current_room.n_cols and 1 <= player_room_tile_pos[1] < current_room.n_rows - 1:
			self.prev_player_room_pos = player_room_pos

			current_room.entered()
		elif self.prev_player_room_pos != player_room_pos and 1 <= player_room_tile_pos[0] < current_room.n_cols - 1 and 1 <= player_room_tile_pos[1] < current_room.n_rows - 1:
			current_room.entered()
			self.get_room_from_room_pos(self.prev_player_room_pos).exited()

			self.prev_player_room_pos = player_room_pos

		# Update the current room
		self.get_room(player_pos).update(delta)  # Could replace with current room?

	def draw_tile(self, layer: int, tile_pos: tuple[int, int], surface: pygame.Surface, camera: pygbase.Camera):
		# room = self.get_room((pos[0] * TILE_SIZE, pos[1] * TILE_SIZE))
		#
		# if room is not None:
		# 	room.draw_tile(level, pos, display, camera, with_offset=True)
		tile = self.get_tile_at_tile_pos(tile_pos, layer)
		if tile is not None:
			tile.draw(surface, camera)

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera):
		top_left = get_tile_pos(camera.pos, (TILE_SIZE, TILE_SIZE))
		bottom_right = get_tile_pos(camera.pos + pygame.Vector2(SCREEN_WIDTH, SCREEN_HEIGHT), (TILE_SIZE, TILE_SIZE))
		top_left = top_left[0], top_left[1]
		bottom_right = bottom_right[0] + 2, bottom_right[1] + 2

		for layer in range(0, 3):
			for row in range(top_left[1], bottom_right[1]):
				for col in range(top_left[0], bottom_right[0]):
					self.draw_tile(layer, (col, row), surface, camera)

				if layer == 1:
					entities = self.entity_manager.get_entities(row)
					for entity in entities:
						if entity.visible:
							entity.draw(surface, camera)

			if layer == 0:
				self.lighting_manager.draw_shadows(surface, camera)

		self.lighting_manager.draw_lights(surface, camera)


class LevelGenerator:
	def __init__(self, depth: int, entity_manager: EntityManager, room_separation: int, wall_gap_radius: int):
		self.depth: int = depth
		self.entity_manager = entity_manager
		self.room_separation = room_separation
		self.wall_gap_radius = wall_gap_radius

		# Room data
		self.rooms: dict[str, dict] = {}
		self.room_names: list[str] = []
		self._load_room_data()

		# Battle data
		self.battle_names: list[str] = []
		self._load_battle_data()

		# Room graph
		self.rooms_to_generate: set[tuple[int, int]] = set()
		self.connection_data: dict[tuple[int, int], list[tuple[int, int]]] = {}
		self.end_rooms: list[tuple[int, int]] = []
		self.room_queue: deque[tuple[tuple[int, int], int]] = deque()  # Position, depth

		# Hallway graph
		self.hallway_connections: dict[tuple[int, int], list[tuple[int, int]]] = {}
		self.visited_connections: set[tuple[int, int]] = set()

		# Rooms
		self.generated_rooms: dict[tuple[int, int], str] = {}  # {room_pos: room_name}

		# Level
		self.level = Level(self.entity_manager, self.room_separation, self.wall_gap_radius)

	def _load_room_data(self):
		for _, _, file_names in os.walk(ROOM_DIR):
			for file_name in file_names:
				name = file_name[:-5]  # Remove .json

				# Ensure only rooms of correct size
				with open(ROOM_DIR / file_name) as room_file:
					room_data = json.load(room_file)
					if room_data["rows"] > self.room_separation or room_data["cols"] > self.room_separation:
						continue

					self.rooms[name] = room_data

				# Ignore special rooms
				if name not in ("lobby", "start", "start2"):
					self.room_names.append(name)

	def _load_battle_data(self):
		for _, _, file_names in os.walk(BATTLE_DIR):
			for file_name in file_names:
				name = file_name[:-5]  # Remove .json

				self.battle_names.append(name)

	def _add_connection(self, start: tuple[int, int], end: tuple[int, int]):
		if start not in self.connection_data:
			self.connection_data[start] = []
		self.connection_data[start].append(end)

		if end not in self.connection_data:
			self.connection_data[end] = []
		self.connection_data[end].append(start)

	def _get_connections(self, pos: tuple[int, int]) -> tuple[bool, bool, bool, bool]:
		top, bottom, left, right = False, False, False, False

		if pos not in self.connection_data:
			return top, bottom, left, right

		for _connection in self.connection_data[pos]:
			if _connection[0] == pos[0] and _connection[1] == pos[1] - 1:
				top = True
			elif _connection[0] == pos[0] and _connection[1] == pos[1] + 1:
				bottom = True
			elif _connection[0] == pos[0] - 1 and _connection[1] == pos[1]:
				left = True
			elif _connection[0] == pos[0] + 1 and _connection[1] == pos[1]:
				right = True

		return top, bottom, left, right

	def _generate_room_graph(self):
		# Directions for generation
		directions = [
			(1, 0),
			(-1, 0),
			(0, 1),
			(0, -1)
		]

		# Room generation
		# Add start room
		self.rooms_to_generate.add((0, 0))

		# Start in all directions
		for direction in directions:
			self.rooms_to_generate.add(direction)
			self.room_queue.append((direction, 1))
			self._add_connection((0, 0), direction)

		while len(self.room_queue) > 0:
			# Get room info, and move to end of queue
			room_info = self.room_queue.popleft()
			room_pos = room_info[0]
			room_depth = room_info[1]

			if room_depth > self.depth:
				continue

			# Get available directions
			available_directions = []
			for direction in directions:
				new_pos = (room_pos[0] + direction[0], room_pos[1] + direction[1])
				if new_pos not in self.rooms_to_generate:
					available_directions.append(direction)

			# If direction not available, continue
			if len(available_directions) == 0:
				continue

			# Have a chance to spread, with the end trying to decrease the change the further the room
			if random.random() < 0.85 - room_depth * (1 / self.depth) * 0.5:
				# Find direction to spread
				direction = random.choice(available_directions)
				new_pos = room_pos[0] + direction[0], room_pos[1] + direction[1]

				self.rooms_to_generate.add(new_pos)
				self._add_connection(room_pos, new_pos)
				self.room_queue.append((new_pos, room_depth + 1))

				self.room_queue.append(room_info)  # Current room still active, move to end of queue
			else:
				# This room is the final room in its branch
				self.end_rooms.append(room_pos)

	def _generate_rooms_from_graph(self):
		rooms_added = set()
		for room_pos in self.rooms_to_generate:
			room_name = random.choice(self.room_names) if room_pos != (0, 0) else "start2"

			room_connections = self._get_connections(room_pos)

			if room_name != "start2":
				if room_pos not in rooms_added:
					rooms_added.add(room_pos)
				else:
					logging.warning("Duplicate")

				self.level.add_room_ex(
					room_pos, room_name,
					room_connections,
					random.choice(self.battle_names),
					self.rooms[room_name]
				)
			else:
				if room_pos not in rooms_added:
					rooms_added.add(room_pos)
				else:
					logging.warning("Duplicate")

				self.level.add_room_ex(room_pos, room_name, room_connections, "", self.rooms[room_name])

			self.generated_rooms[room_pos] = room_name

	def _generate_hallway_graph(self):
		"""
		Processes the connection_data graph to be one dimensional
		"""

		connection_graph_start = (0, 0)

		connection_graph_queue = deque()
		connection_graph_queue.append(connection_graph_start)
		self.visited_connections.add(connection_graph_start)

		while len(connection_graph_queue) > 0:
			current = connection_graph_queue.popleft()

			for connection in self.connection_data[current]:
				if connection not in self.visited_connections:
					self.hallway_connections.setdefault(current, []).append(connection)
					self.visited_connections.add(connection)

					connection_graph_queue.append(connection)

	def _generate_hallways_from_graph(self):
		for room_pos, connections in self.hallway_connections.items():
			for connection in connections:
				self.level.add_hallway(
					room_pos,
					connection,
					self.level.get_room_from_room_pos(room_pos),
					self.level.get_room_from_room_pos(connection)
				)

	# TODO: Redo generation to be over multiple frames
	def generate_level(self) -> Level:
		self._generate_room_graph()
		self._generate_rooms_from_graph()

		self._generate_hallway_graph()
		self._generate_hallways_from_graph()

		gc.collect()

		return self.level
