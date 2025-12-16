"""
Event-driven system for DungeonCrawlerAI.
Allows different components to communicate without tight coupling.
"""
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass


class EventType(Enum):
    """Types of events in the game"""
    # Hero events
    HERO_MOVED = "hero_moved"
    HERO_ATTACKED = "hero_attacked"
    HERO_DAMAGED = "hero_damaged"
    HERO_DIED = "hero_died"
    HERO_LOOTED = "hero_looted"
    HERO_USED_ITEM = "hero_used_item"
    
    # Enemy events
    ENEMY_SPAWNED = "enemy_spawned"
    ENEMY_ATTACKED = "enemy_attacked"
    ENEMY_DIED = "enemy_died"
    ENEMY_MUTATED = "enemy_mutated"
    
    # Room events
    ROOM_ENTERED = "room_entered"
    ROOM_CLEARED = "room_cleared"
    ROOM_ALTERED = "room_altered"
    
    # Trap events
    TRAP_TRIGGERED = "trap_triggered"
    TRAP_PLACED = "trap_placed"
    
    # Item events
    ITEM_CORRUPTED = "item_corrupted"
    ITEM_FOUND = "item_found"
    
    # Player events
    PLAYER_ACTION = "player_action"
    SUSPICION_INCREASED = "suspicion_increased"
    
    # Game events
    GAME_STARTED = "game_started"
    GAME_ENDED = "game_ended"


@dataclass
class Event:
    """Represents a game event"""
    event_type: EventType
    data: Dict[str, Any]
    
    def __repr__(self):
        return f"Event({self.event_type.value}, {self.data})"


class EventBus:
    """Central event bus for publishing and subscribing to events"""
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self._event_history: List[Event] = []
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """Subscribe to an event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """Unsubscribe from an event type"""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]
    
    def publish(self, event: Event):
        """Publish an event to all subscribers"""
        self._event_history.append(event)
        
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                callback(event)
    
    def get_history(self, event_type: Optional[EventType] = None) -> List[Event]:
        """Get event history, optionally filtered by type"""
        if event_type:
            return [e for e in self._event_history if e.event_type == event_type]
        return self._event_history.copy()
    
    def clear_history(self):
        """Clear event history"""
        self._event_history.clear()
