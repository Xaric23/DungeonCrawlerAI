"""
Mod Loader for DungeonCrawlerAI.
Loads custom content (enemies, items, traps, curse powers) from JSON mod files.
"""
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path


class ModRegistry:
    """Registry for all loaded mod content"""
    
    def __init__(self):
        self.enemies: Dict[str, Dict[str, Any]] = {}
        self.items: Dict[str, Dict[str, Any]] = {}
        self.traps: Dict[str, Dict[str, Any]] = {}
        self.curse_powers: Dict[str, Dict[str, Any]] = {}
        self.loaded_mods: List[str] = []
    
    def register_enemy(self, enemy_id: str, enemy_data: Dict[str, Any]):
        """Register a custom enemy type"""
        self.enemies[enemy_id] = enemy_data
    
    def register_item(self, item_id: str, item_data: Dict[str, Any]):
        """Register a custom item type"""
        self.items[item_id] = item_data
    
    def register_trap(self, trap_id: str, trap_data: Dict[str, Any]):
        """Register a custom trap type"""
        self.traps[trap_id] = trap_data
    
    def register_curse_power(self, power_id: str, power_data: Dict[str, Any]):
        """Register a custom curse power"""
        self.curse_powers[power_id] = power_data
    
    def get_enemy(self, enemy_id: str) -> Optional[Dict[str, Any]]:
        """Get enemy data by ID"""
        return self.enemies.get(enemy_id)
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item data by ID"""
        return self.items.get(item_id)
    
    def get_trap(self, trap_id: str) -> Optional[Dict[str, Any]]:
        """Get trap data by ID"""
        return self.traps.get(trap_id)
    
    def get_curse_power(self, power_id: str) -> Optional[Dict[str, Any]]:
        """Get curse power data by ID"""
        return self.curse_powers.get(power_id)
    
    def get_all_enemy_ids(self) -> List[str]:
        """Get list of all registered enemy IDs"""
        return list(self.enemies.keys())
    
    def get_all_item_ids(self) -> List[str]:
        """Get list of all registered item IDs"""
        return list(self.items.keys())
    
    def get_all_trap_ids(self) -> List[str]:
        """Get list of all registered trap IDs"""
        return list(self.traps.keys())
    
    def get_all_curse_power_ids(self) -> List[str]:
        """Get list of all registered curse power IDs"""
        return list(self.curse_powers.keys())


# Global mod registry instance
_mod_registry = ModRegistry()


def get_mod_registry() -> ModRegistry:
    """Get the global mod registry instance"""
    return _mod_registry


class ModLoader:
    """Loads mods from the mods directory"""
    
    def __init__(self, mods_dir: str = "mods"):
        self.mods_dir = Path(mods_dir)
        self.registry = get_mod_registry()
    
    def load_all_mods(self, verbose: bool = False) -> int:
        """
        Load all mods from the mods directory.
        
        Args:
            verbose: Print loading information
            
        Returns:
            Number of mods loaded
        """
        if not self.mods_dir.exists():
            if verbose:
                print(f"Mods directory '{self.mods_dir}' not found. No mods loaded.")
            return 0
        
        mods_loaded = 0
        
        # Find all mod.json files
        for mod_file in self.mods_dir.rglob("mod.json"):
            try:
                if self.load_mod(mod_file, verbose):
                    mods_loaded += 1
            except Exception as e:
                if verbose:
                    print(f"Error loading mod from {mod_file}: {e}")
        
        if verbose and mods_loaded > 0:
            print(f"Loaded {mods_loaded} mod(s)")
        
        return mods_loaded
    
    def load_mod(self, mod_file: Path, verbose: bool = False) -> bool:
        """
        Load a single mod from a mod.json file.
        
        Args:
            mod_file: Path to mod.json file
            verbose: Print loading information
            
        Returns:
            True if mod loaded successfully, False otherwise
        """
        try:
            with open(mod_file, 'r') as f:
                mod_data = json.load(f)
            
            mod_name = mod_data.get("name", "Unknown Mod")
            mod_version = mod_data.get("version", "1.0")
            
            if verbose:
                print(f"Loading mod: {mod_name} v{mod_version}")
            
            # Load enemies
            if "enemies" in mod_data:
                for enemy in mod_data["enemies"]:
                    enemy_id = enemy.get("id")
                    if enemy_id:
                        self.registry.register_enemy(enemy_id, enemy)
                        if verbose:
                            print(f"  - Registered enemy: {enemy_id}")
            
            # Load items
            if "items" in mod_data:
                for item in mod_data["items"]:
                    item_id = item.get("id")
                    if item_id:
                        self.registry.register_item(item_id, item)
                        if verbose:
                            print(f"  - Registered item: {item_id}")
            
            # Load traps
            if "traps" in mod_data:
                for trap in mod_data["traps"]:
                    trap_id = trap.get("id")
                    if trap_id:
                        self.registry.register_trap(trap_id, trap)
                        if verbose:
                            print(f"  - Registered trap: {trap_id}")
            
            # Load curse powers
            if "curse_powers" in mod_data:
                for power in mod_data["curse_powers"]:
                    power_id = power.get("id")
                    if power_id:
                        self.registry.register_curse_power(power_id, power)
                        if verbose:
                            print(f"  - Registered curse power: {power_id}")
            
            self.registry.loaded_mods.append(mod_name)
            return True
            
        except Exception as e:
            if verbose:
                print(f"Error loading mod from {mod_file}: {e}")
            return False
    
    def get_loaded_mods(self) -> List[str]:
        """Get list of loaded mod names"""
        return self.registry.loaded_mods.copy()


def load_mods(mods_dir: str = "mods", verbose: bool = False) -> ModRegistry:
    """
    Convenience function to load all mods and return the registry.
    
    Args:
        mods_dir: Directory containing mods
        verbose: Print loading information
        
    Returns:
        The mod registry with all loaded content
    """
    loader = ModLoader(mods_dir)
    loader.load_all_mods(verbose)
    return loader.registry
