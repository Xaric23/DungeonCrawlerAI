# DungeonCrawlerAI

A reverse dungeon crawler where **you don't control the hero**. Instead, the hero is an AI agent that autonomously explores, fights, and loots. You play as the **dungeon's curse**, manipulating the environment to challenge the hero.

## Concept

In traditional dungeon crawlers, you control the hero. In DungeonCrawlerAI, the roles are reversed:
- **The Hero**: An AI agent with behavior trees that explores rooms, fights enemies, and collects loot automatically
- **The Player (You)**: A curse/entity that controls the dungeon, able to trigger traps, corrupt loot, mutate enemies, and alter rooms
- **The Twist**: If you interfere too obviously, the hero becomes suspicious and adapts their behavior

## Features

### 🤖 AI Hero System
- **Behavior Trees**: Sophisticated AI decision-making for exploration, combat, and survival
- **Adaptive Intelligence**: Hero tracks suspicious events and changes behavior when suspicion is high
- **Autonomous Actions**: Makes decisions about movement, combat targets, item usage, and exploration

### 👻 Player Curse Powers
- **Trigger Traps**: Manually activate traps (Low suspicion)
- **Alter Rooms**: Add hazards and additional traps to rooms (Medium suspicion)
- **Corrupt Loot**: Transform helpful items into harmful ones (High suspicion)
- **Mutate Enemies**: Power up enemies mid-combat (Very high suspicion)
- **Spawn Traps**: Create new traps in strategic locations (Medium suspicion)

### 🎮 Event-Driven Architecture
- Decoupled components communicate through an event bus
- Track all game events for analysis and replay
- Easy to extend with new features

### 🏰 Procedural Dungeon
- Randomly generated rooms with enemies, items, and traps
- Connected room structure with exploration paths
- Special rooms: Entrance, Treasure, Boss

## Installation

No external dependencies required! Uses only Python standard library.

```bash
# Clone the repository
git clone https://github.com/Xaric23/DungeonCrawlerAI.git
cd DungeonCrawlerAI

# Run the simulation
python main.py
```

## Usage

### Run the Main Simulation

```bash
python main.py
```

This runs three scenarios:
1. **No Player Curse**: Hero explores alone
2. **Auto Player Curse**: Automated curse actions interfere
3. **Interactive Demo**: Shows how player can control the curse

### Custom Simulation

```python
from game import DungeonCrawlerGame

# Create a game with 15 rooms, player enabled, auto-play disabled
game = DungeonCrawlerGame(num_rooms=15, enable_player=True, auto_player=False)

# Run the simulation
results = game.run_simulation(max_turns=150, verbose=True)

print(f"Victory: {results['victory']}")
print(f"Hero Suspicion: {results['hero_suspicion']}%")
```

### Manual Player Control

```python
from game import DungeonCrawlerGame

game = DungeonCrawlerGame(num_rooms=10, enable_player=True, auto_player=False)

# Initialize hero
game.run_turn()  # Hero enters dungeon

# Use curse powers
hero_room = game.hero.current_room_id

# Corrupt an item in the hero's room
if game.dungeon.get_room(hero_room).items:
    game.player_curse.corrupt_loot(hero_room, item_index=0)

# Mutate an enemy
if game.dungeon.get_room(hero_room).get_alive_enemies():
    game.player_curse.mutate_enemy(hero_room, enemy_index=0)

# Continue the game
while game.run_turn():
    # Game runs until hero dies or completes dungeon
    pass
```

## Architecture

### Core Components

1. **Models** (`models.py`)
   - Data structures for Hero, Enemies, Items, Rooms, Traps
   - Game entities with stats and behaviors

2. **Behavior Trees** (`behavior_tree.py`)
   - Flexible AI decision-making framework
   - Nodes: Sequence, Selector, Action, Condition
   - Composable and reusable AI behaviors

3. **Hero AI** (`hero_ai.py`)
   - Implements hero's decision-making using behavior trees
   - Priority system: Heal → Fight → Loot → Explore
   - Tracks and reacts to player interference

4. **Dungeon** (`dungeon.py`)
   - Procedural dungeon generation
   - Room connections and layout
   - Population with enemies, items, and traps

5. **Player Curse** (`player_curse.py`)
   - Curse power implementations
   - Energy/resource management
   - Suspicion tracking

6. **Events** (`events.py`)
   - Event bus for decoupled communication
   - Event types for all game actions
   - Event history and replay

7. **Game** (`game.py`)
   - Main game loop and orchestration
   - Turn-based simulation
   - State management

