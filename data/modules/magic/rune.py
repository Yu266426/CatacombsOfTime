from typing import Self


class Rune:
	runes: dict[str, Self] = {}

	def __init__(self, name: str):
		self.name = name

	@classmethod
	def load(cls):
		cls.runes["fire"] = Rune("fire")
		cls.runes["air"] = Rune("air")
		cls.runes["earth"] = Rune("earth")
		cls.runes["water"] = Rune("water")
