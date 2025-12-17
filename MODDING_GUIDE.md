# DungeonCrawlerAI Modding Guide

Welcome to the DungeonCrawlerAI modding system! This guide will help you create custom content for the game.

## Table of Contents
- [Getting Started](#getting-started)
- [Mod Structure](#mod-structure)
- [Creating Custom Enemies](#creating-custom-enemies)
- [Creating Custom Items](#creating-custom-items)
- [Creating Custom Traps](#creating-custom-traps)
- [Creating Custom Curse Powers](#creating-custom-curse-powers)
- [Examples](#examples)

## Getting Started

### Prerequisites
- Python 3.7 or higher
- Basic understanding of JSON format
- DungeonCrawlerAI installed

### Creating Your First Mod

1. Navigate to the `mods` directory in your DungeonCrawlerAI installation
2. Create a new folder for your mod (e.g., `my_custom_mod`)
3. Inside your mod folder, create a file named `mod.json`
4. Define your custom content in the `mod.json` file
5. Run the game - your mod will be automatically loaded!

## Mod Structure

A mod is defined by a `mod.json` file with the following structure:

```json
{
  "name": "My Mod Name",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Description of your mod",
  "enemies": [],
  "items": [],
  "traps": [],
  "curse_powers": []
}
```

### Metadata Fields
- **name**: (Required) Display name of your mod
- **version**: (Optional) Version string (e.g., "1.0.0")
- **author**: (Optional) Your name or handle
- **description**: (Optional) Brief description of what your mod adds

## Creating Custom Enemies

Enemies are hostile creatures that the hero must fight.

### Enemy Definition

```json
{
  "id": "unique_enemy_id",
  "name": "Display Name",
  "type": "enemy_type",
  "health": 100,
  "attack": 20,
  "defense": 5,
  "description": "Flavor text for the enemy"
}
```

### Fields
- **id**: (Required) Unique identifier for this enemy (lowercase, use underscores)
- **name**: (Required) Display name shown in-game
- **type**: (Required) Enemy type identifier (can match id or be a category)
- **health**: (Required) Maximum health points (positive integer)
- **attack**: (Required) Attack power (positive integer)
- **defense**: (Required) Defense value that reduces damage taken (non-negative integer)
- **description**: (Optional) Flavor text or lore

### Example: Custom Boss Enemy

```json
{
  "id": "fire_demon",
  "name": "Infernal Demon Lord",
  "type": "demon",
  "health": 200,
  "attack": 35,
  "defense": 12,
  "description": "A powerful demon wreathed in flames"
}
```

### Balance Guidelines
- Weak enemies: 20-40 HP, 5-10 ATK, 0-3 DEF
- Normal enemies: 40-70 HP, 10-18 ATK, 3-7 DEF
- Strong enemies: 70-120 HP, 18-25 ATK, 7-12 DEF
- Boss enemies: 120-250 HP, 25-40 ATK, 10-20 DEF

## Creating Custom Items

Items can be picked up and used by the hero to improve their capabilities.

### Item Definition

```json
{
  "id": "unique_item_id",
  "name": "Display Name",
  "type": "item_type",
  "value": 50,
  "description": "What the item does"
}
```

### Fields
- **id**: (Required) Unique identifier for this item (lowercase, use underscores)
- **name**: (Required) Display name shown in-game
- **type**: (Required) One of: "weapon", "armor", "health_potion", "treasure"
- **value**: (Required) Numeric value (effect depends on type)
- **description**: (Optional) Flavor text

### Item Types and Values
- **weapon**: Value = attack bonus added to hero (e.g., 10 = +10 attack)
- **armor**: Value = defense bonus added to hero (e.g., 5 = +5 defense)
- **health_potion**: Value = health restored when used (e.g., 50 = +50 HP)
- **treasure**: Value = gold coins collected (e.g., 100 = +100 gold)

### Example: Powerful Weapon

```json
{
  "id": "excalibur",
  "name": "Excalibur",
  "type": "weapon",
  "value": 25,
  "description": "The legendary sword of kings"
}
```

### Balance Guidelines
- Weapons: 5-30 attack bonus
- Armor: 3-15 defense bonus
- Health Potions: 25-100 HP restored
- Treasure: 25-500 gold value

## Creating Custom Traps

Traps are hazards that can damage the hero when triggered.

### Trap Definition

```json
{
  "id": "unique_trap_id",
  "name": "Display Name",
  "type": "trap_type",
  "damage": 25,
  "description": "What happens when triggered"
}
```

### Fields
- **id**: (Required) Unique identifier for this trap (lowercase, use underscores)
- **name**: (Required) Display name shown in-game
- **type**: (Required) Trap type identifier (can match id or be a category)
- **damage**: (Required) Damage dealt when triggered (positive integer)
- **description**: (Optional) Flavor text

### Example: Deadly Trap

```json
{
  "id": "boulder",
  "name": "Rolling Boulder Trap",
  "type": "boulder",
  "damage": 40,
  "description": "A massive boulder crashes down on intruders"
}
```

### Balance Guidelines
- Light traps: 5-15 damage
- Medium traps: 15-30 damage
- Heavy traps: 30-50 damage

## Creating Custom Curse Powers

Curse powers are special abilities the player can use to interfere with the hero.

### Curse Power Definition

```json
{
  "id": "unique_power_id",
  "name": "Display Name",
  "cost": 30,
  "suspicion": 15,
  "description": "What this power does",
  "effect": "effect_type"
}
```

### Fields
- **id**: (Required) Unique identifier for this power (lowercase, use underscores)
- **name**: (Required) Display name shown in-game
- **cost**: (Required) Curse energy cost to use (positive integer)
- **suspicion**: (Required) Suspicion level increase when used (0-50)
- **description**: (Optional) Explanation of what it does
- **effect**: (Required) Effect type identifier

### Effect Types
Currently supported effect types:
- **spawn_enemy**: Spawns an enemy in the current room
- **damage**: Deals direct damage to hero
- **heal_enemies**: Heals all enemies in the room
- **debuff_hero**: Temporarily reduces hero's stats

### Example: Custom Curse Power

```json
{
  "id": "shadow_bolt",
  "name": "Shadow Bolt",
  "cost": 20,
  "suspicion": 10,
  "description": "Strike the hero with dark magic",
  "effect": "damage"
}
```

### Balance Guidelines
- Low suspicion (0-10): Subtle effects, 10-20 energy cost
- Medium suspicion (10-25): Noticeable effects, 20-40 energy cost
- High suspicion (25-50): Obvious interference, 40-60 energy cost

## Examples

### Complete Example Mod

See `mods/example_mod/mod.json` for a complete working example that includes:
- 3 custom enemies (Vampire, Stone Golem, Shadow Stalker)
- 4 custom items (Legendary Sword, Super Potion, Dragon Scales, Ancient Relic)
- 2 custom traps (Lightning, Ice)
- 1 custom curse power (Summon Minion)

### Mini-Mod: Fantasy Enhancement

```json
{
  "name": "Fantasy Enhancement Pack",
  "version": "1.0.0",
  "author": "ModderName",
  "description": "Adds fantasy-themed content",
  "enemies": [
    {
      "id": "elf_ranger",
      "name": "Elf Ranger",
      "type": "elf",
      "health": 50,
      "attack": 22,
      "defense": 4,
      "description": "Swift and accurate with a bow"
    }
  ],
  "items": [
    {
      "id": "elven_cloak",
      "name": "Elven Cloak",
      "type": "armor",
      "value": 8,
      "description": "Light but protective"
    }
  ]
}
```

## Testing Your Mod

1. Place your `mod.json` file in `mods/your_mod_name/`
2. Run the game: `python main.py`
3. Check the console for mod loading messages
4. Play the game to see your custom content in action

## Tips for Modders

1. **Start Small**: Begin with one or two items, then expand
2. **Balance Carefully**: Test your content to ensure it's not too powerful or weak
3. **Use Descriptive IDs**: Make IDs clear and unique (e.g., "fire_demon" not "enemy1")
4. **Consider Lore**: Add descriptions that fit the game's theme
5. **Test Thoroughly**: Make sure your JSON is valid (use a JSON validator)
6. **Share Your Mods**: Share your creations with the community!

## Troubleshooting

### Mod Not Loading
- Check that `mod.json` exists in `mods/your_mod_name/`
- Validate your JSON syntax (missing commas, brackets, etc.)
- Check console output for error messages

### Invalid Values
- Ensure all numeric fields are positive integers
- Check that required fields are present
- Verify field names are spelled correctly

### Custom Content Not Appearing
- Mod content is randomly selected for spawning
- Play multiple games to see your custom content
- Check that IDs are unique and don't conflict with other mods

## Advanced Modding

### Multiple Mods
You can install multiple mods simultaneously. Each mod should be in its own directory:
```
mods/
  mod_a/
    mod.json
  mod_b/
    mod.json
  mod_c/
    mod.json
```

All mods will be loaded automatically when the game starts.

### Mod Compatibility
- Each mod's content is independent
- IDs must be unique across all mods
- If two mods use the same ID, the last loaded one wins

## Community & Support

- Report bugs or request features on GitHub
- Share your mods in the discussions section
- Help other modders in the community

Happy modding! 🎮
