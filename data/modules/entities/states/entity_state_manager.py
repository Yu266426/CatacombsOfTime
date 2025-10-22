from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from data.modules.entities.states.entity_state import EntityState


class EntityStateManager:
	def __init__(self, states: dict[str, EntityState], current_state: str):
		self.current_state = current_state
		self.states = states

	def change_state(self, next_state: str):
		if next_state != self.current_state:
			self.current_state = next_state
			self.states[self.current_state].on_enter()

	def update(self, delta: float):
		self.states[self.current_state].update(delta)

		next_state = self.states[self.current_state].next_state()
		if next_state != "":
			self.current_state = next_state
			self.states[self.current_state].on_enter()
