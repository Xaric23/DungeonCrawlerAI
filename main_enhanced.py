"""
DungeonCrawlerAI - Enhanced Edition Demo

A comprehensive demonstration of all new features including:
- Difficulty System (EASY to NIGHTMARE)
- Hero Archetypes (6 unique classes)
- Dungeon Themes (6 themed environments)
- Multi-Hero Mode (Race, Survival, Coop)
- Curse Synergies (Combo system)
- Progression System (Achievements, XP)
- ASCII Visualization (Map rendering)
- Dynamic Events (Random dungeon events)
"""

import sys
import time
import random

sys.stdout.reconfigure(encoding='utf-8')

from game import DungeonCrawlerGame
from dungeon import Dungeon
from models import Hero
from events import EventBus

from difficulty import Difficulty, DifficultySettings, get_difficulty_settings, DIFFICULTY_PRESETS
from hero_archetypes import HeroArchetype, ArchetypeStats, get_archetype_stats, apply_archetype_to_hero
from dungeon_themes import DungeonTheme, get_theme_config, apply_theme_to_dungeon
from multi_hero import MultiHeroGame, GameMode
from curse_synergies import SynergyTracker, ALL_SYNERGIES
from progression import PlayerProfile, get_default_achievements
from visualization import DungeonVisualizer
from dynamic_events import EventManager, DungeonEventType

try:
    from web_dashboard import run_server, FLASK_AVAILABLE
