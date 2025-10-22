from collections import OrderedDict
from typing import ClassVar


class RunicPattern:
	_runic_patterns: ClassVar[list[type[RunicPattern]]] = []

	def __init__(self, name: str, pattern: list[str]):
		self._name = name
		self._pattern = pattern

	def __eq__(self, other) -> bool:
		if isinstance(other, RunicPattern):
			return self._name == other.name and self._pattern == other._pattern
		if isinstance(other, str):
			return self._name == other

		raise TypeError(f"Cannot compare RunicPattern with {type(other)}")

	def __repr__(self) -> str:
		return f"{self.name}"

	@property
	def name(self) -> str:
		return self._name

	def length(self) -> int:
		return len(self._pattern)

	def search(self, sequence: list[str], start_index: int) -> int | None:
		"""
		Returns first instance of pattern
		:param sequence: List of magic
		:param start_index: Starting index
		:return: Index of pattern or `None` if not found
		"""

		sequence = sequence[start_index:]

		length = self.length()

		if len(sequence) < length:
			return None

		pattern = self._pattern

		for index, rune in enumerate(sequence[:-length + 1]):
			# If first rune of pattern found
			if rune == pattern[0]:
				found = True
				for i in range(1, length):
					if sequence[index + i] != pattern[i]:
						found = False

				if found:
					return index + start_index

		return None


class RunicPatterns:
	_patterns: ClassVar[dict[str, RunicPattern]] = OrderedDict()

	@classmethod
	def add_pattern(cls, pattern: RunicPattern):
		cls._patterns[pattern.name] = pattern

	@classmethod
	def load(cls):
		# TODO: Sort in some way?
		cls.add_pattern(RunicPattern("fireball", ["fire", "air", "fire", "air"]))
		cls.add_pattern(RunicPattern("test", ["fire", "water", "water", "air", "fire"]))

	@classmethod
	def search(cls, sequence: list[str], start_index: int) -> tuple[RunicPattern, int] | None:
		for _, pattern in cls._patterns.items():
			result = pattern.search(sequence, start_index)

			if result is not None:
				return pattern, result

		return None
