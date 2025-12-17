"""
Hero Archetypes for DungeonCrawlerAI.
Defines different hero classes with unique stats, abilities, and passives.
"""
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import Hero


class HeroArchetype(Enum):
    """Available hero archetypes with distinct playstyles."""
    WARRIOR = "warrior"
    ROGUE = "rogue"
    PALADIN = "paladin"
    MAGE = "mage"
    BERSERKER = "berserker"
    RANGER = "ranger"


@dataclass
class ArchetypeStats:
    """
    Statistics and abilities for a hero archetype.
    
    Attributes:
        base_health: Starting health points.
        base_attack: Starting attack power.
        base_defense: Starting defense value.
        special_ability_name: Name of the archetype's special ability.
        special_ability_description: Description of what the special ability does.
        passive_name: Name of the archetype's passive ability.
        passive_description: Description of the passive effect.
    """
    base_health: int
    base_attack: int
    base_defense: int
    special_ability_name: str
    special_ability_description: str
    passive_name: str
    passive_description: str


ARCHETYPE_DATA: dict[HeroArchetype, ArchetypeStats] = {
    HeroArchetype.WARRIOR: ArchetypeStats(
        base_health=120,
        base_attack=18,
        base_defense=10,
        special_ability_name="Shield Bash",
        special_ability_description="Stuns enemy for 1 turn",
        passive_name="Iron Will",
        passive_description="+20% max health",
    ),
    HeroArchetype.ROGUE: ArchetypeStats(
        base_health=80,
        base_attack=22,
        base_defense=4,
        special_ability_name="Backstab",
        special_ability_description="2x damage from behind",
        passive_name="Evasion",
        passive_description="30% dodge chance",
    ),
    HeroArchetype.PALADIN: ArchetypeStats(
        base_health=100,
        base_attack=14,
        base_defense=12,
        special_ability_name="Divine Shield",
        special_ability_description="Immune for 1 turn",
        passive_name="Holy Aura",
        passive_description="Regen 5 HP/turn",
    ),
    HeroArchetype.MAGE: ArchetypeStats(
        base_health=70,
        base_attack=25,
        base_defense=3,
        special_ability_name="Fireball",
        special_ability_description="AoE damage",
        passive_name="Mana Shield",
        passive_description="Absorbs 20% damage",
    ),
    HeroArchetype.BERSERKER: ArchetypeStats(
        base_health=90,
        base_attack=20,
        base_defense=6,
        special_ability_name="Rage",
        special_ability_description="+50% attack, -25% defense",
        passive_name="Bloodlust",
        passive_description="Heal on kill",
    ),
    HeroArchetype.RANGER: ArchetypeStats(
        base_health=85,
        base_attack=16,
        base_defense=5,
        special_ability_name="Multi-shot",
        special_ability_description="Hit all enemies",
        passive_name="Trap Sense",
        passive_description="Detect traps",
    ),
}


def get_archetype_stats(archetype: HeroArchetype) -> ArchetypeStats:
    """
    Get the stats and abilities for a given archetype.
    
    Args:
        archetype: The hero archetype to retrieve stats for.
        
    Returns:
        ArchetypeStats containing all stats and ability info for the archetype.
        
    Raises:
        KeyError: If the archetype is not defined in ARCHETYPE_DATA.
    """
    return ARCHETYPE_DATA[archetype]


def apply_archetype_to_hero(hero: "Hero", archetype: HeroArchetype) -> "Hero":
    """
    Apply an archetype's base stats to a hero, modifying their attributes.
    
    Args:
        hero: The Hero instance to modify.
        archetype: The archetype to apply.
        
    Returns:
        The modified Hero instance with updated stats and archetype attributes.
    """
    stats = get_archetype_stats(archetype)
    
    hero.max_health = stats.base_health
    hero.health = stats.base_health
    hero.base_attack = stats.base_attack
    hero.attack = stats.base_attack
    hero.defense = stats.base_defense
    
    hero.archetype = archetype
    hero.special_ability_name = stats.special_ability_name
    hero.special_ability_description = stats.special_ability_description
    hero.passive_name = stats.passive_name
    hero.passive_description = stats.passive_description
    
    return hero
