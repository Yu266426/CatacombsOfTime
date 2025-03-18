import pygame
import pygbase
from pygbase.ui import *

from data.modules.base.constants import FRAME_BACKGROUND_COLOR
from data.modules.editor.actions.editor_actions import EditorActionQueue
from data.modules.editor.editor_selection_info import TileSelectionInfo, ObjectSelectionInfo
from data.modules.editor.editor_states.editor_state import EditorState, EditorStates
from data.modules.editor.editor_states.object_draw_state import ObjectDrawState
from data.modules.editor.editor_states.object_selection_state import ObjectSelectionState
from data.modules.editor.editor_states.tile_draw_state import TileDrawState
from data.modules.editor.editor_states.tile_selection_state import TileSelectionState
from data.modules.editor.shared_editor_state import SharedEditorState
from data.modules.entities.entity_manager import EntityManager
from data.modules.level.room import EditorRoom


class Editor(pygbase.GameState, name="editor"):
	def __init__(self, room: EditorRoom, entity_manager: EntityManager):
		super().__init__()

		self.room = room
		self.entity_manager = entity_manager
		self.particle_manager: pygbase.ParticleManager = pygbase.Common.get("particle_manager")

		self.shared_state = SharedEditorState(self.room)
		self.action_queue = EditorActionQueue()

		self.tile_selection_info = TileSelectionInfo("tiles")
		self.object_selection_info = ObjectSelectionInfo("small_cube")

		self.current_state: EditorStates = EditorStates.TILE_DRAW_STATE
		self.states: dict[EditorStates, EditorState] = {
			EditorStates.TILE_DRAW_STATE: TileDrawState(self.room, self.shared_state, self.action_queue, self.tile_selection_info),
			EditorStates.TILE_SELECTION_STATE: TileSelectionState(self.room, self.shared_state, self.action_queue, self.tile_selection_info),
			EditorStates.OBJECT_DRAW_STATE: ObjectDrawState(self.room, self.shared_state, self.action_queue, self.object_selection_info),
			EditorStates.OBJECT_SELECTION_STATE: ObjectSelectionState(self.room, self.shared_state, self.action_queue, self.object_selection_info)
		}

		with Frame(size=(Grow(), Grow())) as self.ui:
			self.mode_selector = TextSelector(
				["Tile", "Object"],
				"images/left",
				"images/right",
				pos=(10, 10),
				size=(400, Fit()),
				bg_color=FRAME_BACKGROUND_COLOR,
				can_interact=True,
				blocks_mouse=True
			)

		self.show_overlay = False

	#
	# self.overlay_ui = pygbase.UIManager()
	# self.overlay_darken = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.SRCALPHA)
	# self.overlay_darken.fill((0, 0, 0, 50))
	# self.overlay_frame = self.overlay_ui.add_frame(pygbase.Frame(
	# 	(pygbase.UIValue(0.25, False), pygbase.UIValue(0.24, False)),
	# 	(pygbase.UIValue(0.5, False), pygbase.UIValue(0.52, False)),
	# 	bg_colour=(10, 10, 10, 200)
	# ))
	#
	# self.overlay_frame.add_element(pygbase.Button(
	# 	(pygbase.UIValue(0.5, False), pygbase.UIValue(0.02, False)),
	# 	(pygbase.UIValue(0, False), pygbase.UIValue(0, False)),
	# 	"images", "button",
	# 	self.overlay_frame,
	# 	self.back_to_main_menu,
	# 	text="Menu", alignment="c"
	# ))
	# self.overlay_frame.add_element(pygbase.Button(
	# 	(pygbase.UIValue(0.5, False), pygbase.UIValue(0.02, False)),
	# 	(pygbase.UIValue(0, False), pygbase.UIValue(0, False)),
	# 	"images", "button",
	# 	self.overlay_frame,
	# 	self.room.save,
	# 	text="Save", alignment="c"
	# ), align_with_previous=(True, False), add_on_to_previous=(False, True))
	# self.overlay_frame.add_element(pygbase.Button(
	# 	(pygbase.UIValue(0.5, False), pygbase.UIValue(0.02, False)),
	# 	(pygbase.UIValue(0, False), pygbase.UIValue(0, False)),
	# 	"images", "button",
	# 	self.overlay_frame,
	# 	pygbase.Events.post_event, callback_args=(pygame.QUIT,),
	# 	text="Quit", alignment="c"
	# ), align_with_previous=(True, False), add_on_to_previous=(False, True))

	def enter(self):
		self.particle_manager.clear()

	def back_to_main_menu(self):
		from data.modules.game_states.main_menu import MainMenu
		self.set_next_state_type(MainMenu, ())

		self.room.remove_objects()
		self.entity_manager.clear_entities()

	def update(self, delta: float):
		if pygbase.Input.key_just_pressed(pygame.K_ESCAPE):
			self.show_overlay = not self.show_overlay
			self.shared_state.should_draw_tool = not self.shared_state.should_draw_tool

		if not self.show_overlay:
			if self.shared_state.show_global_ui:
				self.ui.update(delta)

			self.current_state = self.states[self.current_state].next_state(self.mode_selector.index)

			self.states[self.current_state].update(delta)

			# Undo / Redo
			if pygbase.Input.key_just_pressed(pygame.K_z):
				if pygbase.Input.check_modifiers(pygame.KMOD_CTRL) and not pygbase.Input.check_modifiers(pygame.KMOD_SHIFT):
					self.action_queue.undo_action()
				if pygbase.Input.check_modifiers(pygame.KMOD_CTRL, pygame.KMOD_SHIFT, use_and=True):
					self.action_queue.redo_action()

			# Animate objects
			for game_object in self.room.objects:
				game_object.animate(delta * 2)

			self.particle_manager.update(delta)

			# Save
			if pygbase.Input.check_modifiers(pygame.KMOD_LCTRL):
				if pygbase.Input.key_just_pressed(pygame.K_s):
					self.room.save()
		else:
			self.overlay_ui.update(delta)

	def draw(self, surface: pygame.Surface):
		surface.fill((30, 30, 30))

		self.states[self.current_state].draw(surface)

		if self.shared_state.show_global_ui and not self.show_overlay:
			self.ui.draw(surface)

		if self.show_overlay:
			surface.blit(self.overlay_darken, (0, 0))
			self.overlay_ui.draw(surface)
