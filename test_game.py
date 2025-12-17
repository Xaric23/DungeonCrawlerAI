#!/usr/bin/env python3
"""
Unit tests for DungeonCrawlerAI.
Tests core functionality of all game components.
"""
import unittest
from models import (
    Hero, Enemy, EnemyType, Item, ItemType, ItemQuality,
    Room, RoomType, Trap, TrapType
)
from dungeon import Dungeon
from events import EventBus, Event, EventType
from behavior_tree import (
    NodeStatus, SequenceNode, SelectorNode,
    ConditionNode, ActionNode, InverterNode
)
from hero_ai import HeroAI
from player_curse import PlayerCurse
from game import DungeonCrawlerGame


class TestModels(unittest.TestCase):
    """Test game models"""
    
    def test_hero_creation(self):
        """Test hero initialization"""
        hero = Hero("Test Hero")
        self.assertEqual(hero.name, "Test Hero")
        self.assertEqual(hero.health, 100)
        self.assertEqual(hero.max_health, 100)
        self.assertTrue(hero.is_alive)
        self.assertEqual(hero.suspicion_level, 0)
    
    def test_hero_take_damage(self):
        """Test hero taking damage"""
        hero = Hero()
        initial_health = hero.health
        damage = hero.take_damage(30)
        self.assertLess(hero.health, initial_health)
        self.assertGreaterEqual(damage, 1)
        self.assertTrue(hero.is_alive)
    
    def test_hero_death(self):
        """Test hero death"""
        hero = Hero()
        hero.take_damage(200)
        self.assertFalse(hero.is_alive)
        self.assertEqual(hero.health, 0)
    
    def test_hero_suspicion(self):
        """Test hero suspicion system"""
        hero = Hero()
        self.assertFalse(hero.is_suspicious())
        hero.increase_suspicion(60)
        self.assertTrue(hero.is_suspicious())
    
    def test_item_corruption(self):
        """Test item corruption"""
        item = Item(ItemType.HEALTH_POTION, "Potion", 30)
        self.assertEqual(item.quality, ItemQuality.NORMAL)
        
        item.corrupt()
        self.assertEqual(item.quality, ItemQuality.CORRUPTED)
        self.assertEqual(item.value, 15)
        
        item.corrupt()
        self.assertEqual(item.quality, ItemQuality.CURSED)
        self.assertLess(item.value, 0)
    
    def test_enemy_mutation(self):
        """Test enemy mutation"""
        enemy = Enemy(EnemyType.GOBLIN, "Goblin", 30, 8, 2)
        original_attack = enemy.attack
        
        self.assertFalse(enemy.is_mutated)
        enemy.mutate()
        self.assertTrue(enemy.is_mutated)
        self.assertGreater(enemy.attack, original_attack)
    
    def test_enemy_combat(self):
        """Test enemy taking damage"""
        enemy = Enemy(EnemyType.GOBLIN, "Goblin", 30, 8, 2)
        enemy.take_damage(40)
        self.assertFalse(enemy.is_alive)
    
    def test_trap_trigger(self):
        """Test trap triggering"""
        trap = Trap(TrapType.SPIKE, 15)
        self.assertFalse(trap.triggered)
        
        damage = trap.trigger()
        self.assertEqual(damage, 15)
        self.assertTrue(trap.triggered)
        
        # Second trigger should do nothing
        damage2 = trap.trigger()
        self.assertEqual(damage2, 0)
    
    def test_room_alteration(self):
        """Test room alteration"""
        room = Room(1, RoomType.NORMAL)
        trap_count = len(room.traps)
        
        self.assertFalse(room.altered)
        room.alter_room()
        self.assertTrue(room.altered)
        self.assertGreater(len(room.traps), trap_count)


