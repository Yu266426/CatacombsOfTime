class Health:
	__slots__ = ["_alive", "amount"]

	def __init__(self, amount: int):
		self._alive = True

		self.amount: int = amount

	def damage(self, amount: int):
		self.amount -= amount

		if self.amount <= 0:
			self.amount = 0
			self._alive = False

	def is_alive(self):
		return self._alive
