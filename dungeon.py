"""
Dungeon generation and management.
Creates interconnected rooms with items, enemies, and traps.
"""
import random
from typing import List, Optional, Dict
from models import Room, RoomType, Item, ItemType, Enemy, EnemyType, Trap, TrapType


def create_custom_enemy(enemy_data: Dict) -> Enemy:
    """Create an enemy from mod data"""
    from models import Enemy, EnemyType
    
    # Try to use existing EnemyType or create a placeholder
    enemy_type_str = enemy_data.get("type", "custom")
    try:
        enemy_type = EnemyType(enemy_type_str)
    except ValueError:
        # Use GOBLIN as a placeholder for custom types
        enemy_type = EnemyType.GOBLIN
    
    return Enemy(
        enemy_type,
        enemy_data.get("name", "Unknown Enemy"),
        enemy_data.get("health", 50),
        enemy_data.get("attack", 10),
        enemy_data.get("defense", 5)
    )


def create_custom_item(item_data: Dict) -> Item:
    """Create an item from mod data"""
    from models import Item, ItemType
    
    # Map type string to ItemType
    type_str = item_data.get("type", "treasure")
    try:
        item_type = ItemType(type_str)
    except ValueError:
        item_type = ItemType.TREASURE
    
    return Item(
        item_type,
        item_data.get("name", "Unknown Item"),
        item_data.get("value", 10)
    )


def create_custom_trap(trap_data: Dict) -> Trap:
    """Create a trap from mod data"""
    from models import Trap, TrapType
    
    # Try to use existing TrapType or create a placeholder
    trap_type_str = trap_data.get("type", "spike")
    try:
        trap_type = TrapType(trap_type_str)
    except ValueError:
        # Use SPIKE as a placeholder for custom types
        trap_type = TrapType.SPIKE
    
    return Trap(
        trap_type,
        trap_data.get("damage", 15)
    )


