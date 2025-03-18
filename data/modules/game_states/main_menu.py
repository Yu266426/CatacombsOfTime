import pygame

import pygbase
from pygbase.ui import *

from data.modules.base.constants import FRAME_BACKGROUND_COLOR


class MainMenu(pygbase.GameState, name="main_menu"):
	def __init__(self):
		super().__init__()

		from data.modules.game_states.lobby import Lobby
		from data.modules.game_states.editor_room_selection import EditorRoomSelection
		with Frame(size=(Grow(), Grow()), layout=Layout.TOP_TO_BOTTOM, padding=Padding.all(40)) as self.ui:
			with Frame(size=(Grow(), Grow(2)), x_align=XAlign.CENTER, y_align=YAlign.CENTER):
				Image("images/main_title", size=(650, Fit()))

			with Frame(size=(Grow(), Grow(3))):
				Frame(size=(Grow(), Grow()))

				with Frame(size=(Grow(), Grow(2)), layout=Layout.TOP_TO_BOTTOM, padding=Padding.all(10), gap=20, bg_color=FRAME_BACKGROUND_COLOR):
					with Button(self.set_next_state_type, (Lobby, ()), size=(Grow(), Fit())):
						with Image("images/button", size=(Grow(), Fit()), x_align=XAlign.CENTER, y_align=YAlign.CENTER):
							Text("Start", 50, "white")

					with Button(self.set_next_state_type, (EditorRoomSelection, ()), size=(Grow(), Fit())):
						with Image("images/button", size=(Grow(), Fit()), x_align=XAlign.CENTER, y_align=YAlign.CENTER):
							Text("Editor", 50, "white")

					with Button(pygbase.Events.post_event, (pygame.QUIT,), size=(Grow(), Fit())):
						with Image("images/button", size=(Grow(), Fit()), x_align=XAlign.CENTER, y_align=YAlign.CENTER):
							Text("Quit", 50, "white")

				Frame(size=(Grow(), Grow()))

	# self.ui = pygbase.UIManager()
	#
	# self.title_frame = self.ui.add_frame(pygbase.Frame(
	# 	(pygbase.UIValue(0.2, False), pygbase.UIValue(0.1, False)),
	# 	(pygbase.UIValue(0.6, False), pygbase.UIValue(0.3, False))
	# ))
	# self.title_frame.add_element(pygbase.ImageElement(
	# 	(pygbase.UIValue(0, False), pygbase.UIValue(0, False)),
	# 	(pygbase.UIValue(1, False), pygbase.UIValue(0, False)),
	# 	"images",
	# 	"main_title",
	# 	self.title_frame
	# ))
	#
	# self.button_frame = self.ui.add_frame(
	# 	pygbase.Frame(
	# 		(pygbase.UIValue(0.25, False), pygbase.UIValue(0.4, False)),
	# 		(pygbase.UIValue(0.5, False), pygbase.UIValue(0.6, False))
	# 	)
	# )
	#
	# from data.modules.game_states.lobby import Lobby
	# self.button_frame.add_element(pygbase.Button(
	# 	(pygbase.UIValue(0, False), pygbase.UIValue(0, False)),
	# 	(pygbase.UIValue(1, False), pygbase.UIValue(0, False)),
	# 	"images",
	# 	"button",
	# 	self.button_frame,
	# 	self.set_next_state_type,
	# 	callback_args=(Lobby, ()),
	# 	text="Start"
	# ))
	#
	# from data.modules.game_states.editor_room_selection import EditorRoomSelection
	# self.button_frame.add_element(pygbase.Button(
	# 	(pygbase.UIValue(0, False), pygbase.UIValue(0.02, False)),
	# 	(pygbase.UIValue(1, False), pygbase.UIValue(0, False)),
	# 	"images",
	# 	"button",
	# 	self.button_frame,
	# 	self.set_next_state_type,
	# 	callback_args=(EditorRoomSelection, ()),
	# 	text="Editor"
	# ), add_on_to_previous=(False, True))
	#
	# self.button_frame.add_element(pygbase.Button(
	# 	(pygbase.UIValue(0, False), pygbase.UIValue(0.02, False)),
	# 	(pygbase.UIValue(1, False), pygbase.UIValue(0, False)),
	# 	"images",
	# 	"button",
	# 	self.button_frame,
	# 	pygbase.Events.post_event,
	# 	callback_args=(pygame.QUIT,),
	# 	text="Quit"
	# ), add_on_to_previous=(False, True))

	def update(self, delta: float):
		self.ui.update(delta)

		if pygbase.Input.key_just_pressed(pygame.K_ESCAPE):
			pygbase.Events.run_handlers("all", pygame.QUIT)

	def draw(self, surface: pygame.Surface):
		surface.fill((30, 30, 30))
		self.ui.draw(surface)
