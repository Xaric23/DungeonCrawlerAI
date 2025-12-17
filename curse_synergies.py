"""
Curse Synergies/Combos for DungeonCrawlerAI.
Tracks power sequences and rewards strategic combinations with bonus effects.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from advanced_curse_powers import AdvancedCursePowers
from events import EventBus, Event, EventType


@dataclass
class CurseSynergy:
    """Represents a synergy between curse powers."""
    name: str
    description: str
    powers_required: List[str]
    bonus_effect: str
    energy_discount: int
    suspicion_modifier: float


CORRUPTION_CHAIN = CurseSynergy(
    name="Corruption Chain",
    description="Triple corruption causes items to spread their curse",
    powers_required=["corrupt_loot", "corrupt_loot", "corrupt_loot"],
    bonus_effect="Items spread corruption to adjacent room items",
    energy_discount=20,
    suspicion_modifier=0.8
)

TRAP_GAUNTLET = CurseSynergy(
    name="Trap Gauntlet",
    description="Transform a room into a deadly gauntlet",
    powers_required=["spawn_trap", "alter_room", "trigger_trap"],
    bonus_effect="Room becomes deadly, +50% trap damage",
    energy_discount=25,
    suspicion_modifier=1.2
)

MUTATION_SURGE = CurseSynergy(
    name="Mutation Surge",
    description="Mutated enemies gain hive mind coordination",
    powers_required=["mutate_enemy", "mutate_enemy", "summon_enemy"],
    bonus_effect="Mutated enemies coordinate attacks",
    energy_discount=15,
    suspicion_modifier=1.0
)

DOOM_COMBO = CurseSynergy(
    name="Doom Combo",
    description="Accelerate the inevitable",
    powers_required=["time_freeze", "mass_corruption", "doom"],
    bonus_effect="Doom countdown reduced by 2 turns",
    energy_discount=30,
    suspicion_modifier=1.5
)

DARK_RITUAL = CurseSynergy(
    name="Dark Ritual",
    description="Sacrifice a charmed enemy for explosive results",
    powers_required=["charm_enemy", "doom", "dark_blessing"],
    bonus_effect="Charmed enemy explodes on death",
    energy_discount=20,
    suspicion_modifier=0.7
)

CHAOS_STORM = CurseSynergy(
    name="Chaos Storm",
    description="Create a deadly trap maze from dungeon ruins",
    powers_required=["dungeon_collapse", "teleport_hero", "spawn_trap"],
    bonus_effect="Create deadly trap maze",
    energy_discount=35,
    suspicion_modifier=1.3
)

ALL_SYNERGIES = [
    CORRUPTION_CHAIN,
    TRAP_GAUNTLET,
    MUTATION_SURGE,
    DOOM_COMBO,
    DARK_RITUAL,
    CHAOS_STORM,
]


class SynergyTracker:
    """
    Tracks recently used powers and detects when synergies are triggered.
    Applies bonus effects when power sequences match defined synergies.
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None, max_history: int = 10):
        """
        Initialize the synergy tracker.
        
        Args:
            event_bus: Optional event bus for publishing synergy events
            max_history: Maximum number of recent powers to track
        """
        self.recent_powers: List[str] = []
        self.active_synergies: List[CurseSynergy] = []
        self._max_history = max_history
        self._event_bus = event_bus
        self._synergy_count: Dict[str, int] = {}
    
    def track_power(self, power_name: str) -> None:
        """
        Add a power to the recent powers list.
        
        Args:
            power_name: Name of the power that was used
        """
        self.recent_powers.append(power_name)
        if len(self.recent_powers) > self._max_history:
            self.recent_powers.pop(0)
    
    def check_synergies(self) -> Optional[CurseSynergy]:
        """
        Check if any synergy has been triggered by recent power usage.
        
        Returns:
            The triggered CurseSynergy if found, None otherwise
        """
        for synergy in ALL_SYNERGIES:
            if self._matches_synergy(synergy):
                self.active_synergies.append(synergy)
                self._synergy_count[synergy.name] = self._synergy_count.get(synergy.name, 0) + 1
                
                if self._event_bus:
                    self._event_bus.publish(Event(
                        EventType.PLAYER_ACTION,
                        {
                            "action": "synergy_triggered",
                            "synergy": synergy.name,
                            "bonus": synergy.bonus_effect
                        }
                    ))
                
                self._clear_matched_powers(synergy)
                return synergy
        
        return None
    
    def _matches_synergy(self, synergy: CurseSynergy) -> bool:
        """
        Check if recent powers contain the required sequence for a synergy.
        
        Args:
            synergy: The synergy to check against
            
        Returns:
            True if the synergy sequence is present in recent powers
        """
        required = synergy.powers_required
        if len(self.recent_powers) < len(required):
            return False
        
        for i in range(len(self.recent_powers) - len(required) + 1):
            if self.recent_powers[i:i + len(required)] == required:
                return True
        
        return False
    
    def _clear_matched_powers(self, synergy: CurseSynergy) -> None:
        """
        Remove the matched power sequence from recent powers.
        
        Args:
            synergy: The synergy that was matched
        """
        required = synergy.powers_required
        for i in range(len(self.recent_powers) - len(required) + 1):
            if self.recent_powers[i:i + len(required)] == required:
                del self.recent_powers[i:i + len(required)]
                return
    
    def apply_synergy_bonus(self, synergy: CurseSynergy, curse: AdvancedCursePowers) -> None:
        """
        Apply the bonus effects of a triggered synergy.
        
        Args:
            synergy: The synergy to apply
            curse: The AdvancedCursePowers instance to modify
        """
        energy_refund = int(curse.max_curse_energy * (synergy.energy_discount / 100))
        curse.curse_energy = min(curse.max_curse_energy, curse.curse_energy + energy_refund)
        
        if synergy.name == "Corruption Chain":
            pass
        
        elif synergy.name == "Trap Gauntlet":
            for room in curse.dungeon.rooms.values():
                for trap in room.traps:
                    trap.damage = int(trap.damage * 1.5)
        
        elif synergy.name == "Mutation Surge":
            pass
        
        elif synergy.name == "Doom Combo":
            for hero_id in list(curse._doom_targets.keys()):
                curse._doom_targets[hero_id] = max(1, curse._doom_targets[hero_id] - 2)
        
        elif synergy.name == "Dark Ritual":
            pass
        
        elif synergy.name == "Chaos Storm":
            pass
        
        if self._event_bus:
            self._event_bus.publish(Event(
                EventType.PLAYER_ACTION,
                {
                    "action": "synergy_applied",
                    "synergy": synergy.name,
                    "energy_refund": energy_refund
                }
            ))
    
    def get_progress_toward_synergies(self) -> Dict[str, Dict]:
        """
        Get progress toward each available synergy.
        
        Returns:
            Dictionary mapping synergy names to progress info:
            - 'required': List of required powers
            - 'matched': Number of consecutive powers matched from start
            - 'percentage': Completion percentage (0-100)
        """
        progress = {}
        
        for synergy in ALL_SYNERGIES:
            required = synergy.powers_required
            matched = 0
            
            for i, power in enumerate(required):
                if i < len(self.recent_powers) and self.recent_powers[-(len(required) - i):]:
                    check_idx = len(self.recent_powers) - (len(required) - i)
                    if check_idx >= 0 and check_idx < len(self.recent_powers):
                        if self.recent_powers[check_idx] == power:
                            matched += 1
                        else:
                            break
                    else:
                        break
                else:
                    break
            
            tail_matched = 0
            for i in range(min(len(self.recent_powers), len(required))):
                tail_start = len(self.recent_powers) - i - 1
                if tail_start >= 0 and self.recent_powers[tail_start:] == required[:i + 1]:
                    tail_matched = i + 1
            
            matched = tail_matched
            percentage = int((matched / len(required)) * 100) if required else 0
            
            progress[synergy.name] = {
                "required": required,
                "matched": matched,
                "percentage": percentage,
                "next_power": required[matched] if matched < len(required) else None
            }
        
        return progress
    
    def clear_active_synergies(self) -> None:
        """Clear all active synergies."""
        self.active_synergies.clear()
    
    def get_synergy_stats(self) -> Dict[str, int]:
        """
        Get statistics on synergy usage.
        
        Returns:
            Dictionary mapping synergy names to times triggered
        """
        return self._synergy_count.copy()
    
    def __repr__(self) -> str:
        active = [s.name for s in self.active_synergies]
        return f"SynergyTracker(recent={len(self.recent_powers)}, active={active})"
