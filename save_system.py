"""
Save/Load System for DungeonCrawlerAI.
Handles serialization and deserialization of game state.
"""
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any

from models import (
    Hero, Room, RoomType, Item, ItemType, ItemQuality,
    Enemy, EnemyType, Trap, TrapType
)
from dungeon import Dungeon
from events import EventBus, Event, EventType
from player_curse import PlayerCurse


@dataclass
class GameSaveData:
    """Data structure for game save serialization."""
    version: str = "1.0"
    timestamp: str = ""
    turn: int = 0
    hero_data: Dict[str, Any] = field(default_factory=dict)
    dungeon_data: Dict[str, Any] = field(default_factory=dict)
    player_curse_data: Dict[str, Any] = field(default_factory=dict)
    event_history: List[Dict[str, Any]] = field(default_factory=list)
    difficulty: str = "normal"


class SaveSystem:
    """Handles saving and loading game state."""
    
    def serialize_hero(self, hero: Hero) -> dict:
        """Convert hero to dictionary for serialization."""
        return {
            "name": hero.name,
            "max_health": hero.max_health,
            "health": hero.health,
            "base_attack": hero.base_attack,
            "attack": hero.attack,
            "defense": hero.defense,
            "inventory": [self._serialize_item(item) for item in hero.inventory],
            "current_room_id": hero.current_room_id,
            "visited_rooms": hero.visited_rooms.copy(),
            "is_alive": hero.is_alive,
            "suspicion_level": hero.suspicion_level,
            "gold": hero.gold
        }
    
    def deserialize_hero(self, data: dict) -> Hero:
        """Restore hero from dictionary."""
        hero = Hero(name=data["name"])
        hero.max_health = data["max_health"]
        hero.health = data["health"]
        hero.base_attack = data["base_attack"]
        hero.attack = data["attack"]
        hero.defense = data["defense"]
        hero.current_room_id = data["current_room_id"]
        hero.visited_rooms = data["visited_rooms"].copy()
        hero.is_alive = data["is_alive"]
        hero.suspicion_level = data["suspicion_level"]
        hero.gold = data["gold"]
        hero.inventory = [self._deserialize_item(item_data) for item_data in data["inventory"]]
        return hero
    
    def serialize_room(self, room: Room) -> dict:
        """Convert room to dictionary for serialization."""
        return {
            "room_id": room.room_id,
            "room_type": room.room_type.value,
            "items": [self._serialize_item(item) for item in room.items],
            "enemies": [self._serialize_enemy(enemy) for enemy in room.enemies],
            "traps": [self._serialize_trap(trap) for trap in room.traps],
            "connected_rooms": room.connected_rooms.copy(),
            "visited": room.visited,
            "altered": room.altered
        }
    
    def deserialize_room(self, data: dict) -> Room:
        """Restore room from dictionary."""
        room = Room(
            room_id=data["room_id"],
            room_type=RoomType(data["room_type"])
        )
        room.items = [self._deserialize_item(item_data) for item_data in data["items"]]
        room.enemies = [self._deserialize_enemy(enemy_data) for enemy_data in data["enemies"]]
        room.traps = [self._deserialize_trap(trap_data) for trap_data in data["traps"]]
        room.connected_rooms = data["connected_rooms"].copy()
        room.visited = data["visited"]
        room.altered = data["altered"]
        return room
    
    def serialize_dungeon(self, dungeon: Dungeon) -> dict:
        """Convert dungeon to dictionary for serialization."""
        return {
            "num_rooms": dungeon.num_rooms,
            "entrance_room_id": dungeon.entrance_room_id,
            "rooms": {
                str(room_id): self.serialize_room(room) 
                for room_id, room in dungeon.rooms.items()
            }
        }
    
    def serialize_curse(self, curse: PlayerCurse) -> dict:
        """Convert player curse to dictionary for serialization."""
        return {
            "curse_energy": curse.curse_energy,
            "max_curse_energy": curse.max_curse_energy,
            "actions_taken": curse.actions_taken
        }
    
    def _serialize_item(self, item: Item) -> dict:
        """Convert item to dictionary."""
        return {
            "item_type": item.item_type.value,
            "name": item.name,
            "value": item.value,
            "quality": item.quality.value,
            "original_value": item.original_value
        }
    
    def _deserialize_item(self, data: dict) -> Item:
        """Restore item from dictionary."""
        item = Item(
            item_type=ItemType(data["item_type"]),
            name=data["name"],
            value=data["value"],
            quality=ItemQuality(data["quality"])
        )
        item.original_value = data.get("original_value", data["value"])
        return item
    
    def _serialize_enemy(self, enemy: Enemy) -> dict:
        """Convert enemy to dictionary."""
        return {
            "enemy_type": enemy.enemy_type.value,
            "name": enemy.name,
            "max_health": enemy.max_health,
            "health": enemy.health,
            "base_attack": enemy.base_attack,
            "attack": enemy.attack,
            "base_defense": enemy.base_defense,
            "defense": enemy.defense,
            "is_mutated": enemy.is_mutated,
            "is_alive": enemy.is_alive
        }
    
    def _deserialize_enemy(self, data: dict) -> Enemy:
        """Restore enemy from dictionary."""
        enemy = Enemy(
            enemy_type=EnemyType(data["enemy_type"]),
            name=data["name"],
            health=data["max_health"],
            attack=data["base_attack"],
            defense=data["base_defense"]
        )
        enemy.max_health = data["max_health"]
        enemy.health = data["health"]
        enemy.attack = data["attack"]
        enemy.defense = data["defense"]
        enemy.is_mutated = data["is_mutated"]
        enemy.is_alive = data["is_alive"]
        return enemy
    
    def _serialize_trap(self, trap: Trap) -> dict:
        """Convert trap to dictionary."""
        return {
            "trap_type": trap.trap_type.value,
            "damage": trap.damage,
            "triggered": trap.triggered
        }
    
    def _deserialize_trap(self, data: dict) -> Trap:
        """Restore trap from dictionary."""
        return Trap(
            trap_type=TrapType(data["trap_type"]),
            damage=data["damage"],
            triggered=data["triggered"]
        )
    
    def _serialize_event(self, event: Event) -> dict:
        """Convert event to dictionary."""
        return {
            "event_type": event.event_type.value,
            "data": event.data
        }
    
    def _deserialize_event(self, data: dict) -> Event:
        """Restore event from dictionary."""
        return Event(
            event_type=EventType(data["event_type"]),
            data=data["data"]
        )
    
    def save_game(self, filepath: str, game_data: dict) -> bool:
        """
        Save game state to JSON file.
        
        Args:
            filepath: Path to save file
            game_data: Dictionary containing game state
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True) if os.path.dirname(filepath) else None
            
            save_data = GameSaveData(
                version="1.0",
                timestamp=datetime.now().isoformat(),
                turn=game_data.get("turn", 0),
                hero_data=game_data.get("hero_data", {}),
                dungeon_data=game_data.get("dungeon_data", {}),
                player_curse_data=game_data.get("player_curse_data", {}),
                event_history=game_data.get("event_history", []),
                difficulty=game_data.get("difficulty", "normal")
            )
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(save_data), f, indent=2, ensure_ascii=False)
            
            return True
        except (IOError, OSError, TypeError) as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, filepath: str) -> Optional[dict]:
        """
        Load game state from JSON file.
        
        Args:
            filepath: Path to save file
            
        Returns:
            Dictionary containing game state, or None if load failed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "version" not in data:
                print("Invalid save file: missing version")
                return None
            
            return {
                "version": data.get("version", "1.0"),
                "timestamp": data.get("timestamp", ""),
                "turn": data.get("turn", 0),
                "hero_data": data.get("hero_data", {}),
                "dungeon_data": data.get("dungeon_data", {}),
                "player_curse_data": data.get("player_curse_data", {}),
                "event_history": data.get("event_history", []),
                "difficulty": data.get("difficulty", "normal")
            }
        except FileNotFoundError:
            print(f"Save file not found: {filepath}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing save file: {e}")
            return None
        except (IOError, OSError) as e:
            print(f"Error loading game: {e}")
            return None
    
    def get_save_files(self, directory: str) -> List[str]:
        """
        List all save files in a directory.
        
        Args:
            directory: Directory to search for save files
            
        Returns:
            List of save file paths sorted by modification time (newest first)
        """
        try:
            if not os.path.exists(directory):
                return []
            
            save_files = []
            for filename in os.listdir(directory):
                if filename.endswith('.json'):
                    filepath = os.path.join(directory, filename)
                    if os.path.isfile(filepath):
                        save_files.append(filepath)
            
            save_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            return save_files
        except (IOError, OSError) as e:
            print(f"Error listing save files: {e}")
            return []
    
    def deserialize_dungeon(self, data: dict, event_bus: EventBus) -> Dungeon:
        """
        Restore dungeon from dictionary.
        
        Args:
            data: Serialized dungeon data
            event_bus: Event bus for the dungeon (not used by Dungeon directly but kept for consistency)
            
        Returns:
            Restored Dungeon instance
        """
        dungeon = object.__new__(Dungeon)
        dungeon.num_rooms = data["num_rooms"]
        dungeon.entrance_room_id = data["entrance_room_id"]
        dungeon.rooms = {}
        
        for room_id_str, room_data in data["rooms"].items():
            room = self.deserialize_room(room_data)
            dungeon.rooms[int(room_id_str)] = room
        
        return dungeon
    
    def deserialize_curse(self, data: dict, dungeon: Dungeon, event_bus: EventBus) -> PlayerCurse:
        """
        Restore player curse from dictionary.
        
        Args:
            data: Serialized curse data
            dungeon: Dungeon instance
            event_bus: Event bus instance
            
        Returns:
            Restored PlayerCurse instance
        """
        curse = PlayerCurse(dungeon, event_bus)
        curse.curse_energy = data["curse_energy"]
        curse.max_curse_energy = data["max_curse_energy"]
        curse.actions_taken = data["actions_taken"]
        return curse
    
    def deserialize_event_history(self, data: List[dict]) -> List[Event]:
        """
        Restore event history from list of dictionaries.
        
        Args:
            data: List of serialized events
            
        Returns:
            List of Event instances
        """
        return [self._deserialize_event(event_data) for event_data in data]
