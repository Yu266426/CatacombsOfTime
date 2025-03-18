import pygame
import pygbase

from data.modules.entities.components.box_collider import BoxCollider
from data.modules.entities.components.circle_collider import CircleCollider
from data.modules.entities.components.line_collider import LineCollider


class TestState(pygbase.GameState, name="testing"):
	def __init__(self):
		super().__init__()

		self.mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

		self.box = BoxCollider((200, 200), (200, 300))
		self.box_lines = self.box.get_edge_lines()

		self.line = LineCollider((100, 30), 180, 500)

		self.circle = CircleCollider(self.mouse_pos, 30).link_pos(self.mouse_pos)

	def update(self, delta: float):
		self.mouse_pos.update(pygame.mouse.get_pos())

		if pygbase.Input.key_pressed(pygame.K_a):
			self.line.set_angle(self.line.angle - 30 * delta)
		if pygbase.Input.key_pressed(pygame.K_d):
			self.line.set_angle(self.line.angle + 30 * delta)

		# print(self.line.collides_with(self.box_lines[0]))
		print(
			"|  line box:",
			self.box.collides_with(self.line),
			self.line.collides_with(self.box),
			" |  line circle:",
			self.circle.collides_with(self.line),
			self.line.collides_with(self.circle),
			" |  line box:",
			self.circle.collides_with(self.box),
			self.box.collides_with(self.circle)
		)

		if pygbase.Input.key_just_pressed(pygame.K_ESCAPE):
			pygbase.Events.post_event(pygame.QUIT)

	def draw(self, surface: pygame.Surface):
		surface.fill((0, 0, 0))

		pygame.draw.rect(surface, "white", self.box.rect)
		self.line.draw_debug(pygbase.Camera())

		for box_line in self.box_lines:
			pygame.draw.line(surface, "green", box_line.start_pos, box_line.end_pos, width=5)

		pygame.draw.circle(surface, "blue", self.circle.pos, self.circle.radius, width=2)
