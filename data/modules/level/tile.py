from typing import TYPE_CHECKING

from pygbase import Resources

if TYPE_CHECKING:
	import pygame
	from pygbase import Camera
	from pygbase.graphics.image import Image


class Tile:
	__slots__ = ["image", "image_index", "rect", "sprite_sheet_name"]

	def __init__(self, sprite_sheet_name: str, image_index: int, pos: tuple | pygame.Vector2):
		self.sprite_sheet_name = sprite_sheet_name
		self.image_index = image_index

		self.image: Image = Resources.get_resource("sprite_sheets", sprite_sheet_name).get_image(image_index)
		self.rect: pygame.Rect = self.image.get_image().get_rect(bottomleft=pos)

	def draw(self, surface: pygame.Surface, camera: Camera, flag: int = 0):
		self.image.draw(surface, camera.world_to_screen(self.rect.topleft), flags=flag)
