from typing import TYPE_CHECKING

import pygame
import pygbase

from data.modules.base.constants import TILE_SIZE
from data.modules.base.utils import draw_rect_outline
from data.modules.editor.actions.editor_actions import EditorActionBatch
from data.modules.editor.actions.object_actions import PlaceObjectAction, RemoveObjectAction
from data.modules.editor.tools.editor_tool import EditorTool
from data.modules.objects.object_loader import ObjectLoader

if TYPE_CHECKING:
	from data.modules.editor.actions.editor_actions import EditorActionQueue
	from data.modules.editor.editor_selection_info import ObjectSelectionInfo
	from data.modules.editor.shared_editor_state import SharedEditorState
	from data.modules.level.room import EditorRoom


class ObjectDrawTool(EditorTool):
	def __init__(self, room: EditorRoom, shared_state: SharedEditorState, action_queue: EditorActionQueue):
		super().__init__(room, shared_state, action_queue)

		self.current_mouse_pos: tuple | None = None

		self.current_batch: EditorActionBatch | None = None

	def update(self, mouse_tile_pos: tuple[int, int], selection_info: ObjectSelectionInfo):
		if pygbase.Input.mouse_pressed(0):
			self._shared_state.show_global_ui = False

			x_pos = (mouse_tile_pos[0] + 0.5) * TILE_SIZE
			y_pos = (mouse_tile_pos[1] + 1) * TILE_SIZE

			if selection_info.has_object() and self._room.get_object((x_pos, y_pos - 1), with_hitbox=True) is None:
				action = PlaceObjectAction(self._room, selection_info.get_object(mouse_tile_pos))
				action.execute()

				if self.current_batch is None:
					self.current_batch = EditorActionBatch()

				self.current_batch.add_action(action)

		if pygbase.Input.mouse_pressed(2):
			self._shared_state.show_global_ui = False

			x_pos = (mouse_tile_pos[0] + 0.5) * TILE_SIZE
			y_pos = (mouse_tile_pos[1]) * TILE_SIZE

			if self._room.get_object((x_pos, y_pos)) is not None:
				action = RemoveObjectAction(self._room, self._room.get_object((x_pos, y_pos)))
				action.execute()

				if self.current_batch is None:
					self.current_batch = EditorActionBatch()

				self.current_batch.add_action(action)

		if pygbase.Input.mouse_just_released(0) or pygbase.Input.mouse_just_released(2):
			self._shared_state.show_global_ui = True

			if self.current_batch is not None:
				self._action_queue.add_action(self.current_batch)
				self.current_batch = None

	def draw(self, surface: pygame.Surface, camera: pygbase.Camera, mouse_tile_pos: tuple, selection_info: ObjectSelectionInfo):
		draw_rect_outline(
			surface, (255, 255, 255),
			camera.world_to_screen((mouse_tile_pos[0] * TILE_SIZE, mouse_tile_pos[1] * TILE_SIZE)),
			(TILE_SIZE, TILE_SIZE),
			2,
		)

		# Draw selected object if not deleting
		if not pygbase.Input.mouse_pressed(2):
			if selection_info.has_object():
				temp_object = ObjectLoader.create_object(selection_info.get_object_name(), mouse_tile_pos)[0]
				temp_object.removed()
				temp_object.draw(surface, camera, flags=pygame.BLEND_ADD)
