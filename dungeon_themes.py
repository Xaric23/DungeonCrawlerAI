"""
Dungeon Themes for DungeonCrawlerAI.
Defines themed dungeon configurations with unique enemies, traps, and mechanics.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict
import random

from models import Enemy, EnemyType, Trap, TrapType, Room, RoomType, Item, ItemType
from dungeon import Dungeon


class DungeonTheme(Enum):
    """Available dungeon themes."""
    CLASSIC_FANTASY = "classic_fantasy"
    UNDEAD_CRYPT = "undead_crypt"
    TECHNOLOGICAL = "technological"
    VOLCANIC = "volcanic"
    ICE_CAVERN = "ice_cavern"
    ELDRITCH_HORROR = "eldritch_horror"


class ExtendedEnemyType(Enum):
    """Extended enemy types for themed dungeons."""
    GOBLIN = "goblin"
    ORC = "orc"
    SKELETON = "skeleton"
    DRAGON = "dragon"
    WRAITH = "wraith"
    ROBOT = "robot"
    TURRET = "turret"
    FIRE_ELEMENTAL = "fire_elemental"
    LAVA_GOLEM = "lava_golem"
    FROST_WRAITH = "frost_wraith"
    ICE_GOLEM = "ice_golem"
    VOID_SPAWN = "void_spawn"
    MIND_FLAYER = "mind_flayer"


class ExtendedTrapType(Enum):
    """Extended trap types for themed dungeons."""
    SPIKE = "spike"
    POISON = "poison"
    ARROW = "arrow"
    FIRE = "fire"
    CURSE = "curse"
    LASER = "laser"
    EXPLOSION = "explosion"
    LAVA = "lava"
    ICE = "ice"
    FREEZE = "freeze"
    MADNESS = "madness"
    VOID = "void"


@dataclass
class ThemeConfig:
    """Configuration for a dungeon theme.
    
    Attributes:
        name: Display name of the theme.
        description: Flavor text describing the theme.
        enemy_types: List of enemy types that spawn in this theme.
        trap_types: List of trap types that appear in this theme.
        room_count_range: Tuple of (min, max) room counts.
        enemy_stats_modifier: Multiplier for enemy stats.
        trap_damage_modifier: Multiplier for trap damage.
        special_mechanics: List of special mechanics active in this theme.
        atmosphere_events: List of atmospheric events that can occur.
        color_scheme: Dictionary of colors for potential UI rendering.
    """
    name: str
    description: str
    enemy_types: List[ExtendedEnemyType]
    trap_types: List[ExtendedTrapType]
    room_count_range: tuple
    enemy_stats_modifier: float
    trap_damage_modifier: float
    special_mechanics: List[str] = field(default_factory=list)
    atmosphere_events: List[str] = field(default_factory=list)
    color_scheme: Dict[str, str] = field(default_factory=dict)


THEME_CONFIGS: Dict[DungeonTheme, ThemeConfig] = {
    DungeonTheme.CLASSIC_FANTASY: ThemeConfig(
        name="Classic Fantasy Dungeon",
        description="A traditional dungeon filled with goblins, orcs, and ancient traps.",
        enemy_types=[ExtendedEnemyType.GOBLIN, ExtendedEnemyType.ORC, ExtendedEnemyType.SKELETON],
        trap_types=[ExtendedTrapType.SPIKE, ExtendedTrapType.ARROW, ExtendedTrapType.POISON],
        room_count_range=(8, 12),
        enemy_stats_modifier=1.0,
        trap_damage_modifier=1.0,
        special_mechanics=["standard_combat", "loot_drops"],
        atmosphere_events=["torch_flickers", "distant_footsteps", "dripping_water"],
        color_scheme={"primary": "#8B4513", "secondary": "#DAA520", "accent": "#CD853F"}
    ),
    DungeonTheme.UNDEAD_CRYPT: ThemeConfig(
        name="Undead Crypt",
        description="An ancient burial ground where the dead refuse to stay dead.",
        enemy_types=[ExtendedEnemyType.SKELETON, ExtendedEnemyType.WRAITH],
        trap_types=[ExtendedTrapType.POISON, ExtendedTrapType.CURSE],
        room_count_range=(10, 15),
        enemy_stats_modifier=0.9,
        trap_damage_modifier=1.2,
        special_mechanics=["enemy_respawn", "curse_stacking", "life_drain"],
        atmosphere_events=["ghostly_whispers", "bones_rattling", "cold_draft", "grave_mist"],
        color_scheme={"primary": "#2F4F4F", "secondary": "#708090", "accent": "#9932CC"}
    ),
    DungeonTheme.TECHNOLOGICAL: ThemeConfig(
        name="Technological Facility",
        description="An abandoned high-tech facility with malfunctioning robots and security systems.",
        enemy_types=[ExtendedEnemyType.ROBOT, ExtendedEnemyType.TURRET],
        trap_types=[ExtendedTrapType.LASER, ExtendedTrapType.EXPLOSION],
        room_count_range=(8, 14),
        enemy_stats_modifier=1.1,
        trap_damage_modifier=1.3,
        special_mechanics=["energy_shields", "emp_vulnerability", "hacking"],
        atmosphere_events=["sparking_wires", "alarm_beeping", "servo_whirring", "power_fluctuation"],
        color_scheme={"primary": "#1C1C1C", "secondary": "#00CED1", "accent": "#FF4500"}
    ),
    DungeonTheme.VOLCANIC: ThemeConfig(
        name="Volcanic Depths",
        description="A scorching cavern system flowing with molten lava.",
        enemy_types=[ExtendedEnemyType.FIRE_ELEMENTAL, ExtendedEnemyType.LAVA_GOLEM],
        trap_types=[ExtendedTrapType.FIRE, ExtendedTrapType.LAVA],
        room_count_range=(6, 10),
        enemy_stats_modifier=1.2,
        trap_damage_modifier=1.5,
        special_mechanics=["fire_damage_bonus", "heat_damage_over_time", "lava_pools"],
        atmosphere_events=["ground_tremor", "lava_bubbling", "heat_wave", "sulfur_smell"],
        color_scheme={"primary": "#8B0000", "secondary": "#FF4500", "accent": "#FFD700"}
    ),
    DungeonTheme.ICE_CAVERN: ThemeConfig(
        name="Ice Cavern",
        description="A frozen labyrinth where the cold seeps into your bones.",
        enemy_types=[ExtendedEnemyType.FROST_WRAITH, ExtendedEnemyType.ICE_GOLEM],
        trap_types=[ExtendedTrapType.ICE, ExtendedTrapType.FREEZE],
        room_count_range=(7, 11),
        enemy_stats_modifier=1.0,
        trap_damage_modifier=1.1,
        special_mechanics=["slowed_movement", "shatter_mechanic", "frozen_enemies", "hypothermia"],
        atmosphere_events=["howling_wind", "ice_cracking", "breath_visible", "icicles_falling"],
        color_scheme={"primary": "#E0FFFF", "secondary": "#00BFFF", "accent": "#4169E1"}
    ),
    DungeonTheme.ELDRITCH_HORROR: ThemeConfig(
        name="Eldritch Dimension",
        description="A realm of chaos where reality bends and madness lurks in shadows.",
        enemy_types=[ExtendedEnemyType.VOID_SPAWN, ExtendedEnemyType.MIND_FLAYER],
        trap_types=[ExtendedTrapType.MADNESS, ExtendedTrapType.VOID],
        room_count_range=(9, 16),
        enemy_stats_modifier=1.3,
        trap_damage_modifier=1.0,
        special_mechanics=["sanity_system", "random_stat_changes", "reality_warp", "tentacle_grab"],
        atmosphere_events=["reality_flicker", "whispers_in_mind", "impossible_geometry", "eyes_watching"],
        color_scheme={"primary": "#4B0082", "secondary": "#8A2BE2", "accent": "#00FF00"}
    ),
}


ENEMY_STATS: Dict[ExtendedEnemyType, Dict[str, int]] = {
    ExtendedEnemyType.GOBLIN: {"health": 30, "attack": 8, "defense": 2},
    ExtendedEnemyType.ORC: {"health": 50, "attack": 12, "defense": 5},
    ExtendedEnemyType.SKELETON: {"health": 40, "attack": 10, "defense": 3},
    ExtendedEnemyType.DRAGON: {"health": 150, "attack": 25, "defense": 10},
    ExtendedEnemyType.WRAITH: {"health": 35, "attack": 14, "defense": 1},
    ExtendedEnemyType.ROBOT: {"health": 60, "attack": 15, "defense": 8},
    ExtendedEnemyType.TURRET: {"health": 25, "attack": 20, "defense": 12},
    ExtendedEnemyType.FIRE_ELEMENTAL: {"health": 45, "attack": 18, "defense": 3},
    ExtendedEnemyType.LAVA_GOLEM: {"health": 80, "attack": 16, "defense": 10},
    ExtendedEnemyType.FROST_WRAITH: {"health": 40, "attack": 12, "defense": 4},
    ExtendedEnemyType.ICE_GOLEM: {"health": 70, "attack": 14, "defense": 9},
    ExtendedEnemyType.VOID_SPAWN: {"health": 50, "attack": 16, "defense": 2},
    ExtendedEnemyType.MIND_FLAYER: {"health": 55, "attack": 20, "defense": 5},
}


TRAP_BASE_DAMAGE: Dict[ExtendedTrapType, int] = {
    ExtendedTrapType.SPIKE: 10,
    ExtendedTrapType.POISON: 8,
    ExtendedTrapType.ARROW: 12,
    ExtendedTrapType.FIRE: 15,
    ExtendedTrapType.CURSE: 5,
    ExtendedTrapType.LASER: 20,
    ExtendedTrapType.EXPLOSION: 25,
    ExtendedTrapType.LAVA: 30,
    ExtendedTrapType.ICE: 10,
    ExtendedTrapType.FREEZE: 8,
    ExtendedTrapType.MADNESS: 0,
    ExtendedTrapType.VOID: 15,
}


def get_theme_config(theme: DungeonTheme) -> ThemeConfig:
    """Get the configuration for a specific dungeon theme.
    
    Args:
        theme: The dungeon theme to get configuration for.
        
    Returns:
        ThemeConfig object containing all theme settings.
        
    Raises:
        KeyError: If the theme is not found in configurations.
    """
    if theme not in THEME_CONFIGS:
        raise KeyError(f"Theme {theme} not found in configurations")
    return THEME_CONFIGS[theme]


def apply_theme_to_dungeon(dungeon: Dungeon, theme: DungeonTheme) -> None:
    """Apply a theme to an existing dungeon, modifying its contents.
    
    Replaces enemies and traps with theme-appropriate versions and applies
    stat modifiers based on the theme configuration.
    
    Args:
        dungeon: The dungeon to apply the theme to.
        theme: The theme to apply.
    """
    config = get_theme_config(theme)
    
    for room_id, room in dungeon.rooms.items():
        if room.room_type == RoomType.ENTRANCE:
            continue
            
        themed_enemies = []
        for _ in room.enemies:
            themed_enemies.append(create_themed_enemy(theme))
        room.enemies = themed_enemies
        
        themed_traps = []
        for _ in room.traps:
            themed_traps.append(create_themed_trap(theme))
        room.traps = themed_traps
    
    dungeon.theme = theme
    dungeon.theme_config = config


def create_themed_enemy(theme: DungeonTheme) -> Enemy:
    """Create a new enemy appropriate for the given theme.
    
    Selects a random enemy type from the theme's allowed types and
    applies the theme's stat modifiers.
    
    Args:
        theme: The theme to create an enemy for.
        
    Returns:
        A new Enemy instance with theme-appropriate stats.
    """
    config = get_theme_config(theme)
    enemy_type = random.choice(config.enemy_types)
    stats = ENEMY_STATS[enemy_type]
    
    modifier = config.enemy_stats_modifier
    health = int(stats["health"] * modifier)
    attack = int(stats["attack"] * modifier)
    defense = int(stats["defense"] * modifier)
    
    name = enemy_type.value.replace("_", " ").title()
    
    core_type = _map_to_core_enemy_type(enemy_type)
    
    return Enemy(core_type, name, health, attack, defense)


def create_themed_trap(theme: DungeonTheme) -> Trap:
    """Create a new trap appropriate for the given theme.
    
    Selects a random trap type from the theme's allowed types and
    applies the theme's damage modifiers.
    
    Args:
        theme: The theme to create a trap for.
        
    Returns:
        A new Trap instance with theme-appropriate damage.
    """
    config = get_theme_config(theme)
    trap_type = random.choice(config.trap_types)
    base_damage = TRAP_BASE_DAMAGE[trap_type]
    
    damage = int(base_damage * config.trap_damage_modifier)
    damage += random.randint(-3, 5)
    damage = max(1, damage)
    
    core_type = _map_to_core_trap_type(trap_type)
    
    return Trap(core_type, damage)


def _map_to_core_enemy_type(extended_type: ExtendedEnemyType) -> EnemyType:
    """Map extended enemy types to core EnemyType enum.
    
    Args:
        extended_type: The extended enemy type to map.
        
    Returns:
        The corresponding core EnemyType.
    """
    mapping = {
        ExtendedEnemyType.GOBLIN: EnemyType.GOBLIN,
        ExtendedEnemyType.ORC: EnemyType.ORC,
        ExtendedEnemyType.SKELETON: EnemyType.SKELETON,
        ExtendedEnemyType.DRAGON: EnemyType.DRAGON,
        ExtendedEnemyType.WRAITH: EnemyType.SKELETON,
        ExtendedEnemyType.ROBOT: EnemyType.ORC,
        ExtendedEnemyType.TURRET: EnemyType.GOBLIN,
        ExtendedEnemyType.FIRE_ELEMENTAL: EnemyType.DRAGON,
        ExtendedEnemyType.LAVA_GOLEM: EnemyType.ORC,
        ExtendedEnemyType.FROST_WRAITH: EnemyType.SKELETON,
        ExtendedEnemyType.ICE_GOLEM: EnemyType.ORC,
        ExtendedEnemyType.VOID_SPAWN: EnemyType.SKELETON,
        ExtendedEnemyType.MIND_FLAYER: EnemyType.DRAGON,
    }
    return mapping.get(extended_type, EnemyType.GOBLIN)


def _map_to_core_trap_type(extended_type: ExtendedTrapType) -> TrapType:
    """Map extended trap types to core TrapType enum.
    
    Args:
        extended_type: The extended trap type to map.
        
    Returns:
        The corresponding core TrapType.
    """
    mapping = {
        ExtendedTrapType.SPIKE: TrapType.SPIKE,
        ExtendedTrapType.POISON: TrapType.POISON,
        ExtendedTrapType.ARROW: TrapType.ARROW,
        ExtendedTrapType.FIRE: TrapType.FIRE,
        ExtendedTrapType.CURSE: TrapType.POISON,
        ExtendedTrapType.LASER: TrapType.ARROW,
        ExtendedTrapType.EXPLOSION: TrapType.FIRE,
        ExtendedTrapType.LAVA: TrapType.FIRE,
        ExtendedTrapType.ICE: TrapType.SPIKE,
        ExtendedTrapType.FREEZE: TrapType.POISON,
        ExtendedTrapType.MADNESS: TrapType.POISON,
        ExtendedTrapType.VOID: TrapType.FIRE,
    }
    return mapping.get(extended_type, TrapType.SPIKE)
