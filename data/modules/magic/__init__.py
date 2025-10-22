from ..base.tests import test
from .rune import Rune
from .runic_pattern import RunicPattern, RunicPatterns
from .runic_sequence import RunicSequence

__all__ = ["Rune", "RunicPattern", "RunicPatterns", "RunicSequence"]


def load():
	Rune.load()
	RunicPatterns.load()


def run_tests():
	load()

	_test_patterns_search()
	_test_sequence_insert_remove()


@test
def _test_patterns_search():
	assert RunicPatterns.search(["water"], 0) is None
	assert RunicPatterns.search(["fire"], 0) is None
	assert RunicPatterns.search(["fire", "air", "fire", "air"], 0) == ("fireball", 0)
	assert RunicPatterns.search(["fire", "air", "fire", "air"], 1) is None
	assert RunicPatterns.search(["water", "fire", "air", "earth", "air", "fire", "air"], 0) is None
	assert RunicPatterns.search(["water", "fire", "air", "earth", "air", "fire", "air", "fire", "air", "water"], 0) == ("fireball", 5)
	assert RunicPatterns.search(["water", "fire", "air", "earth", "air", "fire", "air", "fire", "air", "water"], 3) == ("fireball", 5)


@test
def _test_sequence_insert_remove():
	sequence = RunicSequence(5)

	sequence.insert_rune(1, "fire")
	sequence.insert_rune(2, "water")
	sequence.insert_rune(3, "fire")
	sequence.insert_rune(4, "air")
	sequence.insert_rune(0, "earth")

	assert sequence.insert_rune(2, "air") == "water"
	assert sequence.remove_rune(0) == "earth"

	print("Sequence:", sequence._sequence)

	sequence.process()
