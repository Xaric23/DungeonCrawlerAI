/**
 * DungeonCrawlerAI - JavaScript Game Engine
 * A reverse dungeon crawler where you play as the curse!
 */

// ============ ENUMS & CONSTANTS ============

const ItemType = {
    HEALTH_POTION: 'health_potion',
    WEAPON: 'weapon',
    ARMOR: 'armor',
    TREASURE: 'treasure'
};

const ItemQuality = {
    NORMAL: 'normal',
    CORRUPTED: 'corrupted',
    CURSED: 'cursed'
};

const EnemyType = {
    GOBLIN: 'goblin',
    ORC: 'orc',
    SKELETON: 'skeleton',
    DRAGON: 'dragon',
    WRAITH: 'wraith',
    ROBOT: 'robot'
};

const TrapType = {
    SPIKE: 'spike',
    POISON: 'poison',
    ARROW: 'arrow',
    FIRE: 'fire'
};

const RoomType = {
    ENTRANCE: 'entrance',
    NORMAL: 'normal',
    TREASURE: 'treasure',
    BOSS: 'boss'
};

const Difficulty = {
    EASY: {
        heroHpMult: 1.5,
        heroAtkMult: 1.2,
        energyRegen: 8,
        enemyDmgMult: 0.8,
        startEnergy: 150
    },
    NORMAL: {
        heroHpMult: 1.0,
        heroAtkMult: 1.0,
        energyRegen: 5,
        enemyDmgMult: 1.0,
        startEnergy: 100
    },
    HARD: {
        heroHpMult: 0.8,
        heroAtkMult: 0.9,
        energyRegen: 3,
        enemyDmgMult: 1.3,
        startEnergy: 80
    },
    NIGHTMARE: {
        heroHpMult: 0.6,
        heroAtkMult: 0.8,
        energyRegen: 2,
        enemyDmgMult: 1.5,
        startEnergy: 50
    }
};

const Archetypes = {
    WARRIOR: { hp: 120, atk: 18, def: 10, name: 'Warrior' },
    ROGUE: { hp: 80, atk: 22, def: 4, name: 'Rogue' },
    PALADIN: { hp: 100, atk: 14, def: 12, name: 'Paladin' },
    MAGE: { hp: 70, atk: 25, def: 3, name: 'Mage' },
    BERSERKER: { hp: 90, atk: 20, def: 6, name: 'Berserker' },
    RANGER: { hp: 85, atk: 16, def: 5, name: 'Ranger' }
};

// ============ GAME CLASSES ============

class Item {
    constructor(type, name, value, quality = ItemQuality.NORMAL) {
        this.type = type;
        this.name = name;
        this.value = value;
        this.quality = quality;
        this.originalValue = value;
    }

    corrupt() {
        if (this.quality === ItemQuality.NORMAL) {
            this.quality = ItemQuality.CORRUPTED;
            this.value = Math.floor(this.value * 0.5);
        } else if (this.quality === ItemQuality.CORRUPTED) {
            this.quality = ItemQuality.CURSED;
            this.value = -Math.abs(this.value);
        }
    }
}

class Enemy {
    constructor(type, name, health, attack, defense) {
        this.type = type;
        this.name = name;
        this.maxHealth = health;
        this.health = health;
        this.baseAttack = attack;
        this.attack = attack;
        this.baseDefense = defense;
        this.defense = defense;
        this.isMutated = false;
        this.isAlive = true;
    }

    mutate() {
        if (!this.isMutated) {
            this.isMutated = true;
            this.attack = Math.floor(this.attack * 1.5);
            this.defense = Math.floor(this.defense * 1.3);
            this.maxHealth = Math.floor(this.maxHealth * 1.4);
            this.health = Math.min(this.maxHealth, Math.floor(this.health * 1.4));
        }
    }

    takeDamage(damage) {
        const actualDamage = Math.max(1, damage - this.defense);
        this.health -= actualDamage;
        if (this.health <= 0) {
            this.isAlive = false;
            this.health = 0;
        }
        return actualDamage;
    }
}

class Trap {
    constructor(type, damage) {
        this.type = type;
        this.damage = damage;
        this.triggered = false;
    }

    trigger() {
        if (!this.triggered) {
            this.triggered = true;
            return this.damage;
        }
        return 0;
    }
}

class Room {
    constructor(id, type) {
        this.id = id;
        this.type = type;
        this.items = [];
        this.enemies = [];
        this.traps = [];
        this.connectedRooms = [];
        this.visited = false;
        this.altered = false;
    }