### Game Flow

```
Start Game
    ↓
Hero AI Evaluates Behavior Tree
    ↓
Execute Action (Move/Fight/Loot/Heal)
    ↓
Publish Events
    ↓
Player Curse Responds (Optional)
    ↓
Check Win/Loss Conditions
    ↓
Repeat Until Game Over
```

### Behavior Tree Structure

```
Hero Root (Selector)
├─ Critical Health Handler (Sequence)
│  ├─ Is Critical Health? (Condition)
│  └─ Use Health Potion (Action)
├─ Combat Handler (Sequence)
│  ├─ Has Enemies? (Condition)
│  └─ Fight Enemy (Action)
├─ Loot Handler (Sequence)
│  ├─ Has Items? (Condition)
│  └─ Loot Item (Action)
└─ Exploration Handler (Sequence)
   ├─ Can Explore? (Condition)
   └─ Move to Next Room (Action)
```

## Game Balance

### Hero Adaptation
- **Suspicion Level 0-30%**: Normal behavior
- **Suspicion Level 31-50%**: Slightly cautious
- **Suspicion Level 51-100%**: Highly suspicious, may avoid corrupted items

### Curse Energy Costs
- Trigger Trap: 5 energy (Low suspicion)
- Spawn Trap: 15 energy (Medium suspicion)
- Corrupt Loot: 15 energy (High suspicion)
- Alter Room: 20 energy (Medium suspicion)
- Mutate Enemy: 25 energy (Very high suspicion)
- Regeneration: +5 energy per turn

### Strategy Tips
- Use traps early when hero is weak
- Save mutations for critical fights
- Corrupt healing items to prevent recovery
- Don't overuse powers or hero will adapt
- Balance energy usage across multiple turns

## Example Output

```
=== DungeonCrawlerAI Simulation Started ===
Dungeon: 10 rooms
Hero: Hero(Brave Adventurer, HP=100/100, ATK=15, DEF=5)
Player Curse: Enabled (Auto: True)
==================================================

Turn 10: Hero(Brave Adventurer, HP=85/100, ATK=18, DEF=7)
  PlayerCurse(energy=75/100, actions=3)

Turn 20: Hero(Brave Adventurer, HP=72/100, ATK=23, DEF=7 (SUSPICIOUS: 35%))
  PlayerCurse(energy=60/100, actions=7)

==================================================
=== Game Over ===
Turns: 45
Result: VICTORY
Reason: Hero defeated the boss!
Hero Final State: Hero(Brave Adventurer, HP=45/100, ATK=28, DEF=9 (SUSPICIOUS: 65%))
Player Actions Taken: 12
Hero Suspicion Level: 65%
==================================================
```

## Extending the Game

### Add New Enemy Types

```python
# In models.py
class EnemyType(Enum):
    VAMPIRE = "vampire"

# In dungeon.py
def _create_enemy(self, enemy_type: EnemyType) -> Enemy:
    if enemy_type == EnemyType.VAMPIRE:
        return Enemy(EnemyType.VAMPIRE, "Vampire", 70, 18, 6)
```

### Add New Curse Powers

```python
# In player_curse.py
def freeze_room(self, room_id: int) -> bool:
    """Freeze all enemies in a room temporarily"""
    cost = 30
    if self.curse_energy < cost:
        return False
    
    room = self.dungeon.get_room(room_id)
    if not room:
        return False
    
    self.curse_energy -= cost
    # Implement freeze logic
    return True
```

### Add New Behavior Nodes

```python
# In hero_ai.py
def _needs_equipment(self, context: HeroAIContext) -> bool:
    """Check if hero needs better equipment"""
    return context.hero.attack < 20

def _seek_treasure_room(self, context: HeroAIContext) -> NodeStatus:
    """Move towards treasure rooms"""
    # Implementation
    return NodeStatus.SUCCESS
```

## Technical Details

- **Language**: Python 3.7+
- **Dependencies**: None (standard library only)
- **Architecture**: Event-driven, component-based
- **AI**: Behavior trees with composable nodes
- **Testing**: Manual simulation and verification

## License

MIT License - Feel free to use and modify!

## Contributing

Contributions welcome! Areas for enhancement:
- More enemy types and behaviors
- Additional curse powers
- Save/load game state
- Visualization (pygame, matplotlib)
- Multiplayer (multiple heroes or curses)
- Difficulty levels
- Achievement system

## Credits

Created as a demonstration of AI behavior trees, event-driven architecture, and reverse game mechanics.