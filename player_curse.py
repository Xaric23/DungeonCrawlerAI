"""
Player Curse system.
The player controls the dungeon as a "curse" and can interfere with the hero's journey.
"""
from models import Trap, TrapType, Hero
from dungeon import Dungeon
from events import EventBus, Event, EventType


class PlayerCurse:
    """
    Represents the player's curse powers.
    Player can manipulate the dungeon but must be careful not to be too obvious.
    """
    
    def __init__(self, dungeon: Dungeon, event_bus: EventBus):
        self.dungeon = dungeon
        self.event_bus = event_bus
        self.curse_energy = 100  # Resource for using curse powers
        self.max_curse_energy = 100
        self.actions_taken = 0
    
    def regenerate_energy(self, amount: int = 10):
        """Regenerate curse energy"""
        self.curse_energy = min(self.max_curse_energy, self.curse_energy + amount)
    
    def trigger_trap(self, room_id: int, trap_index: int = 0) -> bool:
        """
        Manually trigger a trap in a room.
        Cost: 5 energy
        Suspicion: Low (traps are expected)
        """
        cost = 5
        if self.curse_energy < cost:
            return False
        
        room = self.dungeon.get_room(room_id)
        if not room or trap_index >= len(room.traps):
            return False
        
        trap = room.traps[trap_index]
        if trap.triggered:
            return False
        
        self.curse_energy -= cost
        self.actions_taken += 1
        
        # Trap will be triggered naturally when hero enters/is in room
        # This just makes it happen immediately
        
        self.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {"action": "trigger_trap", "room": room_id, "trap": trap.trap_type.value}
        ))
        
        return True
    
    def alter_room(self, room_id: int) -> bool:
        """
        Alter a room's layout, adding traps or hazards.
        Cost: 20 energy
        Suspicion: Medium (hero may notice environmental changes)
        """
        cost = 20
        if self.curse_energy < cost:
            return False
        
        room = self.dungeon.get_room(room_id)
        if not room or room.altered:
            return False
        
        self.curse_energy -= cost
        self.actions_taken += 1
        
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
        Cost: 15 energy
        Suspicion: High (hero will notice cursed items)
        """
        cost = 15
        if self.curse_energy < cost:
            return False
        
        room = self.dungeon.get_room(room_id)
        if not room or item_index >= len(room.items):
            return False
        
        item = room.items[item_index]
        
        self.curse_energy -= cost
        self.actions_taken += 1
        
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
        Cost: 25 energy
        Suspicion: Very High (hero will definitely notice stronger enemies)
        """
        cost = 25
        if self.curse_energy < cost:
            return False
        
        room = self.dungeon.get_room(room_id)
        if not room or enemy_index >= len(room.enemies):
            return False
        
        enemy = room.enemies[enemy_index]
        if enemy.is_mutated or not enemy.is_alive:
            return False
        
        self.curse_energy -= cost
        self.actions_taken += 1
        
        enemy.mutate()
        
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
        Cost: 15 energy
        Suspicion: Medium
        """
        cost = 15
        if self.curse_energy < cost:
            return False
        
        room = self.dungeon.get_room(room_id)
        if not room:
            return False
        
        self.curse_energy -= cost
        self.actions_taken += 1
        
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
    
    def get_available_actions(self, hero: Hero) -> dict:
        """Get list of available actions based on hero's current location"""
        if hero.current_room_id is None:
            return {}
        
        room = self.dungeon.get_room(hero.current_room_id)
        if not room:
            return {}
        
        actions = {}
        
        # Check what can be done in current room and nearby rooms
        for room_id in [hero.current_room_id] + room.connected_rooms:
            target_room = self.dungeon.get_room(room_id)
            if not target_room:
                continue
            
            room_actions = []
            
            # Traps that can be triggered
            if target_room.traps:
                for i, trap in enumerate(target_room.traps):
                    if not trap.triggered:
                        room_actions.append(f"trigger_trap_{i}")
            
            # Can alter room if not already altered
            if not target_room.altered and self.curse_energy >= 20:
                room_actions.append("alter_room")
            
            # Items that can be corrupted
            if target_room.items:
                for i, item in enumerate(target_room.items):
                    if self.curse_energy >= 15:
                        room_actions.append(f"corrupt_item_{i}")
            
            # Enemies that can be mutated
            alive_enemies = target_room.get_alive_enemies()
            if alive_enemies:
                for enemy in alive_enemies:
                    # Find the original index in the full enemy list
                    original_idx = target_room.enemies.index(enemy)
                    if not enemy.is_mutated and self.curse_energy >= 25:
                        room_actions.append(f"mutate_enemy_{original_idx}")
            
            # Can spawn traps
            if self.curse_energy >= 15:
                room_actions.append("spawn_trap")
            
            if room_actions:
                actions[room_id] = room_actions
        
        return actions
    
    def __repr__(self):
        return f"PlayerCurse(energy={self.curse_energy}/{self.max_curse_energy}, actions={self.actions_taken})"
