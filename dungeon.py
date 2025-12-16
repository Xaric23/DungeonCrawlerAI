"""
Dungeon generation and management.
Creates interconnected rooms with items, enemies, and traps.
"""
import random
from typing import List, Optional, Dict
from models import Room, RoomType, Item, ItemType, ItemQuality, Enemy, EnemyType, Trap, TrapType


class Dungeon:
    """Represents the dungeon structure"""
    
    def __init__(self, num_rooms: int = 10):
        self.rooms: Dict[int, Room] = {}
        self.num_rooms = num_rooms
        self.entrance_room_id = 0
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
                enemy_type = random.choice([EnemyType.GOBLIN, EnemyType.ORC, EnemyType.SKELETON])
                enemy = self._create_enemy(enemy_type)
                room.add_enemy(enemy)
        
        # Add items (40% chance)
        if random.random() < 0.4:
            item = self._create_random_item()
            room.add_item(item)
        
        # Add traps (30% chance)
        if random.random() < 0.3:
            trap_type = random.choice(list(TrapType))
            trap = Trap(trap_type, random.randint(5, 15))
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
            enemy = self._create_enemy(random.choice([EnemyType.ORC, EnemyType.SKELETON]))
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
    
    def _create_random_item(self) -> Item:
        """Create a random item"""
        item_choice = random.choice([ItemType.HEALTH_POTION, ItemType.WEAPON, ItemType.ARMOR, ItemType.TREASURE])
        
        if item_choice == ItemType.HEALTH_POTION:
            return Item(ItemType.HEALTH_POTION, "Health Potion", random.randint(20, 40))
        elif item_choice == ItemType.WEAPON:
            return Item(ItemType.WEAPON, "Sword", random.randint(3, 8))
        elif item_choice == ItemType.ARMOR:
            return Item(ItemType.ARMOR, "Shield", random.randint(2, 5))
        else:
            return Item(ItemType.TREASURE, "Coins", random.randint(10, 50))
    
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
