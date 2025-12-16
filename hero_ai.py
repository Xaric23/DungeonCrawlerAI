"""
Hero AI using behavior trees.
The hero autonomously explores, fights, and loots while adapting to player interference.
"""
import random
from typing import Optional, List
from behavior_tree import (
    BehaviorTree, NodeStatus, SequenceNode, SelectorNode,
    ConditionNode, ActionNode, BehaviorNode
)
from models import Hero, Room, Enemy, Item, ItemType
from dungeon import Dungeon
from events import EventBus, Event, EventType


class HeroAIContext:
    """Context object for hero AI decision-making"""
    
    def __init__(self, hero: Hero, dungeon: Dungeon, event_bus: EventBus):
        self.hero = hero
        self.dungeon = dungeon
        self.event_bus = event_bus
        self.current_room: Optional[Room] = None
        self.target_enemy: Optional[Enemy] = None
        self.recent_suspicious_events = 0
    
    def get_current_room(self) -> Optional[Room]:
        """Get the hero's current room"""
        if self.hero.current_room_id is not None:
            self.current_room = self.dungeon.get_room(self.hero.current_room_id)
        return self.current_room
    
    def update_suspicion(self):
        """Update hero's suspicion based on recent events"""
        if self.recent_suspicious_events > 0:
            self.hero.increase_suspicion(self.recent_suspicious_events * 5)
            self.recent_suspicious_events = 0


