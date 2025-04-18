from data.modules.objects.base.game_object import GameObject
from data.modules.objects.object_loader import ObjectLoader


class TileSelectionInfo:
	def __init__(self, sprite_sheet_name: str):
		# Draw Layer
		self.layer = 0

		# Selection Info
		self.sprite_sheet_name = sprite_sheet_name
		self.ids: dict[int, dict[int, int]] = {0: {0: 0}}

		self.selected_topleft = (0, 0)
		self.selected_bottomright = (0, 0)


class ObjectSelectionInfo:
	def __init__(self, starting_object: str):
		self.current_object_name: str = starting_object

	def has_object(self):
		return self.current_object_name is not None

	def set_object(self, game_object: GameObject):
		self.current_object_name = game_object.name

	def get_object_name(self) -> str:
		return self.current_object_name

	def get_object(self, pos: tuple) -> GameObject:
		return ObjectLoader.create_object(self.current_object_name, pos)[0]
