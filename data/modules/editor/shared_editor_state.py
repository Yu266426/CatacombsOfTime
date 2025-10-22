from typing import TYPE_CHECKING

import pygbase

from data.modules.base.constants import TILE_SIZE

if TYPE_CHECKING:
	from data.modules.level.room import EditorRoom


class SharedEditorState:
	def __init__(self, room: EditorRoom):
		# UI
		self.show_global_ui = True

		self.should_draw_tool = True

		# Room Screen
		self.camera_controller = pygbase.CameraController(keep_in=(0, 0, room.n_cols * TILE_SIZE, room.n_rows * TILE_SIZE))
