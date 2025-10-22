import pygame


class CircleCollider:
	def __init__(self, pos, radius: float):
		self.pos = pygame.Vector2(pos)

		self.radius = radius

	def link_pos(self, pos: pygame.Vector2) -> CircleCollider:
		self.pos = pos
		return self

	def collides_with(self, collider) -> bool:
		from data.modules.entities.components.box_collider import BoxCollider
		from data.modules.entities.components.line_collider import LineCollider

		if isinstance(collider, BoxCollider):
			closest_point = pygame.Vector2(
				max(collider.rect.left, min(self.pos.x, collider.rect.right)),
				max(collider.rect.top, min(self.pos.y, collider.rect.bottom)),
			)

			return closest_point.distance_to(self.pos) < self.radius

		if isinstance(collider, LineCollider):
			if collider.start_pos.distance_to(self.pos) < self.radius:
				return True
			if collider.end_pos.distance_to(self.pos) < self.radius:
				return True

			dot = (
					(self.pos.x - collider.start_pos.x) * (collider.end_pos.x - collider.start_pos.x)
					+ (self.pos.y - collider.start_pos.y) * (collider.end_pos.y - collider.start_pos.y)
				) / collider.length ** 2

			closest_point = pygame.Vector2(
				collider.start_pos.x + dot * (collider.end_pos.x - collider.start_pos.x),
				collider.start_pos.y + dot * (collider.end_pos.y - collider.start_pos.y),
			)

			if not collider.point_within_line_segment(closest_point):
				return False

			return closest_point.distance_to(self.pos) < self.radius

		if isinstance(collider, CircleCollider):
			return collider.pos.distance_to(self.pos) < collider.radius + self.radius

		return False
