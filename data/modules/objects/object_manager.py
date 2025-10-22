from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from data.modules.objects.base.game_object import GameObject


# TODO: Finish
class ObjectManager:
	def __init__(self):
		self.objects: list[GameObject] = []

	def add_object(self):
		pass

	def remove_object(self):
		pass

	def update(self):
		pass

	def draw(self):
		pass