class HeroAI:
    """AI controller for the hero character"""
    
    def __init__(self, hero: Hero, dungeon: Dungeon, event_bus: EventBus):
        self.context = HeroAIContext(hero, dungeon, event_bus)
        self.behavior_tree = self._build_behavior_tree()
        
        # Subscribe to events to track suspicious activity
        event_bus.subscribe(EventType.TRAP_TRIGGERED, self._on_trap_triggered)
        event_bus.subscribe(EventType.ENEMY_MUTATED, self._on_enemy_mutated)
        event_bus.subscribe(EventType.ITEM_CORRUPTED, self._on_item_corrupted)
        event_bus.subscribe(EventType.ROOM_ALTERED, self._on_room_altered)
    
    def _build_behavior_tree(self) -> BehaviorTree:
        """Build the hero's behavior tree"""
        root = SelectorNode("Hero Root")
        
        # Priority 1: Handle critical health
        critical_health_sequence = SequenceNode("Critical Health Handler")
        critical_health_sequence.add_child(
            ConditionNode("Is Critical Health", self._is_critical_health)
        )
        critical_health_sequence.add_child(
            ActionNode("Use Health Potion", self._use_health_potion)
        )
        root.add_child(critical_health_sequence)
        
        # Priority 2: Combat - fight enemies in current room
        combat_sequence = SequenceNode("Combat Handler")
        combat_sequence.add_child(
            ConditionNode("Has Enemies", self._has_enemies_in_room)
        )
        combat_sequence.add_child(
            ActionNode("Fight Enemy", self._fight_enemy)
        )
        root.add_child(combat_sequence)
        
        # Priority 3: Loot items in current room
        loot_sequence = SequenceNode("Loot Handler")
        loot_sequence.add_child(
            ConditionNode("Has Items", self._has_items_in_room)
        )
        loot_sequence.add_child(
            ActionNode("Loot Item", self._loot_item)
        )
        root.add_child(loot_sequence)
        
        # Priority 4: Explore - move to next room
        explore_sequence = SequenceNode("Exploration Handler")
        explore_sequence.add_child(
            ConditionNode("Can Explore", self._can_explore)
        )
        explore_sequence.add_child(
            ActionNode("Move to Next Room", self._move_to_next_room)
        )
        root.add_child(explore_sequence)
        
        return BehaviorTree(root)
    
    def tick(self) -> NodeStatus:
        """Execute one tick of the hero AI"""
        if not self.context.hero.is_alive:
            return NodeStatus.FAILURE
        
        self.context.update_suspicion()
        status = self.behavior_tree.tick(self.context)
        return status
    
    # Condition methods
    def _is_critical_health(self, context: HeroAIContext) -> bool:
        """Check if hero health is critical"""
        return context.hero.health < context.hero.max_health * 0.3
    
    def _has_enemies_in_room(self, context: HeroAIContext) -> bool:
        """Check if current room has living enemies"""
        room = context.get_current_room()
        return room is not None and len(room.get_alive_enemies()) > 0
    
    def _has_items_in_room(self, context: HeroAIContext) -> bool:
        """Check if current room has items to loot"""
        room = context.get_current_room()
        return room is not None and len(room.items) > 0
    
    def _can_explore(self, context: HeroAIContext) -> bool:
        """Check if hero can explore to a new room"""
        room = context.get_current_room()
        if room is None:
            return True  # Need to enter first room
        
        # Find unvisited connected rooms
        for room_id in room.connected_rooms:
            if room_id not in context.hero.visited_rooms:
                return True
        
        # If all connected rooms visited, can still revisit
        return len(room.connected_rooms) > 0
    
    # Action methods
    def _use_health_potion(self, context: HeroAIContext) -> NodeStatus:
        """Use a health potion"""
        if context.hero.use_health_potion():
            context.event_bus.publish(Event(
                EventType.HERO_USED_ITEM,
                {"hero": context.hero.name, "item": "health_potion", "health": context.hero.health}
            ))
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
    
    def _fight_enemy(self, context: HeroAIContext) -> NodeStatus:
        """Fight an enemy in the current room"""
        room = context.get_current_room()
        if room is None:
            return NodeStatus.FAILURE
        
        alive_enemies = room.get_alive_enemies()
        if not alive_enemies:
            return NodeStatus.FAILURE
        
        # Select strongest enemy (or target if set)
        if context.target_enemy and context.target_enemy.is_alive:
            enemy = context.target_enemy
        else:
            enemy = max(alive_enemies, key=lambda e: e.attack)
            context.target_enemy = enemy
        
        # Hero attacks enemy
        damage = max(1, context.hero.attack - enemy.defense)
        actual_damage = enemy.take_damage(damage)
        
        context.event_bus.publish(Event(
            EventType.HERO_ATTACKED,
            {"hero": context.hero.name, "enemy": enemy.name, "damage": actual_damage}
        ))
        
        if not enemy.is_alive:
            context.event_bus.publish(Event(
                EventType.ENEMY_DIED,
                {"enemy": enemy.name, "room": room.room_id}
            ))
            context.target_enemy = None
            return NodeStatus.SUCCESS
        
        # Enemy counter-attacks
        enemy_damage = max(1, enemy.attack - context.hero.defense)
        actual_hero_damage = context.hero.take_damage(enemy_damage)
        
        context.event_bus.publish(Event(
            EventType.HERO_DAMAGED,
            {"hero": context.hero.name, "enemy": enemy.name, "damage": actual_hero_damage}
        ))
        
        # Increase suspicion if enemy is unusually strong
        if enemy.is_mutated and not context.hero.is_suspicious():
            context.recent_suspicious_events += 1
        
        return NodeStatus.SUCCESS if context.hero.is_alive else NodeStatus.FAILURE
    
    def _loot_item(self, context: HeroAIContext) -> NodeStatus:
        """Loot an item from the current room"""
        room = context.get_current_room()
        if room is None or not room.items:
            return NodeStatus.FAILURE
        
        # If suspicious, be more cautious about looting
        if context.hero.is_suspicious():
            # Inspect item quality before taking
            item = room.items[0]
            if item.quality != ItemQuality.NORMAL:
                # Suspicious hero might skip corrupted items
                if random.random() < 0.5:
                    room.items.remove(item)  # Leave it
                    context.event_bus.publish(Event(
                        EventType.HERO_LOOTED,
                        {"hero": context.hero.name, "item": "none", "reason": "suspicious"}
                    ))
                    return NodeStatus.SUCCESS
        
        item = room.items.pop(0)
        context.hero.add_item(item)
        
        context.event_bus.publish(Event(
            EventType.HERO_LOOTED,
            {"hero": context.hero.name, "item": item.name, "quality": item.quality.value}
        ))
        
        # Increase suspicion if item was corrupted
        if item.quality != ItemQuality.NORMAL:
            context.recent_suspicious_events += 1
        
        return NodeStatus.SUCCESS
    
    def _move_to_next_room(self, context: HeroAIContext) -> NodeStatus:
        """Move to an adjacent room"""
        # Initial entry into dungeon
        if context.hero.current_room_id is None:
            context.hero.current_room_id = context.dungeon.entrance_room_id
            context.hero.visited_rooms.append(context.dungeon.entrance_room_id)
            room = context.get_current_room()
            
            context.event_bus.publish(Event(
                EventType.ROOM_ENTERED,
                {"hero": context.hero.name, "room": room.room_id, "type": room.room_type.value}
            ))
            return NodeStatus.SUCCESS
        
        room = context.get_current_room()
        if room is None or not room.connected_rooms:
            return NodeStatus.FAILURE
        
        # Choose next room
        unvisited = [rid for rid in room.connected_rooms if rid not in context.hero.visited_rooms]
        
        if unvisited:
            next_room_id = random.choice(unvisited)
        else:
            # All rooms visited, choose randomly
            next_room_id = random.choice(room.connected_rooms)
        
        # Move to room
        context.hero.current_room_id = next_room_id
        if next_room_id not in context.hero.visited_rooms:
            context.hero.visited_rooms.append(next_room_id)
        
        next_room = context.get_current_room()
        next_room.visited = True
        
        # Check for traps
        for trap in next_room.traps:
            if not trap.triggered:
                damage = trap.trigger()
                context.hero.take_damage(damage)
                context.event_bus.publish(Event(
                    EventType.TRAP_TRIGGERED,
                    {"trap": trap.trap_type.value, "damage": damage, "room": next_room_id}
                ))
                
                # Suspicious if room has many traps or altered
                if len(next_room.traps) > 2 or next_room.altered:
                    context.recent_suspicious_events += 1
        
        context.event_bus.publish(Event(
            EventType.ROOM_ENTERED,
            {"hero": context.hero.name, "room": next_room_id, "type": next_room.room_type.value}
        ))
        
        context.event_bus.publish(Event(
            EventType.HERO_MOVED,
            {"hero": context.hero.name, "from": room.room_id, "to": next_room_id}
        ))
        
        return NodeStatus.SUCCESS
    
    # Event handlers for tracking player interference
    def _on_trap_triggered(self, event: Event):
        """Track trap triggers"""
        pass  # Handled in move logic
    
    def _on_enemy_mutated(self, event: Event):
        """Track enemy mutations"""
        pass  # Handled in combat logic
    
    def _on_item_corrupted(self, event: Event):
        """Track item corruptions"""
        pass  # Handled in loot logic
    
    def _on_room_altered(self, event: Event):
        """Track room alterations"""
        pass  # Handled in move logic


from models import ItemQuality