except ImportError:
    FLASK_AVAILABLE = False


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def print_subheader(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---\n")


def demo_difficulty_system() -> None:
    """
    Demonstrate the difficulty system by comparing EASY vs NIGHTMARE settings.
    Shows how difficulty affects hero stats, curse energy, and enemy damage.
    """
    print_header("DIFFICULTY SYSTEM DEMO")
    
    print("Comparing EASY vs NIGHTMARE difficulty settings:\n")
    
    difficulties = [Difficulty.EASY, Difficulty.NIGHTMARE]
    
    for diff in difficulties:
        settings = get_difficulty_settings(diff)
        print(f"╔{'═' * 40}╗")
        print(f"║ {diff.name:^38} ║")
        print(f"╠{'═' * 40}╣")
        print(f"║ Hero HP Multiplier:    {settings.hero_hp_multiplier:>14.1f} ║")
        print(f"║ Hero Attack Multiplier:{settings.hero_attack_multiplier:>14.1f} ║")
        print(f"║ Curse Energy Regen:    {settings.curse_energy_regen:>14}  ║")
        print(f"║ Suspicion Decay Rate:  {settings.suspicion_decay_rate:>14}  ║")
        print(f"║ Enemy Damage Modifier: {settings.enemy_damage_multiplier:>14.1f} ║")
        print(f"║ Trap Damage Modifier:  {settings.trap_damage_multiplier:>14.1f} ║")
        print(f"║ Starting Curse Energy: {settings.starting_curse_energy:>14}  ║")
        print(f"╚{'═' * 40}╝")
        print()
    
    print_subheader("Running Quick Simulations")
    
    for diff in [Difficulty.EASY, Difficulty.NORMAL, Difficulty.HARD, Difficulty.NIGHTMARE]:
        settings = get_difficulty_settings(diff)
        game = DungeonCrawlerGame(num_rooms=8, enable_player=True, auto_player=True)
        
        game.hero.max_health = int(100 * settings.hero_hp_multiplier)
        game.hero.health = game.hero.max_health
        game.hero.attack = int(15 * settings.hero_attack_multiplier)
        
        game.hero.current_room_id = 0
        game.hero.visited_rooms.append(0)
        
        result = game.run_simulation(max_turns=100, verbose=False)
        
        outcome = "✓ Victory" if result["victory"] else "✗ Defeat"
        print(f"  {diff.name:12} | {outcome:12} | Turns: {result['turns']:3} | HP: {result['hero_health']:3}")


def demo_hero_archetypes() -> None:
    """
    Demonstrate the hero archetype system by running games with each class.
    Shows unique stats and abilities for each archetype.
    """
    print_header("HERO ARCHETYPES DEMO")
    
    print("Available Hero Archetypes:\n")
    
    for archetype in HeroArchetype:
        stats = get_archetype_stats(archetype)
        print(f"┌─────────────────────────────────────────────────┐")
        print(f"│ {archetype.value.upper():^47} │")
        print(f"├─────────────────────────────────────────────────┤")
        print(f"│ HP: {stats.base_health:3}  ATK: {stats.base_attack:2}  DEF: {stats.base_defense:2}             │")
        print(f"│                                                 │")
        print(f"│ Special: {stats.special_ability_name:<38} │")
        print(f"│   {stats.special_ability_description:<45} │")
        print(f"│                                                 │")
        print(f"│ Passive: {stats.passive_name:<38} │")
        print(f"│   {stats.passive_description:<45} │")
        print(f"└─────────────────────────────────────────────────┘")
        print()
    
    print_subheader("Archetype Performance Comparison")
    
    results = []
    for archetype in HeroArchetype:
        game = DungeonCrawlerGame(num_rooms=8, enable_player=True, auto_player=True)
        apply_archetype_to_hero(game.hero, archetype)
        
        game.hero.current_room_id = 0
        game.hero.visited_rooms.append(0)
        
        result = game.run_simulation(max_turns=100, verbose=False)
        results.append((archetype.value, result))
    
    print(f"{'Archetype':<12} | {'Result':<10} | {'Turns':<6} | {'Final HP':<10} | {'Rooms':<6}")
    print("-" * 60)
    for name, result in results:
        outcome = "Victory" if result["victory"] else "Defeat"
        print(f"{name:<12} | {outcome:<10} | {result['turns']:<6} | {result['hero_health']:<10} | {result['rooms_visited']:<6}")


def demo_dungeon_themes() -> None:
    """
    Demonstrate the dungeon theme system showing different themed environments.
    Displays theme configuration and enemy/trap types.
    """
    print_header("DUNGEON THEMES DEMO")
    
    print("Available Dungeon Themes:\n")
    
    for theme in DungeonTheme:
        config = get_theme_config(theme)
        print(f"╔{'═' * 56}╗")
        print(f"║ {config.name:^54} ║")
        print(f"╠{'═' * 56}╣")
        print(f"║ {config.description[:54]:<54} ║")
        print(f"╠{'═' * 56}╣")
        
        enemies = ", ".join(e.value.replace("_", " ").title() for e in config.enemy_types[:3])
        print(f"║ Enemies: {enemies[:45]:<45} ║")
        
        traps = ", ".join(t.value.title() for t in config.trap_types[:3])
        print(f"║ Traps: {traps[:47]:<47} ║")
        
        print(f"║ Rooms: {config.room_count_range[0]}-{config.room_count_range[1]:<5} Enemy Mod: {config.enemy_stats_modifier:.1f}x  Trap Mod: {config.trap_damage_modifier:.1f}x ║")
        
        if config.special_mechanics:
            mechs = ", ".join(m.replace("_", " ") for m in config.special_mechanics[:2])
            print(f"║ Mechanics: {mechs[:43]:<43} ║")
        
        print(f"╚{'═' * 56}╝")
        print()
    
    print_subheader("Generating Themed Dungeons")
    
    for theme in [DungeonTheme.CLASSIC_FANTASY, DungeonTheme.VOLCANIC, DungeonTheme.ELDRITCH_HORROR]:
        config = get_theme_config(theme)
        dungeon = Dungeon(num_rooms=random.randint(*config.room_count_range))
        apply_theme_to_dungeon(dungeon, theme)
        
        enemy_count = sum(len(room.enemies) for room in dungeon.rooms.values())
        trap_count = sum(len(room.traps) for room in dungeon.rooms.values())
        
        print(f"  {config.name}: {dungeon.num_rooms} rooms, {enemy_count} enemies, {trap_count} traps")


def demo_multi_hero() -> None:
    """
    Demonstrate the multi-hero race mode with multiple AI heroes competing.
    Shows hero creation, turn execution, and ranking.
    """
    print_header("MULTI-HERO MODE DEMO")
    
    print("Game Modes Available:")
    print("  • RACE     - First hero to clear the boss room wins")
    print("  • SURVIVAL - Last hero standing wins")
    print("  • COOP     - All heroes must survive and clear the boss")
    print()
    
    print_subheader("Running Multi-Hero Race")
    
    dungeon = Dungeon(num_rooms=10)
    event_bus = EventBus()
    
    archetypes = [HeroArchetype.WARRIOR, HeroArchetype.ROGUE, HeroArchetype.MAGE]
    multi_game = MultiHeroGame(
        num_heroes=3,
        dungeon=dungeon,
        event_bus=event_bus,
        game_mode=GameMode.RACE,
        archetypes=archetypes
    )
    
    print("Heroes Created:")
    for hero, archetype in zip(multi_game.heroes, multi_game.hero_archetypes):
        print(f"  • {hero.name} ({archetype.value}) - HP: {hero.health}, ATK: {hero.attack}")
    print()
    
    for hero in multi_game.heroes:
        hero.current_room_id = 0
        hero.visited_rooms.append(0)
    
    print("Running race simulation...")
    max_turns = 50
    
    for turn in range(max_turns):
        actions = multi_game.run_all_heroes_turn()
        
        if turn % 10 == 0:
            print(f"\n  Turn {turn + 1}:")
            rankings = multi_game.get_hero_rankings()
            for i, (hero, rooms, health) in enumerate(rankings, 1):
                status = "ELIMINATED" if hero in multi_game.eliminated_heroes else "Active"
                room = hero.current_room_id if hero.current_room_id is not None else "?"
                print(f"    {i}. {hero.name}: Room {room}, HP: {health}, Rooms: {rooms} [{status}]")
        
        if multi_game.is_game_over():
            break
    
    print("\n" + "─" * 40)
    state = multi_game.get_game_state()
    print(f"Game Over at Turn {state.turn}")
    print(f"Active Heroes: {state.active_heroes}")
    if state.winner:
        print(f"Winner: {state.winner.name}")
    else:
        print("No winner - all heroes eliminated!")


def demo_curse_synergies() -> None:
    """
    Demonstrate the curse synergy/combo system.
    Shows available synergies and how to trigger them.
    """
    print_header("CURSE SYNERGIES DEMO")
    
    print("Available Curse Synergies:\n")
    
    for synergy in ALL_SYNERGIES:
        print(f"┌─────────────────────────────────────────────────────────┐")
        print(f"│ {synergy.name:^55} │")
        print(f"├─────────────────────────────────────────────────────────┤")
        print(f"│ {synergy.description[:55]:<55} │")
        print(f"│                                                         │")
        powers = " → ".join(synergy.powers_required)
        print(f"│ Powers: {powers[:47]:<47} │")
        print(f"│                                                         │")
        print(f"│ Bonus: {synergy.bonus_effect[:48]:<48} │")
        print(f"│ Energy Discount: {synergy.energy_discount}%   Suspicion: {synergy.suspicion_modifier:.1f}x           │")
        print(f"└─────────────────────────────────────────────────────────┘")
        print()
    
    print_subheader("Synergy Tracker Demo")
    
    tracker = SynergyTracker()
    
    print("Simulating power usage...")
    powers = ["corrupt_loot", "corrupt_loot", "corrupt_loot"]
    
    for power in powers:
        tracker.track_power(power)
        print(f"  Used: {power}")
        
        progress = tracker.get_progress_toward_synergies()
        for name, data in progress.items():
            if data["percentage"] > 0:
                print(f"    → {name}: {data['percentage']}% complete")
        
        triggered = tracker.check_synergies()
        if triggered:
            print(f"\n  ★ SYNERGY TRIGGERED: {triggered.name}!")
            print(f"    Bonus: {triggered.bonus_effect}")
            print()


def demo_progression() -> None:
    """
    Demonstrate the progression system with achievements and XP tracking.
    Shows profile creation, game result recording, and achievement unlocking.
    """
    print_header("PROGRESSION SYSTEM DEMO")
    
    profile = PlayerProfile("DemoPlayer")
    
    print("Player Profile Created:")
    print(f"  Username: {profile.username}")
    print(f"  Curse Level: {profile.curse_level}")
    current_xp, needed_xp = profile.get_level_progress()
    print(f"  XP Progress: {current_xp}/{needed_xp}")
    print()
    
    print("Available Achievements:")
    for achievement in profile.achievements[:5]:
        status = "✓" if achievement.unlocked else "○"
        print(f"  {status} {achievement.name}: {achievement.description}")
    print(f"  ... and {len(profile.achievements) - 5} more")
    print()
    
    print_subheader("Simulating Game Results")
    
    game_results = [
        {"victory": True, "turns": 45, "suspicion": 30, "enemies_mutated": 5,
         "items_corrupted": 8, "traps_triggered": 12, "difficulty": "normal",
         "hero_potions_used": 2, "xp_earned": 50},
        {"victory": True, "turns": 25, "suspicion": 15, "enemies_mutated": 3,
         "items_corrupted": 5, "traps_triggered": 8, "difficulty": "normal",
         "hero_potions_used": 0, "xp_earned": 75},
        {"victory": False, "turns": 60, "suspicion": 85, "enemies_mutated": 8,
         "items_corrupted": 10, "traps_triggered": 15, "difficulty": "hard",
         "hero_potions_used": 5, "xp_earned": 25},
    ]
    
    for i, result in enumerate(game_results, 1):
        new_achievements = profile.add_game_result(result)
        outcome = "Victory" if result["victory"] else "Defeat"
        print(f"Game {i}: {outcome} in {result['turns']} turns")
        
        if new_achievements:
            for ach in new_achievements:
                print(f"  ★ Achievement Unlocked: {ach.name}!")
    
    print()
    print("Updated Profile Stats:")
    print(f"  Total Games: {profile.total_games}")
    print(f"  Win Rate: {profile.get_win_rate():.1f}%")
    print(f"  Curse Level: {profile.curse_level}")
    current_xp, needed_xp = profile.get_level_progress()
    print(f"  XP Progress: {current_xp}/{needed_xp}")
    print(f"  Fastest Victory: {profile.fastest_victory_turns} turns")
    
    unlocked = sum(1 for a in profile.achievements if a.unlocked)
    print(f"  Achievements: {unlocked}/{len(profile.achievements)}")


def demo_visualization() -> None:
    """
    Demonstrate the ASCII map visualization system.
    Shows dungeon map, hero status, and room details.
    """
    print_header("ASCII VISUALIZATION DEMO")
    
    dungeon = Dungeon(num_rooms=8)
    visualizer = DungeonVisualizer(dungeon)
    
    hero = Hero("Demo Hero")
    hero.health = 75
    hero.max_health = 100
    hero.attack = 18
    hero.defense = 8
    hero.gold = 250
    hero.current_room_id = 2
    hero.visited_rooms = [0, 1, 2]
    hero.suspicion_level = 35
    
    dungeon.get_room(0).visited = True
    dungeon.get_room(1).visited = True
    dungeon.get_room(2).visited = True
    
    print("Dungeon Map:")
    print(visualizer.render_map(hero.current_room_id, show_details=True))
    
    print("\n" + "─" * 60 + "\n")
    
    print("Hero Status:")
    print(visualizer.render_hero_status(hero))
    
    print("\n" + "─" * 60 + "\n")
    
    print("Current Room Details:")
    print(visualizer.render_room_details(hero.current_room_id))


def demo_dynamic_events() -> None:
    """
    Demonstrate the dynamic events system.
    Shows event triggering and effects.
    """
    print_header("DYNAMIC EVENTS DEMO")
    
    print("Available Event Types:\n")
    
    categories = {
        "Natural Events": [DungeonEventType.COLLAPSE, DungeonEventType.FLOOD,
                          DungeonEventType.EARTHQUAKE, DungeonEventType.GAS_LEAK],
        "Supernatural Events": [DungeonEventType.GHOST_SPAWN, DungeonEventType.BLESSING,
                               DungeonEventType.CURSE_WEAKENED, DungeonEventType.SOUL_ECHO],
        "Curse Events": [DungeonEventType.CURSE_STRENGTHENED, DungeonEventType.ENERGY_SURGE,
                        DungeonEventType.VOID_RIFT],
        "Hero Events": [DungeonEventType.HERO_BLESSED, DungeonEventType.SECOND_WIND,
                       DungeonEventType.DIVINE_INTERVENTION],
    }
    
    for category, events in categories.items():
        print(f"{category}:")
        for event_type in events:
            from dynamic_events import EVENT_DEFINITIONS
            defn = EVENT_DEFINITIONS[event_type]
            print(f"  • {defn['name']} ({defn['probability']*100:.0f}% chance, {defn['duration']} turns)")
        print()
    
    print_subheader("Event Manager Simulation")
    
    event_manager = EventManager()
    dungeon = Dungeon(num_rooms=8)
    hero = Hero("Test Hero")
    hero.current_room_id = 0
    
    print("Simulating 20 turns of random events...")
    events_triggered = []
    
    for turn in range(20):
        event = event_manager.tick()
        if event:
            events_triggered.append((turn + 1, event))
    
    if events_triggered:
        print("\nEvents that occurred:")
        for turn, event in events_triggered:
            print(f"  Turn {turn}: {event.name} (Duration: {event.duration + 1} turns)")
            print(f"           {event.description}")
    else:
        print("\nNo random events occurred (normal variance)")
    
    print("\n" + "─" * 40)
    print("\nForce-triggering sample events:")
    
    sample_events = [DungeonEventType.EARTHQUAKE, DungeonEventType.ENERGY_SURGE]
    for event_type in sample_events:
        event = event_manager.trigger_event(event_type)
        print(f"\n  ★ {event.name}")
        print(f"    {event.description}")
        print(f"    Affects Hero: {event.affects_hero}, Affects Curse: {event.affects_curse}")


def demo_full_game() -> None:
    """
    Run a complete game demonstration with all features enabled.
    Shows the full gameplay loop with visualization.
    """
    print_header("FULL GAME DEMO")
    
    print("Starting enhanced game with all features...\n")
    
    print("Configuration:")
    print("  Difficulty: HARD")
    print("  Archetype: BERSERKER")
    print("  Theme: VOLCANIC")
    print("  Dungeon Size: 10 rooms")
    print()
    
    game = DungeonCrawlerGame(num_rooms=10, enable_player=True, auto_player=True)
    
    apply_archetype_to_hero(game.hero, HeroArchetype.BERSERKER)
    
    settings = get_difficulty_settings(Difficulty.HARD)
    game.hero.max_health = int(game.hero.max_health * settings.hero_hp_multiplier)
    game.hero.health = game.hero.max_health
    game.hero.attack = int(game.hero.attack * settings.hero_attack_multiplier)
    
    apply_theme_to_dungeon(game.dungeon, DungeonTheme.VOLCANIC)
    
    game.hero.current_room_id = 0
    game.hero.visited_rooms.append(0)
    game.dungeon.get_room(0).visited = True
    
    event_manager = EventManager(game.event_bus)
    synergy_tracker = SynergyTracker(game.event_bus)
    profile = PlayerProfile("FullGamePlayer")
    
    visualizer = DungeonVisualizer(game.dungeon)
    
    print("Initial State:")
    print(visualizer.render_hero_status(game.hero))
    print()
    
    print("Running game simulation...")
    print("─" * 40)
    
    checkpoint_turns = [10, 20, 30]
    
    while not game.state.game_over and game.state.turn < 100:
        game.run_turn()
        
        event = event_manager.tick()
        if event:
            print(f"\n  ⚡ EVENT: {event.name}")
        
        if game.state.turn in checkpoint_turns:
            print(f"\n  Turn {game.state.turn}: HP {game.hero.health}/{game.hero.max_health}, "
                  f"Room {game.hero.current_room_id}, Suspicion {game.hero.suspicion_level}%")
    
    print("\n" + "─" * 40)
    print("\nGame Complete!")
    print()
    
    result = game.get_results()
    outcome = "VICTORY" if result["victory"] else "DEFEAT"
    print(f"  Result: {outcome}")
    print(f"  Turns: {result['turns']}")
    print(f"  Final HP: {result['hero_health']}/{game.hero.max_health}")
    print(f"  Gold Collected: {result['gold_collected']}")
    print(f"  Rooms Visited: {result['rooms_visited']}")
    print(f"  Suspicion Level: {result['hero_suspicion']}%")
    print(f"  Player Actions: {result['player_actions']}")
    
    game_result = {
        "victory": result["victory"],
        "turns": result["turns"],
        "suspicion": result["hero_suspicion"],
        "enemies_mutated": 3,
        "items_corrupted": 5,
        "traps_triggered": result["player_actions"],
        "difficulty": "hard",
        "hero_potions_used": 2,
        "xp_earned": 50 if result["victory"] else 20
    }
    new_achievements = profile.add_game_result(game_result)
    
    if new_achievements:
        print("\n  Achievements Unlocked:")
        for ach in new_achievements:
            print(f"    ★ {ach.name}")


def run_all_demos() -> None:
    """Run all demonstration functions in sequence."""
    demos = [
        ("Difficulty System", demo_difficulty_system),
        ("Hero Archetypes", demo_hero_archetypes),
        ("Dungeon Themes", demo_dungeon_themes),
        ("Multi-Hero Mode", demo_multi_hero),
        ("Curse Synergies", demo_curse_synergies),
        ("Progression System", demo_progression),
        ("Visualization", demo_visualization),
        ("Dynamic Events", demo_dynamic_events),
        ("Full Game", demo_full_game),
    ]
    
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "  RUNNING ALL DEMOS  ".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60)
    
    for name, func in demos:
        try:
            func()
        except Exception as e:
            print(f"\n[ERROR in {name}]: {e}")
        
        print("\n" + "▓" * 60)
        print(f"  Completed: {name}")
        print("▓" * 60)
        time.sleep(0.5)
    
    print("\n" + "█" * 60)
    print("█" + " ALL DEMOS COMPLETED ".center(58) + "█")
    print("█" * 60)