    getAliveEnemies() {
        return this.enemies.filter(e => e.isAlive);
    }

    getUntriggeredTraps() {
        return this.traps.filter(t => !t.triggered);
    }
}

class Hero {
    constructor(name, archetype = 'WARRIOR') {
        const stats = Archetypes[archetype.toUpperCase()] || Archetypes.WARRIOR;
        this.name = name;
        this.archetype = archetype;
        this.maxHealth = stats.hp;
        this.health = stats.hp;
        this.baseAttack = stats.atk;
        this.attack = stats.atk;
        this.defense = stats.def;
        this.inventory = [];
        this.currentRoomId = null;
        this.visitedRooms = [];
        this.isAlive = true;
        this.suspicionLevel = 0;
        this.gold = 0;
    }

    takeDamage(damage) {
        const actualDamage = Math.max(1, damage - this.defense);
        this.health -= actualDamage;
        if (this.health <= 0) {
            this.isAlive = false;
            this.health = 0;
        }
        return actualDamage;
    }

    heal(amount) {
        this.health = Math.min(this.maxHealth, this.health + amount);
    }

    addItem(item) {
        this.inventory.push(item);
        if (item.type === ItemType.WEAPON) {
            this.attack += item.value;
        } else if (item.type === ItemType.ARMOR) {
            this.defense += item.value;
        } else if (item.type === ItemType.TREASURE) {
            this.gold += item.value;
        } else if (item.type === ItemType.HEALTH_POTION && item.quality === ItemQuality.CURSED) {
            this.health = Math.max(1, this.health + item.value);
        }
    }

    useHealthPotion() {
        const potionIndex = this.inventory.findIndex(
            item => item.type === ItemType.HEALTH_POTION && item.quality !== ItemQuality.CURSED
        );
        if (potionIndex !== -1) {
            const potion = this.inventory[potionIndex];
            this.heal(potion.value);
            this.inventory.splice(potionIndex, 1);
            return true;
        }
        return false;
    }

    increaseSuspicion(amount) {
        this.suspicionLevel = Math.min(100, this.suspicionLevel + amount);
    }

    isSuspicious() {
        return this.suspicionLevel > 50;
    }
}

class Dungeon {
    constructor(numRooms = 10, theme = 'fantasy') {
        this.rooms = {};
        this.numRooms = numRooms;
        this.theme = theme;
        this.entranceRoomId = 0;
        this.generateDungeon();
    }

    generateDungeon() {
        // Create entrance
        this.rooms[0] = new Room(0, RoomType.ENTRANCE);

        // Create normal rooms
        for (let i = 1; i < this.numRooms - 2; i++) {
            const room = new Room(i, RoomType.NORMAL);
            this.populateRoom(room);
            this.rooms[i] = room;
        }

        // Create treasure room
        const treasureId = this.numRooms - 2;
        const treasureRoom = new Room(treasureId, RoomType.TREASURE);
        this.populateTreasureRoom(treasureRoom);
        this.rooms[treasureId] = treasureRoom;

        // Create boss room
        const bossId = this.numRooms - 1;
        const bossRoom = new Room(bossId, RoomType.BOSS);
        this.populateBossRoom(bossRoom);
        this.rooms[bossId] = bossRoom;

        // Connect rooms
        this.connectRooms();
    }

    populateRoom(room) {
        // Add enemies (50% chance)
        if (Math.random() < 0.5) {
            const numEnemies = Math.floor(Math.random() * 2) + 1;
            for (let i = 0; i < numEnemies; i++) {
                room.enemies.push(this.createRandomEnemy());
            }
        }

        // Add items (40% chance)
        if (Math.random() < 0.4) {
            room.items.push(this.createRandomItem());
        }

        // Add traps (30% chance)
        if (Math.random() < 0.3) {
            const trapTypes = Object.values(TrapType);
            const trapType = trapTypes[Math.floor(Math.random() * trapTypes.length)];
            room.traps.push(new Trap(trapType, 5 + Math.floor(Math.random() * 11)));
        }
    }

    populateTreasureRoom(room) {
        // Add treasures
        for (let i = 0; i < 2 + Math.floor(Math.random() * 3); i++) {
            room.items.push(new Item(ItemType.TREASURE, 'Gold Coins', 50 + Math.floor(Math.random() * 101)));
        }

        // Add good equipment
        room.items.push(new Item(ItemType.WEAPON, 'Enchanted Sword', 10 + Math.floor(Math.random() * 11)));
        room.items.push(new Item(ItemType.ARMOR, 'Sturdy Armor', 5 + Math.floor(Math.random() * 6)));

        // Guards
        room.enemies.push(this.createEnemy(EnemyType.ORC));
        room.enemies.push(this.createEnemy(EnemyType.SKELETON));
    }

