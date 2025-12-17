"""
Advanced Curse Powers for DungeonCrawlerAI.
Extends the base PlayerCurse with more powerful abilities organized by tier.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional
import random

from models import Hero, Enemy, EnemyType, Trap, TrapType
from dungeon import Dungeon
from events import EventBus, Event, EventType


class CursePowerTier(Enum):
    """Tier levels for curse powers"""
    BASIC = "basic"
    ADVANCED = "advanced"
    ULTIMATE = "ultimate"


@dataclass
class CursePower:
    """Represents a curse power and its properties"""
    name: str
    description: str
    energy_cost: int
    suspicion_increase: int
    tier: CursePowerTier
    cooldown: int  # turns


class AdvancedCursePowers:
    """
    Extended curse powers with tiered abilities.
    Provides basic, advanced, and ultimate powers to manipulate the dungeon.
    """
    
    POWERS: Dict[str, CursePower] = {
        # Basic powers
        "trigger_trap": CursePower("trigger_trap", "Trigger a trap in a room", 5, 5, CursePowerTier.BASIC, 0),
        "alter_room": CursePower("alter_room", "Alter a room's layout", 20, 15, CursePowerTier.BASIC, 2),
        "corrupt_loot": CursePower("corrupt_loot", "Corrupt an item", 15, 20, CursePowerTier.BASIC, 1),
        "mutate_enemy": CursePower("mutate_enemy", "Mutate an enemy", 25, 25, CursePowerTier.BASIC, 2),
        "spawn_trap": CursePower("spawn_trap", "Spawn a new trap", 15, 10, CursePowerTier.BASIC, 1),
        # Advanced powers
        "teleport_hero": CursePower("teleport_hero", "Teleport hero to a random room", 35, 40, CursePowerTier.ADVANCED, 5),
        "charm_enemy": CursePower("charm_enemy", "Convert enemy to help hero temporarily", 40, 15, CursePowerTier.ADVANCED, 4),
        "time_freeze": CursePower("time_freeze", "Freeze hero for turns", 50, 30, CursePowerTier.ADVANCED, 6),
        "mass_corruption": CursePower("mass_corruption", "Corrupt all items in room", 45, 35, CursePowerTier.ADVANCED, 5),
        "summon_enemy": CursePower("summon_enemy", "Spawn an enemy in a room", 30, 20, CursePowerTier.ADVANCED, 3),
        # Ultimate powers
        "doom": CursePower("doom", "Mark hero for death after X turns", 80, 50, CursePowerTier.ULTIMATE, 10),
        "dark_blessing": CursePower("dark_blessing", "Double all curse effects for 5 turns", 100, 45, CursePowerTier.ULTIMATE, 15),
        "dungeon_collapse": CursePower("dungeon_collapse", "Destroy room and damage hero", 75, 60, CursePowerTier.ULTIMATE, 8),
    }
    
    def __init__(self, dungeon: Dungeon, event_bus: EventBus):
        """
        Initialize advanced curse powers.
        
        Args:
            dungeon: The dungeon instance to manipulate
            event_bus: Event bus for publishing events
        """
        self.dungeon = dungeon
        self.event_bus = event_bus
        self.curse_energy = 100
        self.max_curse_energy = 150
        self.actions_taken = 0
        self.current_turn = 0
        
        # Cooldown tracking: power_name -> turn when available
        self._cooldowns: Dict[str, int] = {}
        
        # Active effects
        self._time_freeze_remaining = 0
        self._dark_blessing_remaining = 0
        self._doom_targets: Dict[int, int] = {}  # hero_id -> turns remaining
        self._charmed_enemies: Dict[int, int] = {}  # enemy index -> turns remaining
        self._destroyed_rooms: set = set()
    
    def advance_turn(self):
        """Advance the turn counter and process ongoing effects."""
        self.current_turn += 1
        self._process_doom_effects()
        self._process_charm_decay()
        
        if self._time_freeze_remaining > 0:
            self._time_freeze_remaining -= 1
        if self._dark_blessing_remaining > 0:
            self._dark_blessing_remaining -= 1
    
    def _process_doom_effects(self):
        """Process doom countdowns."""
        expired = []
        for hero_id, turns in self._doom_targets.items():
            self._doom_targets[hero_id] = turns - 1
            if self._doom_targets[hero_id] <= 0:
                expired.append(hero_id)
                self.event_bus.publish(Event(
                    EventType.PLAYER_ACTION,
                    {"action": "doom_triggered", "hero_id": hero_id}
                ))
        for hero_id in expired:
            del self._doom_targets[hero_id]
    
    def _process_charm_decay(self):
        """Process charmed enemy duration decay."""
        expired = []
        for enemy_key, turns in self._charmed_enemies.items():
            self._charmed_enemies[enemy_key] = turns - 1
            if self._charmed_enemies[enemy_key] <= 0:
                expired.append(enemy_key)
        for key in expired:
            del self._charmed_enemies[key]
    
    def regenerate_energy(self, amount: int = 10):
        """Regenerate curse energy."""
        self.curse_energy = min(self.max_curse_energy, self.curse_energy + amount)
    
    def is_power_available(self, power_name: str) -> bool:
        """
        Check if a power is available (off cooldown and enough energy).
        
        Args:
            power_name: Name of the power to check
            
        Returns:
            True if power can be used, False otherwise
        """
        if power_name not in self.POWERS:
            return False
        
        power = self.POWERS[power_name]
        
        # Check energy
        if self.curse_energy < power.energy_cost:
            return False
        
        # Check cooldown
        if power_name in self._cooldowns:
            if self.current_turn < self._cooldowns[power_name]:
                return False
        
        return True
    
    def _apply_cost_and_cooldown(self, power_name: str) -> bool:
        """Apply energy cost and set cooldown for a power."""
        if not self.is_power_available(power_name):
            return False
        
        power = self.POWERS[power_name]
        cost = power.energy_cost
        
        # Dark blessing doubles effects but also costs
        if self._dark_blessing_remaining > 0 and power.tier != CursePowerTier.ULTIMATE:
            cost = int(cost * 0.75)  # Reduced cost during dark blessing
        
        self.curse_energy -= cost
        self.actions_taken += 1
        
        if power.cooldown > 0:
            self._cooldowns[power_name] = self.current_turn + power.cooldown
        
        return True
    
    def _get_suspicion_amount(self, power_name: str) -> int:
        """Get suspicion increase for a power, modified by dark blessing."""
        power = self.POWERS[power_name]
        suspicion = power.suspicion_increase
        if self._dark_blessing_remaining > 0:
            suspicion = int(suspicion * 0.5)  # Reduced suspicion during dark blessing
        return suspicion
    
    # === Basic Powers ===
    
    def trigger_trap(self, room_id: int, trap_index: int = 0) -> bool:
        """
        Manually trigger a trap in a room.
        
        Args:
            room_id: Target room ID
            trap_index: Index of trap to trigger
            
        Returns:
            True if successful, False otherwise
        """
        if not self._apply_cost_and_cooldown("trigger_trap"):
            return False
        
        room = self.dungeon.get_room(room_id)
        if not room or trap_index >= len(room.traps):
            return False
        
        trap = room.traps[trap_index]
        if trap.triggered:
            return False
        
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "trigger_trap", "room": room_id, "trap": trap.trap_type.value}
        ))
        return True
    
    def alter_room(self, room_id: int) -> bool:
        """
        Alter a room's layout, adding traps or hazards.
        
        Args:
            room_id: Target room ID
            
        Returns:
            True if successful, False otherwise
        """
        room = self.dungeon.get_room(room_id)
        if not room or room.altered:
            return False
        
        if not self._apply_cost_and_cooldown("alter_room"):
            return False
        
        room.alter_room()
        
        self.event_bus.publish(Event(
            EventType.ROOM_ALTERED,
            {"room": room_id, "type": room.room_type.value}
        ))
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "alter_room", "room": room_id}
        ))
        return True
    
    def corrupt_loot(self, room_id: int, item_index: int = 0) -> bool:
        """
        Corrupt an item in a room, making it harmful.
        
        Args:
            room_id: Target room ID
            item_index: Index of item to corrupt
            
        Returns:
            True if successful, False otherwise
        """
        room = self.dungeon.get_room(room_id)
        if not room or item_index >= len(room.items):
            return False
        
        if not self._apply_cost_and_cooldown("corrupt_loot"):
            return False
        
        item = room.items[item_index]
        item.corrupt()
        
        self.event_bus.publish(Event(
            EventType.ITEM_CORRUPTED,
            {"item": item.name, "room": room_id, "quality": item.quality.value}
        ))
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "corrupt_loot", "room": room_id, "item": item.name}
        ))
        return True
    
    def mutate_enemy(self, room_id: int, enemy_index: int = 0) -> bool:
        """
        Mutate an enemy, making it stronger.
        
        Args:
            room_id: Target room ID
            enemy_index: Index of enemy to mutate
            
        Returns:
            True if successful, False otherwise
        """
        room = self.dungeon.get_room(room_id)
        if not room or enemy_index >= len(room.enemies):
            return False
        
        enemy = room.enemies[enemy_index]
        if enemy.is_mutated or not enemy.is_alive:
            return False
        
        if not self._apply_cost_and_cooldown("mutate_enemy"):
            return False
        
        enemy.mutate()
        
        # Dark blessing doubles mutation effects
        if self._dark_blessing_remaining > 0:
            enemy.attack = int(enemy.attack * 1.25)
            enemy.defense = int(enemy.defense * 1.25)
        
        self.event_bus.publish(Event(
            EventType.ENEMY_MUTATED,
            {"enemy": enemy.name, "room": room_id}
        ))
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "mutate_enemy", "room": room_id, "enemy": enemy.name}
        ))
        return True
    
    def spawn_trap(self, room_id: int, trap_type: TrapType, damage: int = 20) -> bool:
        """
        Spawn a new trap in a room.
        
        Args:
            room_id: Target room ID
            trap_type: Type of trap to spawn
            damage: Damage dealt by the trap
            
        Returns:
            True if successful, False otherwise
        """
        room = self.dungeon.get_room(room_id)
        if not room:
            return False
        
        if not self._apply_cost_and_cooldown("spawn_trap"):
            return False
        
        # Dark blessing increases trap damage
        if self._dark_blessing_remaining > 0:
            damage = int(damage * 1.5)
        
        trap = Trap(trap_type, damage)
        room.add_trap(trap)
        
        self.event_bus.publish(Event(
            EventType.TRAP_PLACED,
            {"trap": trap_type.value, "room": room_id, "damage": damage}
        ))
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "spawn_trap", "room": room_id, "trap": trap_type.value}
        ))
        return True
    
    # === Advanced Powers ===
    
    def teleport_hero(self, hero: Hero, room_id: int) -> bool:
        """
        Teleport the hero to a random room in the dungeon.
        
        Args:
            hero: The hero to teleport
            room_id: Ignored - hero is teleported to a random room
            
        Returns:
            True if successful, False otherwise
        """
        if not self._apply_cost_and_cooldown("teleport_hero"):
            return False
        
        # Get all valid room IDs excluding destroyed rooms
        valid_rooms = [
            rid for rid in self.dungeon.rooms.keys()
            if rid not in self._destroyed_rooms and rid != hero.current_room_id
        ]
        
        if not valid_rooms:
            return False
        
        target_room = random.choice(valid_rooms)
        old_room = hero.current_room_id
        hero.current_room_id = target_room
        
        hero.increase_suspicion(self._get_suspicion_amount("teleport_hero"))
        
        self.event_bus.publish(Event(
            EventType.HERO_MOVED,
            {"from": old_room, "to": target_room, "teleported": True}
        ))
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "teleport_hero", "from": old_room, "to": target_room}
        ))
        return True
    
    def charm_enemy(self, room_id: int, enemy_idx: int) -> bool:
        """
        Convert an enemy to temporarily help the hero.
        The charmed enemy will fight other enemies for 3 turns.
        
        Args:
            room_id: Room containing the enemy
            enemy_idx: Index of enemy to charm
            
        Returns:
            True if successful, False otherwise
        """
        room = self.dungeon.get_room(room_id)
        if not room or enemy_idx >= len(room.enemies):
            return False
        
        enemy = room.enemies[enemy_idx]
        if not enemy.is_alive:
            return False
        
        if not self._apply_cost_and_cooldown("charm_enemy"):
            return False
        
        charm_key = room_id * 1000 + enemy_idx
        charm_duration = 5 if self._dark_blessing_remaining > 0 else 3
        self._charmed_enemies[charm_key] = charm_duration
        
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "charm_enemy", "room": room_id, "enemy": enemy.name, "duration": charm_duration}
        ))
        return True
    
    def is_enemy_charmed(self, room_id: int, enemy_idx: int) -> bool:
        """Check if an enemy is currently charmed."""
        charm_key = room_id * 1000 + enemy_idx
        return charm_key in self._charmed_enemies
    
    def time_freeze(self, duration: int) -> bool:
        """
        Freeze the hero in place for a number of turns.
        
        Args:
            duration: Number of turns to freeze (max 3)
            
        Returns:
            True if successful, False otherwise
        """
        duration = min(duration, 3)  # Cap at 3 turns
        
        if not self._apply_cost_and_cooldown("time_freeze"):
            return False
        
        # Dark blessing increases freeze duration
        if self._dark_blessing_remaining > 0:
            duration = min(duration + 1, 4)
        
        self._time_freeze_remaining = duration
        
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "time_freeze", "duration": duration}
        ))
        return True
    
    def is_hero_frozen(self) -> bool:
        """Check if the hero is currently frozen."""
        return self._time_freeze_remaining > 0
    
    def mass_corruption(self, room_id: int) -> bool:
        """
        Corrupt all items in a room at once.
        
        Args:
            room_id: Target room ID
            
        Returns:
            True if successful, False otherwise
        """
        room = self.dungeon.get_room(room_id)
        if not room or not room.items:
            return False
        
        if not self._apply_cost_and_cooldown("mass_corruption"):
            return False
        
        corrupted_items = []
        for item in room.items:
            item.corrupt()
            # Dark blessing corrupts twice
            if self._dark_blessing_remaining > 0:
                item.corrupt()
            corrupted_items.append(item.name)
        
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "mass_corruption", "room": room_id, "items": corrupted_items}
        ))
        return True
    
    def summon_enemy(self, room_id: int, enemy_type: EnemyType) -> bool:
        """
        Spawn a new enemy in a room.
        
        Args:
            room_id: Target room ID
            enemy_type: Type of enemy to summon
            
        Returns:
            True if successful, False otherwise
        """
        room = self.dungeon.get_room(room_id)
        if not room or room_id in self._destroyed_rooms:
            return False
        
        if not self._apply_cost_and_cooldown("summon_enemy"):
            return False
        
        enemy = self._create_enemy(enemy_type)
        
        # Dark blessing creates stronger enemies
        if self._dark_blessing_remaining > 0:
            enemy.health = int(enemy.health * 1.3)
            enemy.max_health = int(enemy.max_health * 1.3)
            enemy.attack = int(enemy.attack * 1.2)
        
        room.add_enemy(enemy)
        
        self.event_bus.publish(Event(
            EventType.ENEMY_SPAWNED,
            {"enemy": enemy.name, "room": room_id, "type": enemy_type.value}
        ))
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "summon_enemy", "room": room_id, "enemy_type": enemy_type.value}
        ))
        return True
    
    def _create_enemy(self, enemy_type: EnemyType) -> Enemy:
        """Create an enemy of the specified type."""
        if enemy_type == EnemyType.GOBLIN:
            return Enemy(EnemyType.GOBLIN, "Summoned Goblin", 30, 8, 2)
        elif enemy_type == EnemyType.ORC:
            return Enemy(EnemyType.ORC, "Summoned Orc", 50, 12, 5)
        elif enemy_type == EnemyType.SKELETON:
            return Enemy(EnemyType.SKELETON, "Summoned Skeleton", 40, 10, 3)
        else:
            return Enemy(EnemyType.DRAGON, "Summoned Dragon", 150, 25, 10)
    
    # === Ultimate Powers ===
    
    def doom(self, hero: Hero) -> bool:
        """
        Mark the hero for death after a number of turns.
        When doom expires, the hero takes massive damage.
        
        Args:
            hero: The hero to doom
            
        Returns:
            True if successful, False otherwise
        """
        if not hero.is_alive:
            return False
        
        if not self._apply_cost_and_cooldown("doom"):
            return False
        
        doom_turns = 5
        self._doom_targets[id(hero)] = doom_turns
        
        hero.increase_suspicion(self._get_suspicion_amount("doom"))
        
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "doom", "hero": hero.name, "turns": doom_turns}
        ))
        return True
    
    def is_hero_doomed(self, hero: Hero) -> Optional[int]:
        """
        Check if hero is doomed and return turns remaining.
        
        Args:
            hero: The hero to check
            
        Returns:
            Turns remaining if doomed, None otherwise
        """
        return self._doom_targets.get(id(hero))
    
    def dark_blessing(self) -> bool:
        """
        Activate dark blessing, doubling all curse effects for 5 turns.
        Also reduces energy costs and suspicion gains.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._apply_cost_and_cooldown("dark_blessing"):
            return False
        
        self._dark_blessing_remaining = 5
        
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "dark_blessing", "duration": 5}
        ))
        return True
    
    def is_dark_blessing_active(self) -> bool:
        """Check if dark blessing is currently active."""
        return self._dark_blessing_remaining > 0
    
    def dungeon_collapse(self, room_id: int, hero: Hero) -> bool:
        """
        Collapse a room, destroying it and damaging the hero if present.
        The room becomes inaccessible and connections are severed.
        
        Args:
            room_id: Room to collapse
            hero: The hero (to apply damage if in room)
            
        Returns:
            True if successful, False otherwise
        """
        room = self.dungeon.get_room(room_id)
        if not room or room_id in self._destroyed_rooms:
            return False
        
        # Can't destroy entrance or boss room
        if room_id == 0 or room_id == len(self.dungeon.rooms) - 1:
            return False
        
        if not self._apply_cost_and_cooldown("dungeon_collapse"):
            return False
        
        damage = 40 if self._dark_blessing_remaining > 0 else 30
        
        # Damage hero if in room
        if hero.current_room_id == room_id:
            hero.take_damage(damage)
            # Force teleport hero to connected room
            if room.connected_rooms and hero.is_alive:
                hero.current_room_id = room.connected_rooms[0]
        
        # Mark room as destroyed
        self._destroyed_rooms.add(room_id)
        
        # Remove connections to this room
        for connected_id in room.connected_rooms:
            connected_room = self.dungeon.get_room(connected_id)
            if connected_room and room_id in connected_room.connected_rooms:
                connected_room.connected_rooms.remove(room_id)
        
        room.connected_rooms.clear()
        
        hero.increase_suspicion(self._get_suspicion_amount("dungeon_collapse"))
        
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "dungeon_collapse", "room": room_id, "damage": damage}
        ))
        return True
    
    def is_room_destroyed(self, room_id: int) -> bool:
        """Check if a room has been destroyed."""
        return room_id in self._destroyed_rooms
    
    def get_cooldown_remaining(self, power_name: str) -> int:
        """
        Get the remaining cooldown turns for a power.
        
        Args:
            power_name: Name of the power
            
        Returns:
            Turns remaining, 0 if ready
        """
        if power_name not in self._cooldowns:
            return 0
        return max(0, self._cooldowns[power_name] - self.current_turn)
    
    def __repr__(self):
        blessing = " [DARK BLESSING]" if self._dark_blessing_remaining > 0 else ""
        freeze = f" [FREEZE:{self._time_freeze_remaining}]" if self._time_freeze_remaining > 0 else ""
        return f"AdvancedCursePowers(energy={self.curse_energy}/{self.max_curse_energy}, turn={self.current_turn}{blessing}{freeze})"
