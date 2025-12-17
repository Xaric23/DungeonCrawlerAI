#!/usr/bin/env python3
"""
Tests for the modding system.
"""
import unittest
import os
import json
import tempfile
import shutil
from pathlib import Path
from mod_loader import ModLoader, ModRegistry, get_mod_registry, load_mods
from dungeon import create_custom_enemy, create_custom_item, create_custom_trap, Dungeon
from game import DungeonCrawlerGame


class TestModLoader(unittest.TestCase):
    """Test mod loading functionality"""
    
    def test_mod_registry_creation(self):
        """Test creating a mod registry"""
        registry = ModRegistry()
        self.assertEqual(len(registry.enemies), 0)
        self.assertEqual(len(registry.items), 0)
        self.assertEqual(len(registry.traps), 0)
    
    def test_register_enemy(self):
        """Test registering a custom enemy"""
        registry = ModRegistry()
        enemy_data = {
            "id": "test_enemy",
            "name": "Test Enemy",
            "health": 50,
            "attack": 10,
            "defense": 5
        }
        registry.register_enemy("test_enemy", enemy_data)
        self.assertIn("test_enemy", registry.enemies)
        self.assertEqual(registry.get_enemy("test_enemy")["name"], "Test Enemy")
    
    def test_register_item(self):
        """Test registering a custom item"""
        registry = ModRegistry()
        item_data = {
            "id": "test_item",
            "name": "Test Item",
            "type": "weapon",
            "value": 20
        }
        registry.register_item("test_item", item_data)
        self.assertIn("test_item", registry.items)
    
    def test_register_trap(self):
        """Test registering a custom trap"""
        registry = ModRegistry()
        trap_data = {
            "id": "test_trap",
            "name": "Test Trap",
            "type": "fire",
            "damage": 25
        }
        registry.register_trap("test_trap", trap_data)
        self.assertIn("test_trap", registry.traps)
    
    def test_load_example_mod(self):
        """Test loading the example mod"""
        if Path("mods/example_mod/mod.json").exists():
            loader = ModLoader("mods")
            mods_loaded = loader.load_all_mods(verbose=False)
            self.assertGreater(mods_loaded, 0)
            
            registry = loader.registry
            self.assertIn("Example Mod", registry.loaded_mods)
            self.assertGreater(len(registry.enemies), 0)
            self.assertGreater(len(registry.items), 0)


class TestCustomContent(unittest.TestCase):
    """Test creating custom game content from mod data"""
    
    def test_create_custom_enemy(self):
        """Test creating an enemy from mod data"""
        enemy_data = {
            "id": "vampire",
            "name": "Vampire",
            "type": "vampire",
            "health": 70,
            "attack": 18,
            "defense": 6
        }
        enemy = create_custom_enemy(enemy_data)
        self.assertEqual(enemy.name, "Vampire")
        self.assertEqual(enemy.health, 70)
        self.assertEqual(enemy.attack, 18)
        self.assertEqual(enemy.defense, 6)
    
    def test_create_custom_item(self):
        """Test creating an item from mod data"""
        item_data = {
            "id": "super_sword",
            "name": "Super Sword",
            "type": "weapon",
            "value": 30
        }
        item = create_custom_item(item_data)
        self.assertEqual(item.name, "Super Sword")
        self.assertEqual(item.value, 30)
    
    def test_create_custom_trap(self):
        """Test creating a trap from mod data"""
        trap_data = {
            "id": "lightning",
            "name": "Lightning Trap",
            "type": "lightning",
            "damage": 35
        }
        trap = create_custom_trap(trap_data)
        self.assertEqual(trap.damage, 35)


class TestModIntegration(unittest.TestCase):
    """Test mod integration with the game"""
    
    def test_game_with_mods_enabled(self):
        """Test creating a game with mods enabled"""
        game = DungeonCrawlerGame(num_rooms=5, enable_player=False, use_mods=True)
        self.assertIsNotNone(game.dungeon)
        self.assertEqual(game.use_mods, True)
    
    def test_game_with_mods_disabled(self):
        """Test creating a game with mods disabled"""
        game = DungeonCrawlerGame(num_rooms=5, enable_player=False, use_mods=False)
        self.assertIsNotNone(game.dungeon)
        self.assertEqual(game.use_mods, False)
    
    def test_dungeon_with_mods(self):
        """Test dungeon creation with mods"""
        dungeon = Dungeon(num_rooms=5, use_mods=True)
        self.assertEqual(dungeon.num_rooms, 5)
        self.assertTrue(dungeon.use_mods)


if __name__ == "__main__":
    unittest.main()