    populateBossRoom(room) {
        room.enemies.push(new Enemy(EnemyType.DRAGON, 'Dragon Boss', 150, 25, 10));
        
        // Boss treasure
        for (let i = 0; i < 3; i++) {
            room.items.push(new Item(ItemType.TREASURE, 'Dragon Hoard', 100 + Math.floor(Math.random() * 101)));
        }
    }

    createRandomEnemy() {
        const types = [EnemyType.GOBLIN, EnemyType.ORC, EnemyType.SKELETON];
        return this.createEnemy(types[Math.floor(Math.random() * types.length)]);
    }

    createEnemy(type) {
        switch (type) {
            case EnemyType.GOBLIN:
                return new Enemy(type, 'Goblin', 30, 8, 2);
            case EnemyType.ORC:
                return new Enemy(type, 'Orc', 50, 12, 5);
            case EnemyType.SKELETON:
                return new Enemy(type, 'Skeleton', 40, 10, 3);
            case EnemyType.DRAGON:
                return new Enemy(type, 'Dragon', 150, 25, 10);
            case EnemyType.WRAITH:
                return new Enemy(type, 'Wraith', 35, 15, 1);
            default:
                return new Enemy(type, 'Monster', 40, 10, 3);
        }
    }

    createRandomItem() {
        const types = [ItemType.HEALTH_POTION, ItemType.WEAPON, ItemType.ARMOR, ItemType.TREASURE];
        const type = types[Math.floor(Math.random() * types.length)];

        switch (type) {
            case ItemType.HEALTH_POTION:
                return new Item(type, 'Health Potion', 20 + Math.floor(Math.random() * 21));
            case ItemType.WEAPON:
                return new Item(type, 'Sword', 3 + Math.floor(Math.random() * 6));
            case ItemType.ARMOR:
                return new Item(type, 'Shield', 2 + Math.floor(Math.random() * 4));
            case ItemType.TREASURE:
                return new Item(type, 'Coins', 10 + Math.floor(Math.random() * 41));
        }
    }

    connectRooms() {
        // Linear path
        for (let i = 0; i < this.numRooms - 1; i++) {
            this.rooms[i].connectedRooms.push(i + 1);
            this.rooms[i + 1].connectedRooms.push(i);
        }

        // Some branches
        for (let i = 1; i < this.numRooms - 2; i++) {
            if (Math.random() < 0.3 && i + 2 < this.numRooms - 1) {
                if (!this.rooms[i].connectedRooms.includes(i + 2)) {
                    this.rooms[i].connectedRooms.push(i + 2);
                    this.rooms[i + 2].connectedRooms.push(i);
                }
            }
        }
    }

    getRoom(roomId) {
        return this.rooms[roomId];
    }
}

class PlayerCurse {
    constructor(dungeon, startEnergy = 100) {
        this.dungeon = dungeon;
        this.energy = startEnergy;
        this.maxEnergy = 100;
        this.actionsTaken = 0;
        this.energyRegen = 5;
    }

    regenerateEnergy() {
        this.energy = Math.min(this.maxEnergy, this.energy + this.energyRegen);
    }

    canAfford(cost) {
        return this.energy >= cost;
    }

    spendEnergy(cost) {
        if (this.canAfford(cost)) {
            this.energy -= cost;
            this.actionsTaken++;
            return true;
        }
        return false;
    }

    triggerTrap(roomId, trapIndex = 0) {
        const cost = 5;
        if (!this.canAfford(cost)) return { success: false, reason: 'Not enough energy' };

        const room = this.dungeon.getRoom(roomId);
        if (!room) return { success: false, reason: 'Invalid room' };

        const untriggered = room.getUntriggeredTraps();
        if (trapIndex >= untriggered.length) return { success: false, reason: 'No trap available' };

        this.spendEnergy(cost);
        return { success: true, action: 'trigger_trap', room: roomId };
    }

    alterRoom(roomId) {
        const cost = 20;
        if (!this.canAfford(cost)) return { success: false, reason: 'Not enough energy' };

        const room = this.dungeon.getRoom(roomId);
        if (!room || room.altered) return { success: false, reason: 'Cannot alter room' };

        this.spendEnergy(cost);
        room.altered = true;
        
        const trapTypes = Object.values(TrapType);
        const trapType = trapTypes[Math.floor(Math.random() * trapTypes.length)];
        room.traps.push(new Trap(trapType, 10 + Math.floor(Math.random() * 21)));

        return { success: true, action: 'alter_room', room: roomId };
    }

