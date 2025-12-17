"""
Dynamic Dungeon Events for DungeonCrawlerAI.
Implements random and triggered events that affect gameplay.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import random

from models import Hero, Room, Trap, TrapType, Enemy, EnemyType
from dungeon import Dungeon
from events import EventBus, Event, EventType


class DungeonEventType(Enum):
    """Types of dynamic dungeon events."""
    
    # Natural events
    COLLAPSE = "collapse"
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    GAS_LEAK = "gas_leak"
    
    # Supernatural events
    GHOST_SPAWN = "ghost_spawn"
    BLESSING = "blessing"
    CURSE_WEAKENED = "curse_weakened"
    SOUL_ECHO = "soul_echo"
    
    # Curse events
    CURSE_STRENGTHENED = "curse_strengthened"
    ENERGY_SURGE = "energy_surge"
    VOID_RIFT = "void_rift"
    
    # Hero events
    HERO_BLESSED = "hero_blessed"
    SECOND_WIND = "second_wind"
    DIVINE_INTERVENTION = "divine_intervention"


@dataclass
class DungeonEvent:
    """Represents a dynamic dungeon event."""
    
    event_type: DungeonEventType
    name: str
    description: str
    duration: int
    probability: float
    affects_hero: bool
    affects_curse: bool
    effect_data: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self):
        return f"DungeonEvent({self.name}, duration={self.duration})"


# Event definitions with their properties
EVENT_DEFINITIONS: Dict[DungeonEventType, Dict[str, Any]] = {
    # Natural events
    DungeonEventType.COLLAPSE: {
        "name": "Cave Collapse",
        "description": "Part of the dungeon collapses, blocking a room.",
        "duration": 5,
        "probability": 0.03,
        "affects_hero": True,
        "affects_curse": False,
        "effect_data": {"damage": 25, "blocks_room": True}
    },
    DungeonEventType.FLOOD: {
        "name": "Underground Flood",
        "description": "Water floods into the dungeon, slowing movement.",
        "duration": 4,
        "probability": 0.04,
        "affects_hero": True,
        "affects_curse": False,
        "effect_data": {"movement_penalty": 0.5, "damage_per_turn": 5}
    },
    DungeonEventType.EARTHQUAKE: {
        "name": "Earthquake",
        "description": "A violent tremor shakes the dungeon, triggering all traps.",
        "duration": 1,
        "probability": 0.02,
        "affects_hero": True,
        "affects_curse": False,
        "effect_data": {"triggers_all_traps": True}
    },
    DungeonEventType.GAS_LEAK: {
        "name": "Toxic Gas Leak",
        "description": "Poisonous gas seeps through the dungeon.",
        "duration": 3,
        "probability": 0.05,
        "affects_hero": True,
        "affects_curse": False,
        "effect_data": {"poison_damage": 8, "vision_reduced": True}
    },
    
    # Supernatural events
    DungeonEventType.GHOST_SPAWN: {
        "name": "Spectral Manifestation",
        "description": "Ghosts materialize from the dungeon's dark history.",
        "duration": 3,
        "probability": 0.04,
        "affects_hero": True,
        "affects_curse": False,
        "effect_data": {"spawn_ghosts": 2, "ghost_damage": 10}
    },
    DungeonEventType.BLESSING: {
        "name": "Divine Blessing",
        "description": "A holy presence grants temporary protection to the hero.",
        "duration": 4,
        "probability": 0.03,
        "affects_hero": True,
        "affects_curse": True,
        "effect_data": {"temp_hp": 30, "curse_cost_modifier": 1.5}
    },
    DungeonEventType.CURSE_WEAKENED: {
        "name": "Curse Weakened",
        "description": "Ancient wards temporarily suppress curse powers.",
        "duration": 3,
        "probability": 0.03,
        "affects_hero": False,
        "affects_curse": True,
        "effect_data": {"curse_power_modifier": 0.5, "energy_regen_modifier": 0.5}
    },
    DungeonEventType.SOUL_ECHO: {
        "name": "Soul Echo",
        "description": "Echoes of fallen adventurers provide cryptic guidance.",
        "duration": 2,
        "probability": 0.05,
        "affects_hero": True,
        "affects_curse": False,
        "effect_data": {"reveals_traps": True, "attack_bonus": 5}
    },
    
    # Curse events
    DungeonEventType.CURSE_STRENGTHENED: {
        "name": "Curse Strengthened",
        "description": "Dark energy surges through the dungeon.",
        "duration": 3,
        "probability": 0.04,
        "affects_hero": False,
        "affects_curse": True,
        "effect_data": {"curse_cost_modifier": 0.7, "energy_regen_bonus": 15}
    },
    DungeonEventType.ENERGY_SURGE: {
        "name": "Energy Surge",
        "description": "A wave of dark energy restores curse power.",
        "duration": 1,
        "probability": 0.05,
        "affects_hero": False,
        "affects_curse": True,
        "effect_data": {"energy_restore": 50}
    },
    DungeonEventType.VOID_RIFT: {
        "name": "Void Rift",
        "description": "A rift to the void opens, empowering dark forces.",
        "duration": 4,
        "probability": 0.02,
        "affects_hero": True,
        "affects_curse": True,
        "effect_data": {"hero_damage_per_turn": 5, "curse_cost_modifier": 0.5}
    },
    
    # Hero events
    DungeonEventType.HERO_BLESSED: {
        "name": "Hero Blessed",
        "description": "The hero receives a blessing from the gods.",
        "duration": 3,
        "probability": 0.03,
        "affects_hero": True,
        "affects_curse": False,
        "effect_data": {"attack_bonus": 10, "defense_bonus": 5}
    },
    DungeonEventType.SECOND_WIND: {
        "name": "Second Wind",
        "description": "The hero finds renewed strength in dire circumstances.",
        "duration": 2,
        "probability": 0.04,
        "affects_hero": True,
        "affects_curse": False,
        "effect_data": {"heal_percent": 0.25, "attack_bonus": 5}
    },
    DungeonEventType.DIVINE_INTERVENTION: {
        "name": "Divine Intervention",
        "description": "The gods intervene to protect their champion.",
        "duration": 1,
        "probability": 0.01,
        "affects_hero": True,
        "affects_curse": True,
        "effect_data": {"full_heal": True, "curse_stunned": True}
    }
}


class EventManager:
    """Manages dynamic dungeon events."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        Initialize the event manager.
        
        Args:
            event_bus: Optional event bus for publishing events.
        """
        self.active_events: List[DungeonEvent] = []
        self.event_history: List[DungeonEvent] = []
        self.turn_count: int = 0
        self.event_bus = event_bus
        self._blocked_rooms: List[int] = []
    
    def tick(self) -> Optional[DungeonEvent]:
        """
        Process a turn and potentially trigger a random event.
        
        Returns:
            A triggered DungeonEvent if one occurred, None otherwise.
        """
        self.turn_count += 1
        self.update_active_events()
        
        for event_type, definition in EVENT_DEFINITIONS.items():
            if random.random() < definition["probability"]:
                return self.trigger_event(event_type)
        
        return None
    
    def trigger_event(self, event_type: DungeonEventType) -> DungeonEvent:
        """
        Force trigger a specific event type.
        
        Args:
            event_type: The type of event to trigger.
            
        Returns:
            The triggered DungeonEvent.
        """
        definition = EVENT_DEFINITIONS[event_type]
        
        event = DungeonEvent(
            event_type=event_type,
            name=definition["name"],
            description=definition["description"],
            duration=definition["duration"],
            probability=definition["probability"],
            affects_hero=definition["affects_hero"],
            affects_curse=definition["affects_curse"],
            effect_data=definition["effect_data"].copy()
        )
        
        self.active_events.append(event)
        self.event_history.append(event)
        
        if self.event_bus:
            self.event_bus.publish(Event(
                EventType.ROOM_ALTERED,
                {"event": event.name, "duration": event.duration}
            ))
        
        return event
    
    def apply_event_effects(
        self,
        event: DungeonEvent,
        hero: Hero,
        curse: Any,
        dungeon: Dungeon
    ) -> Dict[str, Any]:
        """
        Apply the effects of an event to the game state.
        
        Args:
            event: The event to apply.
            hero: The hero to affect.
            curse: The PlayerCurse to affect.
            dungeon: The dungeon to affect.
            
        Returns:
            A dict describing the effects applied.
        """
        effects_applied = {"event": event.name, "effects": []}
        data = event.effect_data
        
        if event.event_type == DungeonEventType.COLLAPSE:
            if hero.current_room_id is not None:
                connected = dungeon.get_connected_rooms(hero.current_room_id)
                if connected:
                    blocked_room = random.choice(connected)
                    self._blocked_rooms.append(blocked_room)
                    effects_applied["effects"].append(f"Room {blocked_room} blocked")
                    
                    room = dungeon.get_room(blocked_room)
                    if room and hero.current_room_id == blocked_room:
                        damage = hero.take_damage(data.get("damage", 25))
                        effects_applied["effects"].append(f"Hero took {damage} collapse damage")
        
        elif event.event_type == DungeonEventType.FLOOD:
            damage = data.get("damage_per_turn", 5)
            hero.take_damage(damage)
            effects_applied["effects"].append(f"Hero took {damage} flood damage")
        
        elif event.event_type == DungeonEventType.EARTHQUAKE:
            if data.get("triggers_all_traps"):
                total_damage = 0
                for room in dungeon.rooms.values():
                    for trap in room.traps:
                        if not trap.triggered and room.room_id == hero.current_room_id:
                            damage = trap.trigger()
                            total_damage += damage
                if total_damage > 0:
                    hero.take_damage(total_damage)
                    effects_applied["effects"].append(f"Earthquake triggered traps for {total_damage} damage")
        
        elif event.event_type == DungeonEventType.GAS_LEAK:
            poison_damage = data.get("poison_damage", 8)
            hero.take_damage(poison_damage)
            effects_applied["effects"].append(f"Hero took {poison_damage} poison damage")
        
        elif event.event_type == DungeonEventType.GHOST_SPAWN:
            if hero.current_room_id is not None:
                room = dungeon.get_room(hero.current_room_id)
                if room:
                    num_ghosts = data.get("spawn_ghosts", 2)
                    for _ in range(num_ghosts):
                        ghost = Enemy(EnemyType.SKELETON, "Ghost", 20, data.get("ghost_damage", 10), 0)
                        room.add_enemy(ghost)
                    effects_applied["effects"].append(f"Spawned {num_ghosts} ghosts")
        
        elif event.event_type == DungeonEventType.BLESSING:
            temp_hp = data.get("temp_hp", 30)
            hero.max_health += temp_hp
            hero.health += temp_hp
            effects_applied["effects"].append(f"Hero gained {temp_hp} temporary HP")
        
        elif event.event_type == DungeonEventType.CURSE_WEAKENED:
            if hasattr(curse, 'curse_energy'):
                curse.curse_energy = int(curse.curse_energy * data.get("curse_power_modifier", 0.5))
                effects_applied["effects"].append("Curse power weakened")
        
        elif event.event_type == DungeonEventType.SOUL_ECHO:
            hero.attack += data.get("attack_bonus", 5)
            effects_applied["effects"].append(f"Hero attack increased by {data.get('attack_bonus', 5)}")
        
        elif event.event_type == DungeonEventType.CURSE_STRENGTHENED:
            if hasattr(curse, 'curse_energy') and hasattr(curse, 'max_curse_energy'):
                bonus = data.get("energy_regen_bonus", 15)
                curse.curse_energy = min(curse.max_curse_energy, curse.curse_energy + bonus)
                effects_applied["effects"].append(f"Curse gained {bonus} energy")
        
        elif event.event_type == DungeonEventType.ENERGY_SURGE:
            if hasattr(curse, 'curse_energy') and hasattr(curse, 'max_curse_energy'):
                restore = data.get("energy_restore", 50)
                curse.curse_energy = min(curse.max_curse_energy, curse.curse_energy + restore)
                effects_applied["effects"].append(f"Curse restored {restore} energy")
        
        elif event.event_type == DungeonEventType.VOID_RIFT:
            damage = data.get("hero_damage_per_turn", 5)
            hero.take_damage(damage)
            effects_applied["effects"].append(f"Void rift dealt {damage} damage to hero")
        
        elif event.event_type == DungeonEventType.HERO_BLESSED:
            hero.attack += data.get("attack_bonus", 10)
            hero.defense += data.get("defense_bonus", 5)
            effects_applied["effects"].append("Hero blessed with bonus stats")
        
        elif event.event_type == DungeonEventType.SECOND_WIND:
            heal_percent = data.get("heal_percent", 0.25)
            heal_amount = int(hero.max_health * heal_percent)
            hero.heal(heal_amount)
            hero.attack += data.get("attack_bonus", 5)
            effects_applied["effects"].append(f"Hero healed {heal_amount} HP and gained attack bonus")
        
        elif event.event_type == DungeonEventType.DIVINE_INTERVENTION:
            if data.get("full_heal"):
                hero.health = hero.max_health
                effects_applied["effects"].append("Hero fully healed by divine intervention")
        
        return effects_applied
    
    def update_active_events(self) -> List[DungeonEvent]:
        """
        Decrement durations and remove expired events.
        
        Returns:
            List of expired events that were removed.
        """
        expired = []
        still_active = []
        
        for event in self.active_events:
            event.duration -= 1
            if event.duration <= 0:
                expired.append(event)
                if event.event_type == DungeonEventType.COLLAPSE:
                    self._blocked_rooms.clear()
            else:
                still_active.append(event)
        
        self.active_events = still_active
        return expired
    
    def get_active_modifiers(self) -> Dict[str, Any]:
        """
        Return current stat modifiers from active events.
        
        Returns:
            Dict containing all active stat modifiers.
        """
        modifiers = {
            "hero_attack_bonus": 0,
            "hero_defense_bonus": 0,
            "hero_damage_per_turn": 0,
            "curse_cost_modifier": 1.0,
            "curse_energy_regen_modifier": 1.0,
            "blocked_rooms": self._blocked_rooms.copy(),
            "movement_penalty": 1.0,
            "curse_stunned": False
        }
        
        for event in self.active_events:
            data = event.effect_data
            
            if "attack_bonus" in data:
                modifiers["hero_attack_bonus"] += data["attack_bonus"]
            if "defense_bonus" in data:
                modifiers["hero_defense_bonus"] += data["defense_bonus"]
            if "hero_damage_per_turn" in data:
                modifiers["hero_damage_per_turn"] += data["hero_damage_per_turn"]
            if "curse_cost_modifier" in data:
                modifiers["curse_cost_modifier"] *= data["curse_cost_modifier"]
            if "energy_regen_modifier" in data:
                modifiers["curse_energy_regen_modifier"] *= data["energy_regen_modifier"]
            if "movement_penalty" in data:
                modifiers["movement_penalty"] *= data["movement_penalty"]
            if data.get("curse_stunned"):
                modifiers["curse_stunned"] = True
        
        return modifiers
    
    def get_event_forecast(self) -> List[str]:
        """
        Predict likely events based on current game state.
        
        Returns:
            List of strings describing likely upcoming events.
        """
        forecasts = []
        
        high_probability_events = [
            (etype, defn) for etype, defn in EVENT_DEFINITIONS.items()
            if defn["probability"] >= 0.04
        ]
        
        for event_type, definition in high_probability_events:
            already_active = any(e.event_type == event_type for e in self.active_events)
            if not already_active:
                forecasts.append(
                    f"{definition['name']} ({definition['probability']*100:.0f}% chance)"
                )
        
        if self.turn_count > 10 and self.turn_count % 5 == 0:
            forecasts.append("Environmental instability increasing...")
        
        curse_events_active = sum(
            1 for e in self.active_events 
            if e.event_type in [
                DungeonEventType.CURSE_STRENGTHENED,
                DungeonEventType.ENERGY_SURGE,
                DungeonEventType.VOID_RIFT
            ]
        )
        if curse_events_active >= 2:
            forecasts.append("Divine intervention likely due to curse activity")
        
        hero_events_active = sum(
            1 for e in self.active_events
            if e.event_type in [
                DungeonEventType.HERO_BLESSED,
                DungeonEventType.SECOND_WIND,
                DungeonEventType.DIVINE_INTERVENTION
            ]
        )
        if hero_events_active >= 2:
            forecasts.append("Curse backlash likely due to divine presence")
        
        return forecasts
    
    def get_blocked_rooms(self) -> List[int]:
        """Get list of currently blocked room IDs."""
        return self._blocked_rooms.copy()
    
    def is_room_blocked(self, room_id: int) -> bool:
        """Check if a specific room is blocked."""
        return room_id in self._blocked_rooms