class TestBehaviorTree(unittest.TestCase):
    """Test behavior tree implementation"""
    
    def test_condition_node(self):
        """Test condition node"""
        node = ConditionNode("Test", lambda ctx: ctx > 5)
        self.assertEqual(node.tick(10), NodeStatus.SUCCESS)
        self.assertEqual(node.tick(3), NodeStatus.FAILURE)
    
    def test_action_node(self):
        """Test action node"""
        result = {"value": 0}
        
        def action(ctx):
            result["value"] = 10
            return NodeStatus.SUCCESS
        
        node = ActionNode("Test", action)
        status = node.tick(None)
        self.assertEqual(status, NodeStatus.SUCCESS)
        self.assertEqual(result["value"], 10)
    
    def test_sequence_node(self):
        """Test sequence node - succeeds if all children succeed"""
        seq = SequenceNode("Test Sequence")
        seq.add_child(ConditionNode("C1", lambda ctx: True))
        seq.add_child(ConditionNode("C2", lambda ctx: True))
        
        self.assertEqual(seq.tick(None), NodeStatus.SUCCESS)
        
        # Add a failing node
        seq.add_child(ConditionNode("C3", lambda ctx: False))
        self.assertEqual(seq.tick(None), NodeStatus.FAILURE)
    
    def test_selector_node(self):
        """Test selector node - succeeds if any child succeeds"""
        sel = SelectorNode("Test Selector")
        sel.add_child(ConditionNode("C1", lambda ctx: False))
        sel.add_child(ConditionNode("C2", lambda ctx: True))
        sel.add_child(ConditionNode("C3", lambda ctx: False))
        
        self.assertEqual(sel.tick(None), NodeStatus.SUCCESS)
        
        # All failing
        sel2 = SelectorNode("Test Selector 2")
        sel2.add_child(ConditionNode("C1", lambda ctx: False))
        sel2.add_child(ConditionNode("C2", lambda ctx: False))
        
        self.assertEqual(sel2.tick(None), NodeStatus.FAILURE)
    
    def test_inverter_node(self):
        """Test inverter decorator"""
        success_node = ConditionNode("Test", lambda ctx: True)
        inverter = InverterNode("Invert", success_node)
        
        self.assertEqual(inverter.tick(None), NodeStatus.FAILURE)


class TestEventSystem(unittest.TestCase):
    """Test event system"""
    
    def test_event_creation(self):
        """Test event creation"""
        event = Event(EventType.HERO_MOVED, {"from": 0, "to": 1})
        self.assertEqual(event.event_type, EventType.HERO_MOVED)
        self.assertEqual(event.data["from"], 0)
    
    def test_event_bus_subscribe(self):
        """Test subscribing to events"""
        bus = EventBus()
        received = []
        
        def handler(event):
            received.append(event)
        
        bus.subscribe(EventType.HERO_MOVED, handler)
        event = Event(EventType.HERO_MOVED, {"test": "data"})
        bus.publish(event)
        
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0], event)
    
    def test_event_bus_history(self):
        """Test event history tracking"""
        bus = EventBus()
        
        event1 = Event(EventType.HERO_MOVED, {})
        event2 = Event(EventType.HERO_ATTACKED, {})
        
        bus.publish(event1)
        bus.publish(event2)
        
        history = bus.get_history()
        self.assertEqual(len(history), 2)
        
        move_events = bus.get_history(EventType.HERO_MOVED)
        self.assertEqual(len(move_events), 1)


class TestDungeon(unittest.TestCase):
    """Test dungeon generation"""
    
    def test_dungeon_creation(self):
        """Test dungeon initialization"""
        dungeon = Dungeon(10)
        self.assertEqual(dungeon.num_rooms, 10)
        self.assertEqual(len(dungeon.rooms), 10)
    
    def test_room_connections(self):
        """Test room connections"""
        dungeon = Dungeon(5)
        entrance = dungeon.get_room(0)
        
        self.assertIsNotNone(entrance)
        self.assertEqual(entrance.room_type, RoomType.ENTRANCE)
        self.assertGreater(len(entrance.connected_rooms), 0)
    
    def test_special_rooms(self):
        """Test special room generation"""
        dungeon = Dungeon(10)
        
        # Check for boss room
        boss_room = dungeon.get_room(9)
        self.assertEqual(boss_room.room_type, RoomType.BOSS)
        self.assertGreater(len(boss_room.enemies), 0)
        
        # Check for treasure room
        treasure_room = dungeon.get_room(8)
        self.assertEqual(treasure_room.room_type, RoomType.TREASURE)
        self.assertGreater(len(treasure_room.items), 0)