    corruptLoot(roomId, itemIndex = 0) {
        const cost = 15;
        if (!this.canAfford(cost)) return { success: false, reason: 'Not enough energy' };

        const room = this.dungeon.getRoom(roomId);
        if (!room || itemIndex >= room.items.length) return { success: false, reason: 'No item available' };

        this.spendEnergy(cost);
        room.items[itemIndex].corrupt();

        return { success: true, action: 'corrupt_loot', room: roomId, item: room.items[itemIndex].name };
    }

    mutateEnemy(roomId, enemyIndex = 0) {
        const cost = 25;
        if (!this.canAfford(cost)) return { success: false, reason: 'Not enough energy' };

        const room = this.dungeon.getRoom(roomId);
        if (!room) return { success: false, reason: 'Invalid room' };

        const alive = room.getAliveEnemies();
        if (enemyIndex >= alive.length) return { success: false, reason: 'No enemy available' };

        const enemy = alive[enemyIndex];
        if (enemy.isMutated) return { success: false, reason: 'Already mutated' };

        this.spendEnergy(cost);
        enemy.mutate();

        return { success: true, action: 'mutate_enemy', room: roomId, enemy: enemy.name };
    }

    spawnTrap(roomId) {
        const cost = 15;
        if (!this.canAfford(cost)) return { success: false, reason: 'Not enough energy' };

        const room = this.dungeon.getRoom(roomId);
        if (!room) return { success: false, reason: 'Invalid room' };

        this.spendEnergy(cost);
        const trapTypes = Object.values(TrapType);
        const trapType = trapTypes[Math.floor(Math.random() * trapTypes.length)];
        room.traps.push(new Trap(trapType, 15 + Math.floor(Math.random() * 11)));

        return { success: true, action: 'spawn_trap', room: roomId };
    }

    teleportHero(hero) {
        const cost = 35;
        if (!this.canAfford(cost)) return { success: false, reason: 'Not enough energy' };

        const roomIds = Object.keys(this.dungeon.rooms).map(Number);
        const validRooms = roomIds.filter(id => id !== hero.currentRoomId);
        if (validRooms.length === 0) return { success: false, reason: 'No valid room' };

        this.spendEnergy(cost);
        const newRoom = validRooms[Math.floor(Math.random() * validRooms.length)];
        
        return { success: true, action: 'teleport', from: hero.currentRoomId, to: newRoom };
    }

    summonEnemy(roomId) {
        const cost = 30;
        if (!this.canAfford(cost)) return { success: false, reason: 'Not enough energy' };

        const room = this.dungeon.getRoom(roomId);
        if (!room) return { success: false, reason: 'Invalid room' };

        this.spendEnergy(cost);
        const enemy = this.dungeon.createRandomEnemy();
        room.enemies.push(enemy);

        return { success: true, action: 'summon', room: roomId, enemy: enemy.name };
    }
}

// ============ HERO AI ============

class HeroAI {
    constructor(hero, dungeon) {
        this.hero = hero;
        this.dungeon = dungeon;
        this.targetEnemy = null;
    }

    tick() {
        if (!this.hero.isAlive) return { action: 'dead' };

        const room = this.dungeon.getRoom(this.hero.currentRoomId);

        // Priority 1: Heal if critical
        if (this.hero.health < this.hero.maxHealth * 0.3) {
            if (this.hero.useHealthPotion()) {
                return { action: 'heal', health: this.hero.health };
            }
        }

        // Priority 2: Fight enemies
        if (room) {
            const enemies = room.getAliveEnemies();
            if (enemies.length > 0) {
                return this.fight(room, enemies);
            }
        }

        // Priority 3: Loot items
        if (room && room.items.length > 0) {
            return this.loot(room);
        }

        // Priority 4: Explore
        return this.explore(room);
    }

    fight(room, enemies) {
        const enemy = enemies.reduce((a, b) => a.attack > b.attack ? a : b);
        
        // Hero attacks
        const damageDealt = enemy.takeDamage(this.hero.attack);
        const result = { action: 'attack', enemy: enemy.name, damage: damageDealt };

        if (!enemy.isAlive) {
            result.killed = true;
            return result;
        }

        // Enemy counter-attacks
        const damageTaken = this.hero.takeDamage(enemy.attack);
        result.counterDamage = damageTaken;

        if (enemy.isMutated && !this.hero.isSuspicious()) {
            this.hero.increaseSuspicion(5);
        }

        return result;
    }

