
import pygame

from data.modules.base.constants import PIXEL_SCALE


def to_scaled[T: float | pygame.Vector2](value: T) -> T:
	return value * PIXEL_SCALE


def to_scaled_sequence[T: tuple | list](value: T) -> T:
	scaled = (e * PIXEL_SCALE for e in value)
	return type(value)(scaled)


def get_tile_pos(pos: tuple | pygame.Vector2, tile_size: tuple[int | float, int | float]):
	return int(pos[0] // tile_size[0]), int(pos[1] // tile_size[1])


def get_1d_tile_pos(pos: int | float, tile_size: int | float):
	return int(pos // tile_size)


def get_pixel_pos(tile_pos: tuple[int, int], tile_size: tuple[int | float, int | float]):
	return tile_pos[0] * tile_size[0], tile_pos[1] * tile_size[1]


def generate_3d_list(levels: int, n_rows: int, n_cols: int, fill_data=None):
	data = []

	for _ in range(levels):
		rows = []
		for __ in range(n_rows):
			col = []
			for ___ in range(n_cols):
				col.append(fill_data)
			rows.append(col)

		data.append(rows)

	return data


def generate_2d_list(n_rows: int, n_cols: int, fill: bool = False):
	data = []
	for _ in range(n_rows):
		col = []
		if fill:
			for __ in range(n_cols):
				col.append(None)
		data.append(col)
	return data


def sort_tuple(tup1: tuple[int, int], tup2: tuple[int, int]):
	new_tup1 = min(tup1[0], tup2[0]), min(tup1[1], tup2[1])
	new_tup2 = max(tup1[0], tup2[0]), max(tup1[1], tup2[1])

	return new_tup1, new_tup2


def draw_rect_outline(
		display: pygame.Surface,
		colour: pygame.typing.ColorLike,
		pos: pygame.typing.Point,
		size: tuple[int | float, int | float] | pygame.Vector2,
		width: int,
):
	pygame.draw.rect(
		display, colour,
		(pos, size),
		width=width,
	)


def one_if_even(*nums: int) -> int:
	for num in nums:
		if num % 2 != 0:
			return 0
	return 1


def one_if_odd(*nums: int) -> int:
	for num in nums:
		if num % 2 == 0:
			return 0
	return 1


def even_flipper(num: int):
	"""
	:return: 1 if even else -1
	"""
	return 1 if num % 2 == 0 else -1