class TestPlayerCurse(unittest.TestCase):
    """Test player curse system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.event_bus = EventBus()
        self.dungeon = Dungeon(5)
        self.player_curse = PlayerCurse(self.dungeon, self.event_bus)
    
    def test_curse_energy(self):
        """Test curse energy system"""
        initial_energy = self.player_curse.curse_energy
        self.assertEqual(initial_energy, 100)
        
        self.player_curse.regenerate_energy(10)
        self.assertEqual(self.player_curse.curse_energy, 100)  # Already at max
    
    def test_alter_room(self):
        """Test room alteration"""
        room = self.dungeon.get_room(1)
        self.assertFalse(room.altered)
        
        success = self.player_curse.alter_room(1)
        self.assertTrue(success)
        self.assertTrue(room.altered)
        
        # Can't alter twice
        success2 = self.player_curse.alter_room(1)
        self.assertFalse(success2)
    
    def test_corrupt_loot(self):
        """Test loot corruption"""
        room = self.dungeon.get_room(1)
        room.items.clear()  # Clear existing items
        
        # Add an item to corrupt
        item = Item(ItemType.HEALTH_POTION, "Potion", 30)
        room.add_item(item)
        
        self.assertEqual(item.quality, ItemQuality.NORMAL)
        success = self.player_curse.corrupt_loot(1, 0)
        self.assertTrue(success)
        self.assertEqual(item.quality, ItemQuality.CORRUPTED)
    
    def test_mutate_enemy(self):
        """Test enemy mutation"""
        room = self.dungeon.get_room(1)
        room.enemies.clear()  # Clear existing enemies
        
        # Add an enemy to mutate
        enemy = Enemy(EnemyType.GOBLIN, "Goblin", 30, 8, 2)
        room.add_enemy(enemy)
        
        self.assertFalse(enemy.is_mutated)
        success = self.player_curse.mutate_enemy(1, 0)
        self.assertTrue(success)
        self.assertTrue(enemy.is_mutated)


class TestHeroAI(unittest.TestCase):
    """Test hero AI behavior"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.event_bus = EventBus()
        self.dungeon = Dungeon(5)
        self.hero = Hero("Test Hero")
        self.hero_ai = HeroAI(self.hero, self.dungeon, self.event_bus)
    
    def test_hero_enters_dungeon(self):
        """Test hero entering dungeon"""
        self.assertIsNone(self.hero.current_room_id)
        
        # First tick should enter dungeon
        status = self.hero_ai.tick()
        self.assertIsNotNone(self.hero.current_room_id)
        self.assertEqual(status, NodeStatus.SUCCESS)
    
    def test_hero_loots_item(self):
        """Test hero looting items"""
        # Place hero in a room with an item
        self.hero.current_room_id = 1
        self.hero.visited_rooms.append(1)
        
        room = self.dungeon.get_room(1)
        room.items.clear()
        room.enemies.clear()  # Clear enemies so hero will loot
        item = Item(ItemType.WEAPON, "Sword", 5)
        room.add_item(item)
        
        initial_attack = self.hero.attack
        initial_items = len(room.items)
        
        # Hero should loot the item
        status = self.hero_ai.tick()
        self.assertEqual(status, NodeStatus.SUCCESS)
        self.assertLess(len(room.items), initial_items)  # Item taken
        self.assertGreater(self.hero.attack, initial_attack)  # Weapon equipped
    
    def test_hero_fights_enemy(self):
        """Test hero combat"""
        self.hero.current_room_id = 1
        self.hero.visited_rooms.append(1)
        
        room = self.dungeon.get_room(1)
        room.enemies.clear()
        enemy = Enemy(EnemyType.GOBLIN, "Goblin", 10, 5, 1)
        room.add_enemy(enemy)
        
        # Hero should fight
        status = self.hero_ai.tick()
        self.assertEqual(status, NodeStatus.SUCCESS)
        self.assertLess(enemy.health, 10)  # Enemy took damage


class TestGame(unittest.TestCase):
    """Test game integration"""
    
    def test_game_creation(self):
        """Test game initialization"""
        game = DungeonCrawlerGame(num_rooms=5, enable_player=False)
        self.assertIsNotNone(game.hero)
        self.assertIsNotNone(game.dungeon)
        self.assertIsNotNone(game.hero_ai)
        self.assertIsNone(game.player_curse)
    
    def test_game_with_player(self):
        """Test game with player curse enabled"""
        game = DungeonCrawlerGame(num_rooms=5, enable_player=True)
        self.assertIsNotNone(game.player_curse)
    
    def test_game_turn(self):
        """Test running a single turn"""
        game = DungeonCrawlerGame(num_rooms=5, enable_player=False)
        
        initial_turn = game.state.turn
        result = game.run_turn()
        
        self.assertTrue(result)  # Game continues
        self.assertEqual(game.state.turn, initial_turn + 1)
    
    def test_game_simulation(self):
        """Test full game simulation"""
        game = DungeonCrawlerGame(num_rooms=5, enable_player=False)
        results = game.run_simulation(max_turns=50, verbose=False)
        
        self.assertIn("turns", results)
        self.assertIn("victory", results)
        self.assertIn("hero_alive", results)
        self.assertLessEqual(results["turns"], 50)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestModels))
    suite.addTests(loader.loadTestsFromTestCase(TestBehaviorTree))
    suite.addTests(loader.loadTestsFromTestCase(TestEventSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestDungeon))
    suite.addTests(loader.loadTestsFromTestCase(TestPlayerCurse))
    suite.addTests(loader.loadTestsFromTestCase(TestHeroAI))
    suite.addTests(loader.loadTestsFromTestCase(TestGame))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