    loot(room) {
        const item = room.items[0];

        // Suspicious hero might skip corrupted items
        if (this.hero.isSuspicious() && item.quality !== ItemQuality.NORMAL) {
            if (Math.random() < 0.5) {
                room.items.shift();
                return { action: 'skip_loot', item: item.name, reason: 'suspicious' };
            }
        }

        room.items.shift();
        this.hero.addItem(item);

        if (item.quality !== ItemQuality.NORMAL) {
            this.hero.increaseSuspicion(5);
        }

        return { action: 'loot', item: item.name, quality: item.quality };
    }

    explore(room) {
        // Initial entry
        if (this.hero.currentRoomId === null) {
            this.hero.currentRoomId = this.dungeon.entranceRoomId;
            this.hero.visitedRooms.push(this.dungeon.entranceRoomId);
            const startRoom = this.dungeon.getRoom(this.dungeon.entranceRoomId);
            startRoom.visited = true;
            return { action: 'enter', room: this.dungeon.entranceRoomId };
        }

        if (!room || room.connectedRooms.length === 0) {
            return { action: 'stuck' };
        }

        // Find unvisited rooms
        const unvisited = room.connectedRooms.filter(id => !this.hero.visitedRooms.includes(id));
        let nextRoomId;

        if (unvisited.length > 0) {
            nextRoomId = unvisited[Math.floor(Math.random() * unvisited.length)];
        } else {
            nextRoomId = room.connectedRooms[Math.floor(Math.random() * room.connectedRooms.length)];
        }

        const previousRoom = this.hero.currentRoomId;
        this.hero.currentRoomId = nextRoomId;
        
        if (!this.hero.visitedRooms.includes(nextRoomId)) {
            this.hero.visitedRooms.push(nextRoomId);
        }

        const nextRoom = this.dungeon.getRoom(nextRoomId);
        nextRoom.visited = true;

        const result = { action: 'move', from: previousRoom, to: nextRoomId, type: nextRoom.type };

        // Trigger traps
        const untriggeredTraps = nextRoom.getUntriggeredTraps();
        if (untriggeredTraps.length > 0) {
            let totalTrapDamage = 0;
            for (const trap of untriggeredTraps) {
                totalTrapDamage += trap.trigger();
            }
            this.hero.takeDamage(totalTrapDamage);
            result.trapDamage = totalTrapDamage;

            if (nextRoom.traps.length > 2 || nextRoom.altered) {
                this.hero.increaseSuspicion(10);
            }
        }

        return result;
    }
}

// ============ MAIN GAME ============

class DungeonCrawlerGame {
    constructor(config = {}) {
        this.config = {
            numRooms: config.numRooms || 10,
            difficulty: config.difficulty || 'NORMAL',
            archetype: config.archetype || 'WARRIOR',
            theme: config.theme || 'fantasy'
        };

        this.difficultySettings = Difficulty[this.config.difficulty.toUpperCase()] || Difficulty.NORMAL;
        
        this.dungeon = new Dungeon(this.config.numRooms, this.config.theme);
        this.hero = new Hero('Brave Adventurer', this.config.archetype);
        this.applyDifficultyToHero();
        
        this.heroAI = new HeroAI(this.hero, this.dungeon);
        this.curse = new PlayerCurse(this.dungeon, this.difficultySettings.startEnergy);
        this.curse.energyRegen = this.difficultySettings.energyRegen;

        this.turn = 0;
        this.maxTurns = 200;
        this.gameOver = false;
        this.victory = false;
        this.reason = '';
        this.eventLog = [];
        this.isPaused = false;
        this.speed = 1000; // ms per turn
    }

    applyDifficultyToHero() {
        this.hero.maxHealth = Math.floor(this.hero.maxHealth * this.difficultySettings.heroHpMult);
        this.hero.health = this.hero.maxHealth;
        this.hero.attack = Math.floor(this.hero.attack * this.difficultySettings.heroAtkMult);
    }

    log(message, type = 'normal') {
        this.eventLog.push({ turn: this.turn, message, type });
        if (this.eventLog.length > 100) {
            this.eventLog.shift();
        }
    }

