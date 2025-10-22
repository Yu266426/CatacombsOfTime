from typing import TYPE_CHECKING

from data.modules.entities.entity_spawn import EntitySpawn

if TYPE_CHECKING:
	from data.modules.entities.entity_manager import EntityManager
	from data.modules.level.level import Level
	from data.modules.level.room import Room


class EnemyWave:
	def __init__(self, wave_data: dict, entity_manager: EntityManager):
		self.entity_manager = entity_manager

		self.wave_data: dict = wave_data
		self.enemies = []

		self.wave_in_progress = False

	def spawn_wave(self, level: Level, room: Room):
		from data.modules.entities.enemies.enemy_loader import EnemyLoader

		for enemy_type, num_enemies in self.wave_data.items():
			for _ in range(num_enemies):
				spawn_pos = room.generate_spawn_pos()
				enemy = EnemyLoader.create_enemy(enemy_type, spawn_pos, level, self.entity_manager)
				spawn = EntitySpawn(spawn_pos, self.entity_manager, 0.7, enemy)

				self.enemies.append(enemy)
				self.entity_manager.add_entity(spawn)

		self.wave_in_progress = True

	def check_done(self):
		return all(not enemy.is_alive() for enemy in self.enemies)
