from data.modules.level.room import EditorRoom
from data.modules.editor.actions.editor_actions import EditorAction
from data.modules.objects.base.game_object import GameObject


class PlaceObjectAction(EditorAction):
	def __init__(self, room: EditorRoom, game_object: GameObject):
		self._room = room

		self.game_object = game_object

	def execute(self):
		self._room.add_object(self.game_object, ())

	def undo(self):
		self._room.remove_object(self.game_object)


class RemoveObjectAction(EditorAction):
	def __init__(self, room: EditorRoom, game_object: GameObject):
		self._room = room

		self.game_object = game_object

	def execute(self):
		self._room.remove_object(self.game_object)

	def undo(self):
		self._room.add_object(self.game_object, ())
