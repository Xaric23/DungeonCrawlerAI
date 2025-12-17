# Mods Directory

This directory contains mods for DungeonCrawlerAI. Mods allow you to add custom content to the game without modifying the source code.

## Quick Start

1. **Create a new folder** for your mod in this directory (e.g., `my_awesome_mod`)
2. **Create a `mod.json` file** inside your mod folder
3. **Define your custom content** using the JSON format
4. **Run the game** - your mod will be loaded automatically!

## Example Structure

```
mods/
├── example_mod/
│   └── mod.json          # Example mod included with the game
└── my_awesome_mod/
    └── mod.json          # Your custom mod
```

## Creating Your First Mod

Create a file `mods/my_first_mod/mod.json`:

```json
{
  "name": "My First Mod",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "My first custom mod",
  "enemies": [
    {
      "id": "super_goblin",
      "name": "Super Goblin",
      "type": "goblin",
      "health": 60,
      "attack": 15,
      "defense": 8,
      "description": "A more powerful goblin variant"
    }
  ],
  "items": [
    {
      "id": "magic_staff",
      "name": "Magic Staff",
      "type": "weapon",
      "value": 25,
      "description": "A staff crackling with magical energy"
    }
  ]
}
```

## What You Can Add

- **Enemies**: Custom monsters with unique stats
- **Items**: Weapons, armor, potions, and treasures
- **Traps**: Dangerous hazards with custom damage
- **Curse Powers**: Special abilities for the player (coming soon)

## Getting Help

- See **[../MODDING_GUIDE.md](../MODDING_GUIDE.md)** for complete documentation
- Check `example_mod/mod.json` for a working example
- All fields are explained in the modding guide

## Tips

✅ **DO:**
- Use descriptive IDs (e.g., `fire_demon` not `enemy1`)
- Test your mod to ensure JSON is valid
- Balance your content (not too weak or too strong)
- Add descriptions for flavor text

❌ **DON'T:**
- Use duplicate IDs (must be unique across all mods)
- Forget required fields (id, name, type, stats)
- Use invalid JSON syntax
- Make content extremely overpowered

## Community

Share your mods with the community! Consider:
- Posting on GitHub Discussions
- Creating a pull request to add to the official collection
- Helping other modders with questions

Happy Modding! 🎮
