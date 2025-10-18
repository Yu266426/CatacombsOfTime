from .runic_pattern import RunicPatterns
from .spell.spell import Spell


class RunicSequence:
	"""
	Sequence that users will manipulate
	"""

	def __init__(self, length: int):
		self.length = length
		self._sequence: list[str | None] = [None for _ in range(length)]

	def insert_rune(self, index: int, rune: str) -> str | None:
		assert 0 <= index < self.length

		# TODO: Should it stop if the spot is occupied?
		prev_rune = self._sequence[index]
		self._sequence[index] = rune

		return prev_rune

	def remove_rune(self, index: int) -> str:
		assert 0 <= index < self.length

		rune = self._sequence[index]
		self._sequence[index] = None

		return rune

	def process(self) -> Spell:
		patterns = []

		index = 0
		result = RunicPatterns.search(self._sequence, index)

		while result is not None:
			patterns.append(result[0])
			index = result[1] + result[0].length()

			result = RunicPatterns.search(self._sequence, index)

		print(patterns)

		return Spell()