def display_menu() -> None:
    """Display the interactive menu."""
    print()
    print("╔════════════════════════════════════════════╗")
    print("║     DungeonCrawlerAI - Enhanced Edition    ║")
    print("╠════════════════════════════════════════════╣")
    print("║  1. Quick Game (Normal Difficulty)         ║")
    print("║  2. Choose Difficulty                      ║")
    print("║  3. Choose Hero Archetype                  ║")
    print("║  4. Choose Dungeon Theme                   ║")
    print("║  5. Multi-Hero Mode                        ║")
    print("║  6. View Achievements                      ║")
    print("║  7. Start Web Dashboard                    ║")
    print("║  8. Run All Demos                          ║")
    print("║  0. Exit                                   ║")
    print("╚════════════════════════════════════════════╝")
    print()


def quick_game(difficulty: Difficulty = Difficulty.NORMAL,
               archetype: HeroArchetype = HeroArchetype.WARRIOR,
               theme: DungeonTheme = DungeonTheme.CLASSIC_FANTASY) -> dict:
    """
    Run a quick game with specified settings.
    
    Args:
        difficulty: The difficulty level to use.
        archetype: The hero archetype to use.
        theme: The dungeon theme to use.
    
    Returns:
        Dictionary containing game results.
    """
    print(f"\nStarting game with:")
    print(f"  Difficulty: {difficulty.name}")
    print(f"  Archetype: {archetype.value}")
    print(f"  Theme: {theme.value}")
    print()
    
    game = DungeonCrawlerGame(num_rooms=10, enable_player=True, auto_player=True)
    
    apply_archetype_to_hero(game.hero, archetype)
    settings = get_difficulty_settings(difficulty)
    game.hero.max_health = int(game.hero.max_health * settings.hero_hp_multiplier)
    game.hero.health = game.hero.max_health
    game.hero.attack = int(game.hero.attack * settings.hero_attack_multiplier)
    
    apply_theme_to_dungeon(game.dungeon, theme)
    
    game.hero.current_room_id = 0
    game.hero.visited_rooms.append(0)
    
    result = game.run_simulation(max_turns=150, verbose=True)
    return result


