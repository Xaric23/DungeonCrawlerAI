"""
Core data models for DungeonCrawlerAI.
Defines the basic entities: Items, Enemies, Rooms, and Hero.
"""
from enum import Enum
from typing import List, Optional
import random


class ItemType(Enum):
    """Types of items in the dungeon"""
    HEALTH_POTION = "health_potion"
    WEAPON = "weapon"
    ARMOR = "armor"
    TREASURE = "treasure"


class ItemQuality(Enum):
    """Quality levels for items"""
    NORMAL = "normal"
    CORRUPTED = "corrupted"
    CURSED = "cursed"


class Item:
    """Represents an item in the dungeon"""
    def __init__(self, item_type: ItemType, name: str, value: int, quality: ItemQuality = ItemQuality.NORMAL):
        self.item_type = item_type
        self.name = name
        self.value = value
        self.quality = quality
        self.original_value = value
    
    def corrupt(self):
        """Corrupt the item, reducing its effectiveness"""
        if self.quality == ItemQuality.NORMAL:
            self.quality = ItemQuality.CORRUPTED
            self.value = int(self.value * 0.5)
        elif self.quality == ItemQuality.CORRUPTED:
            self.quality = ItemQuality.CURSED
            self.value = -abs(self.value)  # Now harmful
    
    def __repr__(self):
        return f"Item({self.name}, {self.quality.value}, value={self.value})"


class EnemyType(Enum):
    """Types of enemies"""
    GOBLIN = "goblin"
    ORC = "orc"
    SKELETON = "skeleton"
    DRAGON = "dragon"


class Enemy:
    """Represents an enemy in the dungeon"""
    def __init__(self, enemy_type: EnemyType, name: str, health: int, attack: int, defense: int):
        self.enemy_type = enemy_type
        self.name = name
        self.max_health = health
        self.health = health
        self.base_attack = attack
        self.attack = attack
        self.base_defense = defense
        self.defense = defense
        self.is_mutated = False
        self.is_alive = True
    
    def mutate(self):
        """Mutate the enemy, increasing its power"""
        if not self.is_mutated:
            self.is_mutated = True
            self.attack = int(self.attack * 1.5)
            self.defense = int(self.defense * 1.3)
            self.max_health = int(self.max_health * 1.4)
            self.health = min(self.max_health, int(self.health * 1.4))
    
    def take_damage(self, damage: int):
        """Apply damage to the enemy"""
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        if self.health <= 0:
            self.is_alive = False
        return actual_damage
    
    def __repr__(self):
        mutation = " (MUTATED)" if self.is_mutated else ""
        return f"Enemy({self.name}{mutation}, HP={self.health}/{self.max_health}, ATK={self.attack})"


class TrapType(Enum):
    """Types of traps"""
    SPIKE = "spike"
    POISON = "poison"
    ARROW = "arrow"
    FIRE = "fire"


class Trap:
    """Represents a trap in a room"""
    def __init__(self, trap_type: TrapType, damage: int, triggered: bool = False):
        self.trap_type = trap_type
        self.damage = damage
        self.triggered = triggered
    
    def trigger(self) -> int:
        """Trigger the trap and return damage dealt"""
        if not self.triggered:
            self.triggered = True
            return self.damage
        return 0
    
    def __repr__(self):
        status = "TRIGGERED" if self.triggered else "ARMED"
        return f"Trap({self.trap_type.value}, {status}, dmg={self.damage})"


class RoomType(Enum):
    """Types of rooms"""
    ENTRANCE = "entrance"
    NORMAL = "normal"
    TREASURE = "treasure"
    BOSS = "boss"
    TRAP = "trap"


class Room:
    """Represents a room in the dungeon"""
    def __init__(self, room_id: int, room_type: RoomType):
        self.room_id = room_id
        self.room_type = room_type
        self.items: List[Item] = []
        self.enemies: List[Enemy] = []
        self.traps: List[Trap] = []
        self.connected_rooms: List[int] = []
        self.visited = False
        self.altered = False
    
    def add_item(self, item: Item):
        """Add an item to the room"""
        self.items.append(item)
    
    def add_enemy(self, enemy: Enemy):
        """Add an enemy to the room"""
        self.enemies.append(enemy)
    
    def add_trap(self, trap: Trap):
        """Add a trap to the room"""
        self.traps.append(trap)
    
    def alter_room(self):
        """Alter the room's layout/difficulty"""
        if not self.altered:
            self.altered = True
            # Add a random trap
            trap_types = list(TrapType)
            new_trap = Trap(random.choice(trap_types), random.randint(10, 30))
            self.traps.append(new_trap)
    
    def get_alive_enemies(self) -> List[Enemy]:
        """Get list of alive enemies in the room"""
        return [e for e in self.enemies if e.is_alive]
    
    def __repr__(self):
        status = "(ALTERED)" if self.altered else ""
        return f"Room({self.room_id}, {self.room_type.value}{status}, enemies={len(self.get_alive_enemies())}, items={len(self.items)}, traps={len(self.traps)})"


class Hero:
    """The AI-controlled hero"""
    def __init__(self, name: str = "Hero"):
        self.name = name
        self.max_health = 100
        self.health = 100
        self.base_attack = 15
        self.attack = 15
        self.defense = 5
        self.inventory: List[Item] = []
        self.current_room_id: Optional[int] = None
        self.visited_rooms: List[int] = []
        self.is_alive = True
        self.suspicion_level = 0  # Tracks awareness of player interference
        self.gold = 0
    
    def take_damage(self, damage: int) -> int:
        """Apply damage to the hero"""
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        if self.health <= 0:
            self.is_alive = False
            self.health = 0
        return actual_damage
    
    def heal(self, amount: int):
        """Heal the hero"""
        if amount < 0:
            raise ValueError("Heal amount must be non-negative. Use take_damage for negative effects.")
        self.health = min(self.max_health, self.health + amount)
    
    def add_item(self, item: Item):
        """Add item to inventory and apply effects"""
        self.inventory.append(item)
        
        if item.item_type == ItemType.WEAPON:
            self.attack += item.value
        elif item.item_type == ItemType.ARMOR:
            self.defense += item.value
        elif item.item_type == ItemType.TREASURE:
            self.gold += item.value
        elif item.item_type == ItemType.HEALTH_POTION:
            # Apply health effects from potions (including cursed ones)
            if item.quality == ItemQuality.CURSED:
                self.health = max(1, self.health + item.value)  # item.value is negative
    
    def use_health_potion(self) -> bool:
        """Use a health potion from inventory"""
        for item in self.inventory:
            if item.item_type == ItemType.HEALTH_POTION and item.quality != ItemQuality.CURSED:
                self.heal(item.value)
                self.inventory.remove(item)
                return True
        return False
    
    def increase_suspicion(self, amount: int):
        """Increase hero's suspicion of player interference"""
        self.suspicion_level = min(100, self.suspicion_level + amount)
    
    def is_suspicious(self) -> bool:
        """Check if hero is highly suspicious"""
        return self.suspicion_level > 50
    
    def __repr__(self):
        suspicion = f" (SUSPICIOUS: {self.suspicion_level}%)" if self.suspicion_level > 30 else ""
        return f"Hero({self.name}, HP={self.health}/{self.max_health}, ATK={self.attack}, DEF={self.defense}{suspicion})"