    runTurn() {
        if (this.gameOver || this.isPaused) return false;

        if (this.turn >= this.maxTurns) {
            this.gameOver = true;
            this.reason = 'Turn limit reached';
            return false;
        }

        this.turn++;

        // Hero AI action
        const heroAction = this.heroAI.tick();
        this.processHeroAction(heroAction);

        // Check game over
        if (!this.hero.isAlive) {
            this.gameOver = true;
            this.victory = true; // Curse wins!
            this.reason = 'Hero was defeated!';
            this.log('💀 Hero has fallen!', 'combat');
            return false;
        }

        // Check victory (hero wins)
        const currentRoom = this.dungeon.getRoom(this.hero.currentRoomId);
        if (currentRoom && currentRoom.type === RoomType.BOSS) {
            if (currentRoom.getAliveEnemies().length === 0) {
                this.gameOver = true;
                this.victory = false; // Hero wins, curse loses
                this.reason = 'Hero defeated the boss!';
                this.log('👑 Hero conquered the dungeon!', 'hero-action');
                return false;
            }
        }

        // Curse regenerates energy
        this.curse.regenerateEnergy();

        return true;
    }

    processHeroAction(action) {
        switch (action.action) {
            case 'enter':
                this.log(`🚪 Hero entered the dungeon (Room ${action.room})`, 'hero-action');
                break;
            case 'move':
                let moveMsg = `🚶 Hero moved to Room ${action.to} (${action.type})`;
                if (action.trapDamage) {
                    moveMsg += ` - Trap dealt ${action.trapDamage} damage!`;
                }
                this.log(moveMsg, action.trapDamage ? 'combat' : 'hero-action');
                break;
            case 'attack':
                let atkMsg = `⚔️ Hero attacks ${action.enemy} for ${action.damage} damage`;
                if (action.killed) {
                    atkMsg += ' - KILLED!';
                } else if (action.counterDamage) {
                    atkMsg += ` (took ${action.counterDamage} counter)`;
                }
                this.log(atkMsg, 'combat');
                break;
            case 'loot':
                this.log(`💰 Hero looted ${action.item} (${action.quality})`, 'loot');
                break;
            case 'skip_loot':
                this.log(`🤔 Hero skipped suspicious ${action.item}`, 'loot');
                break;
            case 'heal':
                this.log(`💊 Hero used potion (HP: ${action.health})`, 'hero-action');
                break;
        }
    }

    executeCursePower(power, roomId = null) {
        if (roomId === null) roomId = this.hero.currentRoomId;
        
        let result;
        switch (power) {
            case 'trigger_trap':
                result = this.curse.triggerTrap(roomId);
                if (result.success) {
                    this.log(`⚡ Triggered trap in Room ${roomId}!`, 'curse-action');
                    this.hero.increaseSuspicion(3);
                }
                break;
            case 'alter_room':
                result = this.curse.alterRoom(roomId);
                if (result.success) {
                    this.log(`🏚️ Altered Room ${roomId} - trap added!`, 'curse-action');
                    this.hero.increaseSuspicion(8);
                }
                break;
            case 'corrupt_loot':
                result = this.curse.corruptLoot(roomId);
                if (result.success) {
                    this.log(`💀 Corrupted ${result.item} in Room ${roomId}!`, 'curse-action');
                    this.hero.increaseSuspicion(10);
                }
                break;
            case 'mutate_enemy':
                result = this.curse.mutateEnemy(roomId);
                if (result.success) {
                    this.log(`👹 Mutated ${result.enemy} in Room ${roomId}!`, 'curse-action');
                    this.hero.increaseSuspicion(15);
                }
                break;
            case 'spawn_trap':
                result = this.curse.spawnTrap(roomId);
                if (result.success) {
                    this.log(`🪤 Spawned trap in Room ${roomId}!`, 'curse-action');
                    this.hero.increaseSuspicion(5);
                }
                break;
            case 'teleport':
                result = this.curse.teleportHero(this.hero);
                if (result.success) {
                    this.hero.currentRoomId = result.to;
                    this.log(`🌀 Teleported hero to Room ${result.to}!`, 'curse-action');
                    this.hero.increaseSuspicion(20);
                }
                break;
            case 'summon':
                result = this.curse.summonEnemy(roomId);
                if (result.success) {
                    this.log(`👻 Summoned ${result.enemy} in Room ${roomId}!`, 'curse-action');
                    this.hero.increaseSuspicion(12);
                }
                break;
            default:
                result = { success: false, reason: 'Unknown power' };
        }

        return result;
    }