def choose_difficulty() -> Difficulty:
    """Interactive difficulty selection."""
    print("\nSelect Difficulty:")
    for i, diff in enumerate(Difficulty, 1):
        settings = get_difficulty_settings(diff)
        print(f"  {i}. {diff.name} (HP: {settings.hero_hp_multiplier:.1f}x, "
              f"Energy: {settings.starting_curse_energy})")
    
    try:
        choice = int(input("\nChoice (1-4): "))
        return list(Difficulty)[choice - 1]
    except (ValueError, IndexError):
        print("Invalid choice, using NORMAL")
        return Difficulty.NORMAL


def choose_archetype() -> HeroArchetype:
    """Interactive archetype selection."""
    print("\nSelect Hero Archetype:")
    for i, arch in enumerate(HeroArchetype, 1):
        stats = get_archetype_stats(arch)
        print(f"  {i}. {arch.value.upper()} (HP: {stats.base_health}, "
              f"ATK: {stats.base_attack}, DEF: {stats.base_defense})")
    
    try:
        choice = int(input("\nChoice (1-6): "))
        return list(HeroArchetype)[choice - 1]
    except (ValueError, IndexError):
        print("Invalid choice, using WARRIOR")
        return HeroArchetype.WARRIOR


def choose_theme() -> DungeonTheme:
    """Interactive theme selection."""
    print("\nSelect Dungeon Theme:")
    for i, theme in enumerate(DungeonTheme, 1):
        config = get_theme_config(theme)
        print(f"  {i}. {config.name}")
    
    try:
        choice = int(input("\nChoice (1-6): "))
        return list(DungeonTheme)[choice - 1]
    except (ValueError, IndexError):
        print("Invalid choice, using CLASSIC_FANTASY")
        return DungeonTheme.CLASSIC_FANTASY


