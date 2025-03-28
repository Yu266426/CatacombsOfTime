from .runic_pattern import RunicPattern, FireballPattern
from .rune import Rune


def load():
	Rune.load()
	RunicPattern.load()


def test():
	load()

	assert FireballPattern.search(["water"], 0) is None
	assert FireballPattern.search(["fire"], 0) is None
	assert FireballPattern.search(["fire", "air", "fire", "air"], 0) == 0
	assert FireballPattern.search(["fire", "air", "fire", "air"], 1) is None
	assert FireballPattern.search(["water", "fire", "air", "earth", "air", "fire", "air"], 0) is None
	assert FireballPattern.search(["water", "fire", "air", "earth", "air", "fire", "air", "fire", "air", "water"], 0) == 5
	assert FireballPattern.search(["water", "fire", "air", "earth", "air", "fire", "air", "fire", "air", "water"], 3) == 5