    getState() {
        const room = this.dungeon.getRoom(this.hero.currentRoomId);
        return {
            turn: this.turn,
            hero: {
                health: this.hero.health,
                maxHealth: this.hero.maxHealth,
                attack: this.hero.attack,
                defense: this.hero.defense,
                gold: this.hero.gold,
                suspicion: this.hero.suspicionLevel,
                currentRoom: this.hero.currentRoomId,
                isAlive: this.hero.isAlive
            },
            curse: {
                energy: this.curse.energy,
                maxEnergy: this.curse.maxEnergy,
                actions: this.curse.actionsTaken
            },
            room: room ? {
                id: room.id,
                type: room.type,
                enemies: room.getAliveEnemies().length,
                items: room.items.length,
                traps: room.traps.length
            } : null,
            gameOver: this.gameOver,
            victory: this.victory,
            reason: this.reason
        };
    }
}

// ============ UI CONTROLLER ============

class GameUI {
    constructor() {
        this.game = null;
        this.autoRunInterval = null;
        this.isAutoRunning = false;
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('start-btn').addEventListener('click', () => this.startGame());
        document.getElementById('restart-btn').addEventListener('click', () => this.showSetup());
        document.getElementById('pause-btn').addEventListener('click', () => this.togglePause());
        document.getElementById('speed-btn').addEventListener('click', () => this.toggleSpeed());

        // Power buttons
        document.querySelectorAll('.power-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const power = btn.dataset.power;
                this.usePower(power);
            });
        });
    }

    startGame() {
        const config = {
            numRooms: parseInt(document.getElementById('rooms-select').value),
            difficulty: document.getElementById('difficulty-select').value.toUpperCase(),
            archetype: document.getElementById('archetype-select').value.toUpperCase(),
            theme: document.getElementById('theme-select').value
        };

        this.game = new DungeonCrawlerGame(config);
        this.game.log('🎮 Game started! You are the curse.', 'event');

        document.getElementById('setup-screen').classList.add('hidden');
        document.getElementById('game-screen').classList.remove('hidden');
        document.getElementById('gameover-screen').classList.add('hidden');

        this.renderMap();
        this.updateUI();
        this.startAutoRun();
    }

    showSetup() {
        this.stopAutoRun();
        document.getElementById('setup-screen').classList.remove('hidden');
        document.getElementById('game-screen').classList.add('hidden');
        document.getElementById('gameover-screen').classList.add('hidden');
    }

    showGameOver() {
        this.stopAutoRun();
        
        const state = this.game.getState();
        
        document.getElementById('game-screen').classList.add('hidden');
        document.getElementById('gameover-screen').classList.remove('hidden');

        const title = document.getElementById('gameover-title');
        const message = document.getElementById('gameover-message');

        if (this.game.victory) {
            title.textContent = '😈 Victory!';
            title.className = 'victory';
            message.textContent = 'The hero has fallen to your curse!';
        } else {
            title.textContent = '😢 Defeat';
            title.className = 'defeat';
            message.textContent = 'The hero conquered your dungeon...';
        }

        document.getElementById('final-turns').textContent = state.turn;
        document.getElementById('final-health').textContent = state.hero.health;
        document.getElementById('final-suspicion').textContent = state.hero.suspicion + '%';
        document.getElementById('final-actions').textContent = state.curse.actions;
        document.getElementById('final-gold').textContent = state.hero.gold;
    }

    startAutoRun() {
        this.isAutoRunning = true;
        document.getElementById('pause-btn').textContent = '⏸️ Pause';
        
        this.autoRunInterval = setInterval(() => {
            if (!this.game.gameOver && !this.game.isPaused) {
                this.game.runTurn();
                this.updateUI();

                if (this.game.gameOver) {
                    this.showGameOver();
                }
            }
        }, this.game.speed);
    }

    stopAutoRun() {
        this.isAutoRunning = false;
        if (this.autoRunInterval) {
            clearInterval(this.autoRunInterval);
            this.autoRunInterval = null;
        }
    }

    togglePause() {
        this.game.isPaused = !this.game.isPaused;
        document.getElementById('pause-btn').textContent = this.game.isPaused ? '▶️ Resume' : '⏸️ Pause';
    }

    toggleSpeed() {
        const btn = document.getElementById('speed-btn');
        if (this.game.speed === 1000) {
            this.game.speed = 500;
            btn.textContent = '🐇 Fast';
        } else if (this.game.speed === 500) {
            this.game.speed = 200;
            btn.textContent = '⚡ Faster';
        } else {
            this.game.speed = 1000;
            btn.textContent = '🐢 Normal';
        }

        // Restart auto-run with new speed
        if (this.isAutoRunning) {
            this.stopAutoRun();
            this.startAutoRun();
        }
    }

    usePower(power) {
        if (this.game.gameOver) return;

        const result = this.game.executeCursePower(power);
        if (!result.success) {
            this.game.log(`❌ Failed: ${result.reason}`, 'event');
        }
        this.updateUI();
    }

    renderMap() {
        const mapContainer = document.getElementById('dungeon-map');
        mapContainer.innerHTML = '';

        const rooms = this.game.dungeon.rooms;
        const numRooms = this.game.dungeon.numRooms;

        // Calculate grid layout
        const cols = Math.min(5, numRooms);
        mapContainer.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;

        for (let i = 0; i < numRooms; i++) {
            const room = rooms[i];
            const cell = document.createElement('div');
            cell.className = 'room-cell';
            cell.dataset.roomId = i;

            // Room type styling
            cell.classList.add(room.type);
            
            // Visited status
            cell.classList.add(room.visited ? 'visited' : 'unvisited');

            // Hero location
            if (this.game.hero.currentRoomId === i) {
                cell.classList.add('hero-here');
            }

            // Room icon
            let icon = '🚪';
            switch (room.type) {
                case RoomType.ENTRANCE: icon = '🚪'; break;
                case RoomType.NORMAL: icon = '🏠'; break;
                case RoomType.TREASURE: icon = '💎'; break;
                case RoomType.BOSS: icon = '🐉'; break;
            }

            cell.innerHTML = `
                <div class="room-type-icon">${icon}</div>
                <div class="room-contents">
                    ${room.getAliveEnemies().length > 0 ? '👹' + room.getAliveEnemies().length : ''}
                    ${room.items.length > 0 ? '📦' + room.items.length : ''}
                    ${room.getUntriggeredTraps().length > 0 ? '⚠️' : ''}
                </div>
                ${this.game.hero.currentRoomId === i ? '<div class="room-hero-marker">@</div>' : ''}
            `;

            // Click to target room for powers
            cell.addEventListener('click', () => this.selectRoom(i));

            mapContainer.appendChild(cell);
        }
    }

    selectRoom(roomId) {
        // Visual feedback
        document.querySelectorAll('.room-cell').forEach(c => c.style.boxShadow = '');
        const cell = document.querySelector(`[data-room-id="${roomId}"]`);
        if (cell) {
            cell.style.boxShadow = '0 0 15px var(--accent-purple)';
        }

        // Store selected room for next power use
        this.selectedRoom = roomId;
    }

    updateUI() {
        const state = this.game.getState();

        // Turn counter
        document.getElementById('turn-num').textContent = state.turn;

        // Hero status
        document.getElementById('hero-health-bar').style.width = 
            `${(state.hero.health / state.hero.maxHealth) * 100}%`;
        document.getElementById('hero-health-text').textContent = 
            `${state.hero.health}/${state.hero.maxHealth}`;
        document.getElementById('hero-attack').textContent = state.hero.attack;
        document.getElementById('hero-defense').textContent = state.hero.defense;
        document.getElementById('hero-gold').textContent = state.hero.gold;
        document.getElementById('hero-suspicion-bar').style.width = `${state.hero.suspicion}%`;
        document.getElementById('hero-suspicion-text').textContent = `${state.hero.suspicion}%`;

        // Curse status
        document.getElementById('curse-energy-bar').style.width = 
            `${(state.curse.energy / state.curse.maxEnergy) * 100}%`;
        document.getElementById('curse-energy-text').textContent = 
            `${state.curse.energy}/${state.curse.maxEnergy}`;
        document.getElementById('curse-actions').textContent = state.curse.actions;

        // Room info
        if (state.room) {
            document.getElementById('room-id').textContent = state.room.id;
            document.getElementById('room-type').textContent = state.room.type;
            document.getElementById('room-enemies').textContent = state.room.enemies;
            document.getElementById('room-items').textContent = state.room.items;
            document.getElementById('room-traps').textContent = state.room.traps;
        }

        // Update power buttons
        document.querySelectorAll('.power-btn').forEach(btn => {
            const cost = parseInt(btn.dataset.cost);
            btn.disabled = state.curse.energy < cost || state.gameOver;
        });

        // Update map
        this.renderMap();

        // Update event log
        this.updateEventLog();
    }

    updateEventLog() {
        const logContainer = document.getElementById('event-log');
        const recentEvents = this.game.eventLog.slice(-20);
        
        logContainer.innerHTML = recentEvents.map(event => 
            `<div class="log-entry ${event.type}">[${event.turn}] ${event.message}</div>`
        ).join('');

        logContainer.scrollTop = logContainer.scrollHeight;
    }
}

// ============ INIT ============

document.addEventListener('DOMContentLoaded', () => {
    window.gameUI = new GameUI();
});