class Dungeon:
    """Represents the dungeon structure"""
    
    def __init__(self, num_rooms: int = 10, use_mods: bool = True):
        if num_rooms < 3:
            raise ValueError(f"Dungeon requires at least 3 rooms (entrance, treasure, boss), got {num_rooms}")
        self.rooms: Dict[int, Room] = {}
        self.num_rooms = num_rooms
        self.entrance_room_id = 0
        self.use_mods = use_mods
        self._generate_dungeon()
    
    def _generate_dungeon(self):
        """Generate the dungeon structure"""
        # Create entrance room
        entrance = Room(0, RoomType.ENTRANCE)
        self.rooms[0] = entrance
        
        # Create normal rooms
        for i in range(1, self.num_rooms - 2):
            room = Room(i, RoomType.NORMAL)
            self._populate_room(room)
            self.rooms[i] = room
        
        # Create treasure room
        treasure_room_id = self.num_rooms - 2
        treasure_room = Room(treasure_room_id, RoomType.TREASURE)
        self._populate_treasure_room(treasure_room)
        self.rooms[treasure_room_id] = treasure_room
        
        # Create boss room
        boss_room_id = self.num_rooms - 1
        boss_room = Room(boss_room_id, RoomType.BOSS)
        self._populate_boss_room(boss_room)
        self.rooms[boss_room_id] = boss_room
        
        # Connect rooms in a somewhat linear path with some branches
        self._connect_rooms()
    
    def _populate_room(self, room: Room):
        """Populate a normal room with enemies, items, and traps"""
        # Add enemies (50% chance)
        if random.random() < 0.5:
            num_enemies = random.randint(1, 2)
            for _ in range(num_enemies):
                enemy = self._create_random_enemy()
                room.add_enemy(enemy)
        
        # Add items (40% chance)
        if random.random() < 0.4:
            item = self._create_random_item()
            room.add_item(item)
        
        # Add traps (30% chance)
        if random.random() < 0.3:
            trap = self._create_random_trap()
            room.add_trap(trap)
    
    def _populate_treasure_room(self, room: Room):
        """Populate treasure room with valuable items"""
        # Add multiple treasures
        for _ in range(random.randint(2, 4)):
            treasure = Item(ItemType.TREASURE, "Gold Coins", random.randint(50, 150))
            room.add_item(treasure)
        
        # Add good equipment
        weapon = Item(ItemType.WEAPON, "Enchanted Sword", random.randint(10, 20))
        armor = Item(ItemType.ARMOR, "Sturdy Armor", random.randint(5, 10))
        room.add_item(weapon)
        room.add_item(armor)
        
        # But also some enemies guarding it
        for _ in range(2):
            enemy = self._create_random_enemy(strong=True)
            room.add_enemy(enemy)
    
    def _populate_boss_room(self, room: Room):
        """Populate boss room with a powerful enemy"""
        boss = Enemy(EnemyType.DRAGON, "Dragon Boss", 150, 25, 10)
        room.add_enemy(boss)
        
        # Boss room treasure
        for _ in range(3):
            treasure = Item(ItemType.TREASURE, "Dragon Hoard", random.randint(100, 200))
            room.add_item(treasure)
    
    def _create_enemy(self, enemy_type: EnemyType) -> Enemy:
        """Create an enemy of the specified type"""
        if enemy_type == EnemyType.GOBLIN:
            return Enemy(EnemyType.GOBLIN, "Goblin", 30, 8, 2)
        elif enemy_type == EnemyType.ORC:
            return Enemy(EnemyType.ORC, "Orc", 50, 12, 5)
        elif enemy_type == EnemyType.SKELETON:
            return Enemy(EnemyType.SKELETON, "Skeleton", 40, 10, 3)
        else:
            return Enemy(EnemyType.DRAGON, "Dragon", 150, 25, 10)
    
    def _create_random_enemy(self, strong: bool = False) -> Enemy:
        """Create a random enemy, optionally from mod content"""
        if self.use_mods:
            try:
                from mod_loader import get_mod_registry
                registry = get_mod_registry()
                custom_enemies = registry.get_all_enemy_ids()
                
                # Mix vanilla and custom enemies (30% chance for custom if available)
                if custom_enemies and random.random() < 0.3:
                    enemy_id = random.choice(custom_enemies)
                    enemy_data = registry.get_enemy(enemy_id)
                    if enemy_data:
                        return create_custom_enemy(enemy_data)
            except Exception:
                pass  # Fall back to vanilla enemies
        
        # Default vanilla enemies
        if strong:
            enemy_type = random.choice([EnemyType.ORC, EnemyType.SKELETON])
        else:
            enemy_type = random.choice([EnemyType.GOBLIN, EnemyType.ORC, EnemyType.SKELETON])
        return self._create_enemy(enemy_type)
    
    def _create_random_item(self) -> Item:
        """Create a random item, optionally from mod content"""
        if self.use_mods:
            try:
                from mod_loader import get_mod_registry
                registry = get_mod_registry()
                custom_items = registry.get_all_item_ids()
                
                # Mix vanilla and custom items (30% chance for custom if available)
                if custom_items and random.random() < 0.3:
                    item_id = random.choice(custom_items)
                    item_data = registry.get_item(item_id)
                    if item_data:
                        return create_custom_item(item_data)
            except Exception:
                pass  # Fall back to vanilla items
        
        # Default vanilla items
        item_choice = random.choice([ItemType.HEALTH_POTION, ItemType.WEAPON, ItemType.ARMOR, ItemType.TREASURE])
        
        if item_choice == ItemType.HEALTH_POTION:
            return Item(ItemType.HEALTH_POTION, "Health Potion", random.randint(20, 40))
        elif item_choice == ItemType.WEAPON:
            return Item(ItemType.WEAPON, "Sword", random.randint(3, 8))
        elif item_choice == ItemType.ARMOR:
            return Item(ItemType.ARMOR, "Shield", random.randint(2, 5))
        else:
            return Item(ItemType.TREASURE, "Coins", random.randint(10, 50))
    
    def _create_random_trap(self) -> Trap:
        """Create a random trap, optionally from mod content"""
        if self.use_mods:
            try:
                from mod_loader import get_mod_registry
                registry = get_mod_registry()
                custom_traps = registry.get_all_trap_ids()
                
                # Mix vanilla and custom traps (30% chance for custom if available)
                if custom_traps and random.random() < 0.3:
                    trap_id = random.choice(custom_traps)
                    trap_data = registry.get_trap(trap_id)
                    if trap_data:
                        return create_custom_trap(trap_data)
            except Exception:
                pass  # Fall back to vanilla traps
        
        # Default vanilla traps
        trap_type = random.choice(list(TrapType))
        return Trap(trap_type, random.randint(5, 15))
    
    def _connect_rooms(self):
        """Connect rooms to create a dungeon layout"""
        # Create a main path from entrance to boss
        for i in range(self.num_rooms - 1):
            self.rooms[i].connected_rooms.append(i + 1)
            self.rooms[i + 1].connected_rooms.append(i)
        
        # Add some additional connections for branches
        for i in range(1, self.num_rooms - 2):
            if random.random() < 0.3 and i + 2 < self.num_rooms - 1:
                if i + 2 not in self.rooms[i].connected_rooms:
                    self.rooms[i].connected_rooms.append(i + 2)
                    self.rooms[i + 2].connected_rooms.append(i)
    
    def get_room(self, room_id: int) -> Optional[Room]:
        """Get a room by ID"""
        return self.rooms.get(room_id)
    
    def get_connected_rooms(self, room_id: int) -> List[int]:
        """Get list of connected room IDs"""
        room = self.get_room(room_id)
        return room.connected_rooms if room else []
    
    def __repr__(self):
        return f"Dungeon(rooms={self.num_rooms}, entrance={self.entrance_room_id})"
