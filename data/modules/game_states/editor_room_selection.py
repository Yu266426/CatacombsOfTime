import os
from typing import Optional

import pygame
import pygbase
from pygbase.ui import *

from data.modules.base.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_BACKGROUND_COLOR
from data.modules.base.paths import ROOM_DIR
from data.modules.entities.entity_manager import EntityManager
from data.modules.game_states.editor import Editor
from data.modules.game_states.main_menu import MainMenu
from data.modules.level.room import EditorRoom


class EditorRoomSelection(pygbase.GameState, name="editor_room_select"):
	def __init__(self):
		super().__init__()

		self.rooms = sorted(os.listdir(ROOM_DIR))
		self.selected_room: Optional[EditorRoom] = None

		self._make_ui()

		self.entity_manager = EntityManager()

	def _make_ui(self):
		with (Frame(size=(Grow(), Grow()), padding=Padding.all(10), gap=10) as self.ui):
			with Frame(size=(Grow(3), Grow()), layout=Layout.TOP_TO_BOTTOM, gap=10):
				with Frame(
						size=(Grow(), Grow()),
						layout=Layout.TOP_TO_BOTTOM,
						padding=Padding.all(5),
						gap=5,
						bg_color=FRAME_BACKGROUND_COLOR
				):  # Room Selection
					for index, room in enumerate(self.rooms):
						room_name = room[:-5]
						with Button(self.select_room, (index, room_name), size=(Grow(), Fit())):
							with Image("images/button", size=(Grow(), Fit()), x_align=XAlign.CENTER, y_align=YAlign.CENTER):
								Text(room_name, 40, "white")

				with Frame(size=(Grow(), 100), padding=Padding.all(5), gap=10, bg_color=FRAME_BACKGROUND_COLOR):  # Button Panel
					with Button(self.set_next_state_type, (MainMenu, ()), size=(Fit(), Grow())):
						Image("images/home_button", size=(Fit(), Grow()))

					with Button(self.edit_button_callback, size=(Fit(), Grow())):
						Image("images/draw_tool_button", size=(Fit(), Grow()))

					with Button(self.add_room_button_callback, size=(Fit(), Grow())):
						Image("images/plus_button", size=(Fit(), Grow()))

			with Frame(size=(Grow(2), Grow()), layout=Layout.TOP_TO_BOTTOM, gap=10):  # Room info
				with Frame(size=(Grow(), Fit())):
					selected_room_image = pygame.Surface((SCREEN_WIDTH * 0.3, SCREEN_HEIGHT * 0.3), flags=pygame.SRCALPHA)

					if self.selected_room is None:
						selected_room_image.fill((20, 20, 20))
					else:
						self.selected_room.draw_room_to_surface(selected_room_image)

					self.selected_room_image = Image(selected_room_image, size=(Grow(), Fit()))

				with Frame(size=(Grow(), Grow()), layout=Layout.TOP_TO_BOTTOM, padding=Padding.all(10), gap=10, bg_color=FRAME_BACKGROUND_COLOR):
					room = self.selected_room

					Text(f"Name: {"N/A" if room is None else room.name}", 35, "white")
					Text(f"Size: {"N/A" if room is None else (room.n_cols, room.n_rows)}", 35, "white")

	def exit(self):
		if self.selected_room is not None:
			self.selected_room.remove_objects()
		self.entity_manager.clear_entities()

	def select_room(self, _index, room_name):
		if self.selected_room is not None:
			self.selected_room.remove_objects()

		self.selected_room = EditorRoom(room_name, self.entity_manager)

		self._make_ui()

	def edit_button_callback(self):

		if self.selected_room is not None:
			self.selected_room.remove_objects()

			self.set_next_state(Editor(EditorRoom(self.selected_room.name, self.entity_manager), self.entity_manager))

	def add_room_button_callback(self):
		from data.modules.game_states.editor import Editor

		if self.selected_room is not None:
			self.selected_room.remove_objects()

		# TODO: Allow users to specify room
		self.set_next_state(Editor(EditorRoom("start2", self.entity_manager, n_rows=9, n_cols=9), self.entity_manager))

	def update(self, delta: float):

		self.ui.update(delta)
		self.entity_manager.update(delta)

		if pygbase.Input.key_just_pressed(pygame.K_ESCAPE):
			self.set_next_state_type(MainMenu, ())

	def draw(self, surface: pygame.Surface):
		surface.fill((30, 30, 30))
		self.ui.draw(surface)
