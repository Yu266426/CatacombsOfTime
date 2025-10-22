from typing import TYPE_CHECKING

from data.modules.editor.actions.editor_actions import EditorAction

if TYPE_CHECKING:
	from data.modules.level.room import EditorRoom
	from data.modules.level.tile import Tile


class PlaceTileAction(EditorAction):
	def __init__(self, room: EditorRoom, level: int, row: int, col: int, tile: Tile):
		self._room = room

		self._level = level
		self._row = row
		self._col = col

		self._tile = tile

		self._prev_tile = None

	def execute(self):
		self._prev_tile = self._room.get_tile(self._level, (self._col, self._row))
		self._room.add_tile(self._level, (self._col, self._row), self._tile)

	def undo(self):
		self._room.remove_tile(self._level, (self._col, self._row))
		if self._prev_tile is not None:
			self._room.add_tile(self._level, (self._col, self._row), self._prev_tile)


class RemoveTileAction(EditorAction):
	def __init__(self, room: EditorRoom, level: int, row: int, col: int):
		self._room = room

		self._level = level
		self._row = row
		self._col = col

		self._prev_tile = None

	def execute(self):
		self._prev_tile = self._room.get_tile(self._level, (self._col, self._row))
		self._room.remove_tile(self._level, (self._col, self._row))

	def undo(self):
		if self._prev_tile is not None:
			self._room.add_tile(self._level, (self._col, self._row), self._prev_tile)