def view_achievements() -> None:
    """Display all available achievements."""
    print_header("ACHIEVEMENTS")
    
    achievements = get_default_achievements()
    
    for ach in achievements:
        status = "✓" if ach.unlocked else "○"
        print(f"  {status} {ach.name}")
        print(f"      {ach.description}")
        print()


def start_web_dashboard() -> None:
    """Start the Flask web dashboard if available."""
    if not FLASK_AVAILABLE:
        print("\n[ERROR] Flask is not installed.")
        print("Install it with: pip install flask")
        return
    
    print("\nStarting Web Dashboard...")
    print("Open http://localhost:5000 in your browser")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        run_server(host="127.0.0.1", port=5000)
    except KeyboardInterrupt:
        print("\nWeb server stopped.")


def main() -> None:
    """Main entry point with interactive menu."""
    print("\n" + "█" * 50)
    print("█" + " " * 48 + "█")
    print("█" + "  DungeonCrawlerAI - Enhanced Edition  ".center(48) + "█")
    print("█" + "  Comprehensive Feature Demo  ".center(48) + "█")
    print("█" + " " * 48 + "█")
    print("█" * 50)
    
    while True:
        display_menu()
        
        try:
            choice = input("Enter your choice: ").strip()
        except EOFError:
            break
        
        if choice == "0":
            print("\nGoodbye!")
            break
        
        elif choice == "1":
            quick_game()
        
        elif choice == "2":
            difficulty = choose_difficulty()
            quick_game(difficulty=difficulty)
        
        elif choice == "3":
            archetype = choose_archetype()
            quick_game(archetype=archetype)
        
        elif choice == "4":
            theme = choose_theme()
            quick_game(theme=theme)
        
        elif choice == "5":
            demo_multi_hero()
        
        elif choice == "6":
            view_achievements()
        
        elif choice == "7":
            start_web_dashboard()
        
        elif choice == "8":
            run_all_demos()
        
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
