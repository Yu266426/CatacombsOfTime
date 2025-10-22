import json
from typing import TYPE_CHECKING

from data.modules.base.paths import BATTLE_DIR
from data.modules.level.enemy_wave import EnemyWave

if TYPE_CHECKING:
	from data.modules.entities.entity_manager import EntityManager
	from data.modules.level.level import Level
	from data.modules.level.room import Room


class Battle:
	def __init__(self, battle_name: str, level: Level, room: Room, entity_manager: EntityManager):
		self.level = level
		self.entity_manager = entity_manager
		self.room = room

		self.completed = False
		self.current_wave = 0

		self.num_waves: int | None = None
		self.waves: list[EnemyWave] = []

		self.load(battle_name)

	def load(self, battle_name: str):
		with open(BATTLE_DIR / f"{battle_name}.json") as battle_file:
			battle_data = json.load(battle_file)

		self.num_waves = len(battle_data["waves"])

		for wave_data in battle_data["waves"]:
			self.waves.append(EnemyWave(wave_data, self.entity_manager))

	def update(self):
		"""

		:return: True if battle done else False
		"""
		if self.completed:
			return True

		current_wave = self.waves[self.current_wave]

		if not current_wave.wave_in_progress:
			current_wave.spawn_wave(self.level, self.room)

		current_wave_done = current_wave.check_done()
		if current_wave_done:
			self.current_wave += 1

			if self.current_wave == self.num_waves:
				self.completed = True
				return True

		return False
