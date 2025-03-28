from typing import Type


class RunicPattern:
	_runic_patterns: list[Type["RunicPattern"]] = []

	_pattern: list[str]

	@classmethod
	def load(cls):
		cls._runic_patterns.append(FireballPattern)
		cls._runic_patterns.append(TestPattern)

		cls._runic_patterns.sort(key=lambda e: e.length())  # Sort from shortest to longest

	@classmethod
	def length(cls) -> int:
		return len(cls._pattern)

	@classmethod
	def search(cls, sequence: list[str], start_index: int) -> int | None:
		"""
		Returns first instance of pattern
		:param sequence: List of magic
		:param start_index: Starting index
		:return: Index of pattern or `None` if not found
		"""

		sequence = sequence[start_index:]

		if len(sequence) < cls.length():
			return None

		pattern = cls._pattern

		for index, rune in enumerate(sequence[:-cls.length() + 1]):
			# If first rune of pattern found
			if rune == pattern[0]:
				found = True
				for i in range(1, cls.length()):
					if sequence[index + i] != pattern[i]:
						found = False

				if found:
					return index + start_index

		return None


class FireballPattern(RunicPattern):
	_pattern = ["fire", "air", "fire", "air"]


class TestPattern(RunicPattern):
	_pattern = ["fire", "water", "water", "air", "fire"]
