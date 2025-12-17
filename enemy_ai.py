"""
Advanced Enemy AI with behavior trees for DungeonCrawlerAI.
Implements various enemy behavior patterns including aggressive, defensive,
cowardly, tactical, and boss behaviors.
"""
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass
import random

from behavior_tree import (
    BehaviorTree, BehaviorNode, NodeStatus,
    ActionNode, ConditionNode, SequenceNode, SelectorNode
)
from models import Enemy, Room, Hero
from events import EventBus, Event, EventType


class EnemyBehavior(Enum):
    """Behavior patterns for enemy AI."""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    COWARDLY = "cowardly"
    TACTICAL = "tactical"
    BOSS = "boss"


@dataclass
class EnemyAIContext:
    """Context data passed to behavior tree nodes during enemy AI execution."""
    enemy: Enemy
    room: Room
    hero: Hero
    event_bus: EventBus
    nearby_allies: List[Enemy]


class EnemyAI:
    """
    AI controller for enemy entities using behavior trees.
    
    Each enemy can have different behavior patterns that determine
    how they react to the hero and environment.
    """
    
    def __init__(self, enemy: Enemy, behavior: EnemyBehavior, event_bus: EventBus):
        """
        Initialize enemy AI with a specific behavior pattern.
        
        Args:
            enemy: The enemy entity this AI controls.
            behavior: The behavior pattern to use.
            event_bus: Event bus for publishing game events.
        """
        self.enemy = enemy
        self.behavior = behavior
        self.event_bus = event_bus
        self.behavior_tree = self._build_behavior_tree()
        self._enraged = False
        self._attack_pattern = 0
    
    def _build_behavior_tree(self) -> BehaviorTree:
        """
        Create the behavior tree based on the enemy's behavior type.
        
        Returns:
            BehaviorTree configured for the enemy's behavior pattern.
        """
        if self.behavior == EnemyBehavior.AGGRESSIVE:
            return self._build_aggressive_tree()
        elif self.behavior == EnemyBehavior.DEFENSIVE:
            return self._build_defensive_tree()
        elif self.behavior == EnemyBehavior.COWARDLY:
            return self._build_cowardly_tree()
        elif self.behavior == EnemyBehavior.TACTICAL:
            return self._build_tactical_tree()
        elif self.behavior == EnemyBehavior.BOSS:
            return self._build_boss_tree()
        else:
            return self._build_aggressive_tree()
    
    def _build_aggressive_tree(self) -> BehaviorTree:
        """Build behavior tree for aggressive enemies that always attack."""
        root = SelectorNode("AggressiveRoot", [
            SequenceNode("AttackSequence", [
                ConditionNode("CanAttack", self._can_attack),
                ActionNode("Attack", self._attack_hero)
            ]),
            ActionNode("Idle", lambda ctx: NodeStatus.SUCCESS)
        ])
        return BehaviorTree(root)
    
    def _build_defensive_tree(self) -> BehaviorTree:
        """Build behavior tree for defensive enemies that retreat when hurt."""
        root = SelectorNode("DefensiveRoot", [
            SequenceNode("RetreatSequence", [
                ConditionNode("ShouldFlee", self._should_flee),
                ActionNode("Flee", self._flee)
            ]),
            SequenceNode("DefendSequence", [
                ConditionNode("HeroInRoom", self._hero_in_room),
                ConditionNode("CanAttack", self._can_attack),
                ActionNode("Attack", self._attack_hero)
            ]),
            ActionNode("Defend", lambda ctx: NodeStatus.SUCCESS)
        ])
        return BehaviorTree(root)
    
    def _build_cowardly_tree(self) -> BehaviorTree:
        """Build behavior tree for cowardly enemies that flee and call for help."""
        root = SelectorNode("CowardlyRoot", [
            SequenceNode("FleeSequence", [
                ConditionNode("ShouldFlee", self._should_flee),
                ActionNode("CallForHelp", self._call_for_help),
                ActionNode("Flee", self._flee)
            ]),
            SequenceNode("CautiousAttack", [
                ConditionNode("CanAttack", self._can_attack),
                ConditionNode("HealthyEnough", lambda ctx: ctx.enemy.health > ctx.enemy.max_health * 0.5),
                ActionNode("Attack", self._attack_hero)
            ]),
            ActionNode("Hide", lambda ctx: NodeStatus.SUCCESS)
        ])
        return BehaviorTree(root)
    
    def _build_tactical_tree(self) -> BehaviorTree:
        """Build behavior tree for tactical enemies that coordinate attacks."""
        root = SelectorNode("TacticalRoot", [
            SequenceNode("CoordinatedAttack", [
                ConditionNode("HasAllies", lambda ctx: len(ctx.nearby_allies) > 0),
                ConditionNode("CanAttack", self._can_attack),
                ActionNode("CoordinateAttack", self._coordinate_attack)
            ]),
            SequenceNode("FocusedAttack", [
                ConditionNode("CanAttack", self._can_attack),
                ActionNode("Attack", self._attack_hero)
            ]),
            SequenceNode("TacticalRetreat", [
                ConditionNode("ShouldFlee", self._should_flee),
                ActionNode("Flee", self._flee)
            ]),
            ActionNode("UseTerrain", self._use_terrain)
        ])
        return BehaviorTree(root)
    
    def _build_boss_tree(self) -> BehaviorTree:
        """Build behavior tree for boss enemies with multiple attack patterns."""
        root = SelectorNode("BossRoot", [
            SequenceNode("EnrageSequence", [
                ConditionNode("LowHealth", lambda ctx: ctx.enemy.health < ctx.enemy.max_health * 0.3),
                ActionNode("Enrage", self._enrage),
                ActionNode("SummonMinions", self._summon_minions)
            ]),
            SequenceNode("SpecialAttack", [
                ConditionNode("CanAttack", self._can_attack),
                ActionNode("BossAttackPattern", self._boss_attack_pattern)
            ]),
            ActionNode("Intimidate", lambda ctx: NodeStatus.SUCCESS)
        ])
        return BehaviorTree(root)
    
    def tick(self, context: EnemyAIContext) -> NodeStatus:
        """
        Execute one tick of the enemy AI.
        
        Args:
            context: The current game context for decision making.
            
        Returns:
            NodeStatus indicating the result of the AI tick.
        """
        if not self.enemy.is_alive:
            return NodeStatus.FAILURE
        return self.behavior_tree.tick(context)
    
    def _can_attack(self, ctx: EnemyAIContext) -> bool:
        """
        Check if the enemy can attack the hero.
        
        Args:
            ctx: Current AI context.
            
        Returns:
            True if the enemy can attack, False otherwise.
        """
        return (
            ctx.enemy.is_alive and
            ctx.hero.is_alive and
            ctx.hero.current_room_id == ctx.room.room_id
        )
    
    def _attack_hero(self, ctx: EnemyAIContext) -> NodeStatus:
        """
        Execute an attack against the hero.
        
        Args:
            ctx: Current AI context.
            
        Returns:
            NodeStatus.SUCCESS if attack executed, FAILURE otherwise.
        """
        if not self._can_attack(ctx):
            return NodeStatus.FAILURE
        
        damage = ctx.enemy.attack
        actual_damage = ctx.hero.take_damage(damage)
        
        ctx.event_bus.publish(Event(
            EventType.ENEMY_ATTACKED,
            {
                "enemy": ctx.enemy.name,
                "target": ctx.hero.name,
                "damage": actual_damage,
                "enemy_type": ctx.enemy.enemy_type.value
            }
        ))
        
        if not ctx.hero.is_alive:
            ctx.event_bus.publish(Event(
                EventType.HERO_DIED,
                {"killed_by": ctx.enemy.name}
            ))
        
        return NodeStatus.SUCCESS
    
    def _should_flee(self, ctx: EnemyAIContext) -> bool:
        """
        Determine if the enemy should flee.
        
        Args:
            ctx: Current AI context.
            
        Returns:
            True if enemy should flee, False otherwise.
        """
        health_threshold = 0.3 if self.behavior == EnemyBehavior.DEFENSIVE else 0.5
        return ctx.enemy.health < ctx.enemy.max_health * health_threshold
    
    def _flee(self, ctx: EnemyAIContext) -> NodeStatus:
        """
        Attempt to flee from combat.
        
        Args:
            ctx: Current AI context.
            
        Returns:
            NodeStatus.SUCCESS if fleeing, RUNNING if still in combat.
        """
        ctx.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {
                "action": "enemy_flee",
                "enemy": ctx.enemy.name,
                "room_id": ctx.room.room_id
            }
        ))
        return NodeStatus.SUCCESS
    
    def _call_for_help(self, ctx: EnemyAIContext) -> NodeStatus:
        """
        Call for help from nearby allies.
        
        Args:
            ctx: Current AI context.
            
        Returns:
            NodeStatus.SUCCESS if help called.
        """
        ctx.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {
                "action": "call_for_help",
                "enemy": ctx.enemy.name,
                "room_id": ctx.room.room_id,
                "allies_nearby": len(ctx.nearby_allies)
            }
        ))
        
        for ally in ctx.nearby_allies:
            if ally.is_alive and ally != ctx.enemy:
                ally.attack = int(ally.attack * 1.1)
        
        return NodeStatus.SUCCESS
    
    def _coordinate_attack(self, ctx: EnemyAIContext) -> NodeStatus:
        """
        Coordinate an attack with nearby allies for bonus damage.
        
        Args:
            ctx: Current AI context.
            
        Returns:
            NodeStatus.SUCCESS if coordinated attack executed.
        """
        if not self._can_attack(ctx):
            return NodeStatus.FAILURE
        
        bonus_damage = len([a for a in ctx.nearby_allies if a.is_alive]) * 2
        total_damage = ctx.enemy.attack + bonus_damage
        actual_damage = ctx.hero.take_damage(total_damage)
        
        ctx.event_bus.publish(Event(
            EventType.ENEMY_ATTACKED,
            {
                "enemy": ctx.enemy.name,
                "target": ctx.hero.name,
                "damage": actual_damage,
                "coordinated": True,
                "allies_count": len(ctx.nearby_allies)
            }
        ))
        
        return NodeStatus.SUCCESS
    
    def _hero_in_room(self, ctx: EnemyAIContext) -> bool:
        """
        Check if the hero is in the same room as the enemy.
        
        Args:
            ctx: Current AI context.
            
        Returns:
            True if hero is in the room.
        """
        return ctx.hero.current_room_id == ctx.room.room_id
    
    def _use_terrain(self, ctx: EnemyAIContext) -> NodeStatus:
        """
        Use terrain for tactical advantage.
        
        Args:
            ctx: Current AI context.
            
        Returns:
            NodeStatus.SUCCESS if terrain used.
        """
        ctx.enemy.defense += 2
        
        ctx.event_bus.publish(Event(
            EventType.PLAYER_ACTION,
            {
                "action": "use_terrain",
                "enemy": ctx.enemy.name,
                "defense_bonus": 2
            }
        ))
        
        return NodeStatus.SUCCESS
    
    def _enrage(self, ctx: EnemyAIContext) -> NodeStatus:
        """
        Enter enraged state at low health (boss behavior).
        
        Args:
            ctx: Current AI context.
            
        Returns:
            NodeStatus.SUCCESS if enraged.
        """
        if self._enraged:
            return NodeStatus.SUCCESS
        
        self._enraged = True
        ctx.enemy.attack = int(ctx.enemy.attack * 1.5)
        
        ctx.event_bus.publish(Event(
            EventType.ENEMY_MUTATED,
            {
                "enemy": ctx.enemy.name,
                "mutation": "enraged",
                "attack_boost": 1.5
            }
        ))
        
        return NodeStatus.SUCCESS
    
    def _summon_minions(self, ctx: EnemyAIContext) -> NodeStatus:
        """
        Summon minion enemies (boss behavior).
        
        Args:
            ctx: Current AI context.
            
        Returns:
            NodeStatus.SUCCESS if minions summoned.
        """
        from models import EnemyType
        
        minion_count = random.randint(1, 2)
        
        for i in range(minion_count):
            minion = Enemy(
                EnemyType.SKELETON,
                f"Summoned Minion {i+1}",
                health=20,
                attack=5,
                defense=1
            )
            ctx.room.add_enemy(minion)
            ctx.nearby_allies.append(minion)
            
            ctx.event_bus.publish(Event(
                EventType.ENEMY_SPAWNED,
                {
                    "enemy": minion.name,
                    "summoned_by": ctx.enemy.name,
                    "room_id": ctx.room.room_id
                }
            ))
        
        return NodeStatus.SUCCESS
    
    def _boss_attack_pattern(self, ctx: EnemyAIContext) -> NodeStatus:
        """
        Execute boss attack patterns that cycle through different attacks.
        
        Args:
            ctx: Current AI context.
            
        Returns:
            NodeStatus.SUCCESS if attack executed.
        """
        if not self._can_attack(ctx):
            return NodeStatus.FAILURE
        
        patterns = [
            ("Normal Attack", 1.0),
            ("Heavy Strike", 1.5),
            ("Sweeping Attack", 0.8),
            ("Devastating Blow", 2.0)
        ]
        
        pattern_name, multiplier = patterns[self._attack_pattern % len(patterns)]
        self._attack_pattern += 1
        
        if self._enraged:
            multiplier *= 1.3
        
        damage = int(ctx.enemy.attack * multiplier)
        actual_damage = ctx.hero.take_damage(damage)
        
        ctx.event_bus.publish(Event(
            EventType.ENEMY_ATTACKED,
            {
                "enemy": ctx.enemy.name,
                "target": ctx.hero.name,
                "damage": actual_damage,
                "pattern": pattern_name,
                "enraged": self._enraged
            }
        ))
        
        if not ctx.hero.is_alive:
            ctx.event_bus.publish(Event(
                EventType.HERO_DIED,
                {"killed_by": ctx.enemy.name, "attack_pattern": pattern_name}
            ))
        
        return NodeStatus.SUCCESS
