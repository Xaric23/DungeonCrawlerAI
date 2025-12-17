"""Difficulty system for DungeonCrawlerAI."""

from dataclasses import dataclass
from enum import Enum, auto


class Difficulty(Enum):
    """Enum representing game difficulty levels."""
    EASY = auto()
    NORMAL = auto()
    HARD = auto()
    NIGHTMARE = auto()


@dataclass(frozen=True)
class DifficultySettings:
    """Settings that vary based on difficulty level.
    
    Attributes:
        hero_hp_multiplier: Multiplier applied to hero health points.
        hero_attack_multiplier: Multiplier applied to hero attack damage.
        curse_energy_regen: Amount of curse energy regenerated per turn.
        suspicion_decay_rate: Rate at which suspicion decreases per turn.
        enemy_damage_multiplier: Multiplier applied to enemy damage.
        trap_damage_multiplier: Multiplier applied to trap damage.
        starting_curse_energy: Initial curse energy at game start.
    """
    hero_hp_multiplier: float
    hero_attack_multiplier: float
    curse_energy_regen: int
    suspicion_decay_rate: int
    enemy_damage_multiplier: float
    trap_damage_multiplier: float
    starting_curse_energy: int


DIFFICULTY_PRESETS: dict[Difficulty, DifficultySettings] = {
    Difficulty.EASY: DifficultySettings(
        hero_hp_multiplier=1.5,
        hero_attack_multiplier=1.2,
        curse_energy_regen=8,
        suspicion_decay_rate=5,
        enemy_damage_multiplier=0.8,
        trap_damage_multiplier=0.8,
        starting_curse_energy=150,
    ),
    Difficulty.NORMAL: DifficultySettings(
        hero_hp_multiplier=1.0,
        hero_attack_multiplier=1.0,
        curse_energy_regen=5,
        suspicion_decay_rate=2,
        enemy_damage_multiplier=1.0,
        trap_damage_multiplier=1.0,
        starting_curse_energy=100,
    ),
    Difficulty.HARD: DifficultySettings(
        hero_hp_multiplier=0.8,
        hero_attack_multiplier=0.9,
        curse_energy_regen=3,
        suspicion_decay_rate=0,
        enemy_damage_multiplier=1.3,
        trap_damage_multiplier=1.2,
        starting_curse_energy=80,
    ),
    Difficulty.NIGHTMARE: DifficultySettings(
        hero_hp_multiplier=0.6,
        hero_attack_multiplier=0.8,
        curse_energy_regen=2,
        suspicion_decay_rate=0,
        enemy_damage_multiplier=1.5,
        trap_damage_multiplier=1.5,
        starting_curse_energy=50,
    ),
}


def get_difficulty_settings(difficulty: Difficulty) -> DifficultySettings:
    """Get the settings for a specific difficulty level.
    
    Args:
        difficulty: The difficulty level to get settings for.
        
    Returns:
        DifficultySettings configured for the specified difficulty.
    """
    return DIFFICULTY_PRESETS[difficulty]
