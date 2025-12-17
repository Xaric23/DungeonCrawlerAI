# DungeonCrawlerAI - Enhanced Edition 🎮

A **reverse dungeon crawler** where the hero is AI-controlled and YOU play as the dungeon's curse!

## 🌟 New Features

### Core Systems

| Feature | Description |
|---------|-------------|
| **Difficulty System** | EASY, NORMAL, HARD, NIGHTMARE modes with scaling stats |
| **Save/Load** | Full game state persistence to JSON |
| **ASCII Visualization** | Beautiful dungeon maps and status displays |
| **Hero Archetypes** | 6 classes: Warrior, Rogue, Paladin, Mage, Berserker, Ranger |
| **Advanced Enemy AI** | 5 behavior types with behavior trees |
| **Dungeon Themes** | 6 unique themes with special mechanics |

### Curse Powers

| Tier | Powers |
|------|--------|
| **Basic** | Trigger Trap, Alter Room, Corrupt Loot, Mutate Enemy, Spawn Trap |
| **Advanced** | Teleport Hero, Charm Enemy, Time Freeze, Mass Corruption, Summon Enemy |
| **Ultimate** | Doom, Dark Blessing, Dungeon Collapse |

### Game Modes

- **Single Hero** - Classic experience
- **Multi-Hero Race** - First to beat boss wins
- **Multi-Hero Survival** - Last hero standing
- **Multi-Hero Coop** - All must survive

## 🚀 Quick Start

```bash
# Basic game (no dependencies)
python main.py

# Enhanced edition with all features
python main_enhanced.py

# Web dashboard (requires Flask)
pip install flask
python web_dashboard.py
```

## 📁 File Structure

```
DungeonCrawlerAI/
├── Core Files
│   ├── models.py           # Data models (Hero, Enemy, Item, Room)
│   ├── behavior_tree.py    # AI decision framework
│   ├── dungeon.py          # Dungeon generation
│   ├── events.py           # Event bus system
│   ├── hero_ai.py          # Hero AI controller
│   ├── player_curse.py     # Basic curse powers
│   └── game.py             # Original game loop
│
├── Enhanced Features
│   ├── difficulty.py       # Difficulty settings
│   ├── save_system.py      # Save/load functionality
│   ├── visualization.py    # ASCII rendering
│   ├── hero_archetypes.py  # Hero classes
│   ├── enemy_ai.py         # Advanced enemy behaviors
│   ├── advanced_curse_powers.py  # New curse abilities
│   ├── curse_synergies.py  # Power combos
│   ├── dungeon_themes.py   # Themed dungeons
│   ├── dynamic_events.py   # Random events
│   ├── item_enhancement.py # Item crafting
│   ├── multi_hero.py       # Multi-hero modes
│   ├── progression.py      # Achievements & XP
│   └── game_enhanced.py    # Integrated game
│
├── Interfaces
│   ├── main.py             # Original entry point
│   ├── main_enhanced.py    # Enhanced menu system
│   └── web_dashboard.py    # Flask web interface
│
└── Documentation
    ├── README.md
    └── README_ENHANCED.md
```

## 🎯 Hero Archetypes

| Class | HP | ATK | DEF | Special | Passive |
|-------|-----|-----|-----|---------|---------|
| **Warrior** | 120 | 18 | 10 | Shield Bash (stun) | Iron Will (+20% HP) |
| **Rogue** | 80 | 22 | 4 | Backstab (2x dmg) | Evasion (30% dodge) |
| **Paladin** | 100 | 14 | 12 | Divine Shield | Holy Aura (regen) |
| **Mage** | 70 | 25 | 3 | Fireball (AoE) | Mana Shield |
| **Berserker** | 90 | 20 | 6 | Rage (+50% ATK) | Bloodlust (heal on kill) |
| **Ranger** | 85 | 16 | 5 | Multi-shot | Trap Sense |

## 🏰 Dungeon Themes

- **Classic Fantasy** - Goblins, Orcs, standard traps
- **Undead Crypt** - Skeletons, Wraiths, enemy respawn
- **Technological** - Robots, lasers, energy shields
- **Volcanic** - Fire enemies, lava, heat damage
- **Ice Cavern** - Frost, freeze, shatter mechanics
- **Eldritch Horror** - Chaos, madness, sanity system

## 🔮 Curse Synergies

Chain specific powers for bonus effects:

| Synergy | Powers | Bonus |
|---------|--------|-------|
| Corruption Chain | 3x Corrupt Loot | Items spread corruption |
| Trap Gauntlet | Spawn + Alter + Trigger | +50% trap damage |
| Mutation Surge | 2x Mutate + Summon | Enemies coordinate |
| Dark Ritual | Charm + Doom + Blessing | Enemy explodes on death |

## 🏆 Achievements

- **First Victory** - Win your first game
- **Speed Demon** - Win in under 30 turns
- **Master Manipulator** - Win with hero suspicion > 80%
- **Stealth Master** - Win with hero suspicion < 10%
- **Nightmare Conqueror** - Win on Nightmare difficulty
- ...and more!

## 🌐 Web Dashboard

Access the game through your browser:

```bash
pip install flask
python web_dashboard.py
# Open http://localhost:5000
```

Features:
- Real-time ASCII map
- Click-to-act curse powers
- Live event log
- Statistics tracking

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/game/new` | POST | Start new game |
| `/api/game/turn` | POST | Execute turn |
| `/api/game/action` | POST | Use curse power |
| `/api/game/state` | GET | Current state |
| `/api/game/map` | GET | ASCII map |
| `/api/stats` | GET | Player stats |
| `/api/achievements` | GET | Achievement list |

## 🎮 Example Session

```
╔══════════════════════════════════════════════════════════╗
║         DungeonCrawlerAI - Reverse Dungeon Crawler       ║
╚══════════════════════════════════════════════════════════╝

Turn 15: Hero in Room 5 (Treasure)
┌─────────────────────────────────────────┐
│ HERO STATUS                             │
│ Health: ████████░░ 78/100               │
│ Attack: 22  Defense: 8  Gold: 150       │
│ Suspicion: ██░░░░░░░░ 24%               │
├─────────────────────────────────────────┤
│ CURSE ENERGY                            │
│ Energy: ██████████ 85/100               │
│ Available: Mutate Enemy, Corrupt Loot   │
└─────────────────────────────────────────┘

[EVENT] Earthquake! All traps triggered!
```

## 🛠️ Development

```bash
# Run tests
python test_game.py

# Run specific demo
python -c "from main_enhanced import demo_difficulty_system; demo_difficulty_system()"
```

## 📜 License

MIT License - Feel free to modify and distribute!

---

**Have fun being evil!** 😈
