from abc import ABC, abstractmethod


class EditorAction(ABC):
	@abstractmethod
	def execute(self):
		pass

	@abstractmethod
	def undo(self):
		pass


class EditorActionBatch:
	def __init__(self):
		self.actions: list[EditorAction] = []

	def add_action(self, action: EditorAction):
		self.actions.append(action)

	def execute(self):
		for action in self.actions:
			action.execute()

	def undo(self):
		for action in self.actions[::-1]:
			action.undo()


class EditorActionQueue:
	def __init__(self, max_actions: int = 20):
		self.action_index = -1
		self.editor_actions: list[EditorAction | EditorActionBatch] = []
		self.max_action_length = max_actions

	def add_action(self, action: EditorAction | EditorActionBatch):
		if self.action_index != len(self.editor_actions) - 1:
			for _ in range(len(self.editor_actions) - self.action_index - 1):
				self.editor_actions.pop()

		self.editor_actions.append(action)
		self.action_index += 1

		if self.max_action_length < len(self.editor_actions):
			self.editor_actions.pop(0)
			self.action_index -= 1

	def undo_action(self):
		if self.action_index >= 0:
			self.editor_actions[self.action_index].undo()
			self.action_index -= 1

	def redo_action(self):
		if self.action_index < len(self.editor_actions) - 1:
			self.action_index += 1
			self.editor_actions[self.action_index].execute()
