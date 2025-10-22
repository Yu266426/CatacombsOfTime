from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	import pygame
	import pygbase

	from data.modules.editor.actions.editor_actions import EditorActionQueue
	from data.modules.editor.editor_selection_info import ObjectSelectionInfo, TileSelectionInfo
	from data.modules.editor.shared_editor_state import SharedEditorState
	from data.modules.level.room import EditorRoom


class EditorTool(ABC):
	def __init__(self, room: EditorRoom, shared_state: SharedEditorState, action_queue: EditorActionQueue):
		self._room = room
		self._shared_state = shared_state
		self._action_queue = action_queue

	@abstractmethod
	def update(self, mouse_tile_pos: tuple[int, int], selection_info: TileSelectionInfo | ObjectSelectionInfo):
		pass

	@abstractmethod
	def draw(self, screen: pygame.Surface, camera: pygbase.Camera, mouse_tile_pos: tuple, selection_info: TileSelectionInfo | ObjectSelectionInfo):
		pass
