#!/usr/bin/env python3
"""
Example use cases for DungeonCrawlerAI.
Demonstrates various features and configurations.
"""
from game import DungeonCrawlerGame
import random


def example_passive_observation():
    """Example: Watch the hero navigate without any interference"""
    print("=" * 70)
    print("EXAMPLE 1: Passive Observation")
    print("Watch the hero explore the dungeon with no player interference")
    print("=" * 70)
    print()
    
    game = DungeonCrawlerGame(num_rooms=8, enable_player=False)
    results = game.run_simulation(max_turns=80, verbose=True)
    
    print("\n--- Final Statistics ---")
    print(f"Outcome: {'VICTORY' if results['victory'] else 'DEFEAT'}")
    print(f"Survival: {'Hero survived' if results['hero_alive'] else 'Hero died'}")
    print(f"Duration: {results['turns']} turns")
    print(f"Rooms visited: {results['rooms_visited']}")
    print(f"Gold collected: {results['gold_collected']}")


def example_strategic_interference():
    """Example: Use curse powers strategically"""
    print("\n\n")
    print("=" * 70)
    print("EXAMPLE 2: Strategic Curse Usage")
    print("Player uses curse powers strategically to challenge the hero")
    print("=" * 70)
    print()
    
    game = DungeonCrawlerGame(num_rooms=10, enable_player=True, auto_player=False)
    
    # Let hero get started
    for _ in range(5):
        game.run_turn()
    
    print(f"Starting situation:")
    print(game.get_game_state_summary())
    print()
    
    # Manual curse actions
    actions_taken = []
    
    # Strategy: Focus on the current room and next rooms
    if game.hero.current_room_id is not None:
        current_room = game.hero.current_room_id
        
        # Corrupt any healing items
        room = game.dungeon.get_room(current_room)
        for i, item in enumerate(room.items):
            if item.item_type.value == "health_potion":
                if game.player_curse.corrupt_loot(current_room, i):
                    actions_taken.append("Corrupted health potion")
                    print(f"✓ Corrupted health potion in room {current_room}")
                    break
        
        # Mutate enemies in connected rooms
        for connected_id in room.connected_rooms[:2]:  # First 2 connected rooms
            connected_room = game.dungeon.get_room(connected_id)
            if connected_room and connected_room.get_alive_enemies():
                if game.player_curse.mutate_enemy(connected_id, 0):
                    actions_taken.append("Mutated enemy")
                    print(f"✓ Mutated enemy in room {connected_id}")
    
    print(f"\nActions taken: {len(actions_taken)}")
    print(f"Curse energy remaining: {game.player_curse.curse_energy}")
    print()
    
    # Continue simulation
    print("Continuing simulation...")
    turn_count = 5
    while game.run_turn() and turn_count < 60:
        turn_count += 1
        if turn_count % 15 == 0:
            print(f"Turn {turn_count}: Hero HP={game.hero.health}, Suspicion={game.hero.suspicion_level}%")
    
    results = game.get_results()  # Just get final results
    
    print("\n--- Final Statistics ---")
    print(f"Outcome: {'VICTORY' if results['victory'] else 'DEFEAT'}")
    print(f"Hero suspicion level: {results['hero_suspicion']}%")
    print(f"Curse actions used: {game.player_curse.actions_taken}")


def example_overwhelming_curse():
    """Example: Use curse powers heavily to stop the hero"""
    print("\n\n")
    print("=" * 70)
    print("EXAMPLE 3: Overwhelming Curse")
    print("Player uses maximum curse interference (hero will notice!)")
    print("=" * 70)
    print()
    
    game = DungeonCrawlerGame(num_rooms=10, enable_player=True, auto_player=True)
    
    # Modify auto-player to be more aggressive
    original_tick = game.run_turn
    
    def aggressive_turn():
        result = original_tick()
        # Player takes more actions
        if game.player_curse and random.random() < 0.6:  # 60% chance
            game._auto_player_action()
        return result
    
    game.run_turn = aggressive_turn
    
    results = game.run_simulation(max_turns=100, verbose=True)
    
    print("\n--- Final Statistics ---")
    print(f"Outcome: {'VICTORY' if results['victory'] else 'DEFEAT'}")
    print(f"Hero suspicion level: {results['hero_suspicion']}%")
    print(f"Total curse actions: {game.player_curse.actions_taken}")
    print(f"Hero adaptation: {'HIGHLY SUSPICIOUS' if results['hero_suspicion'] > 70 else 'NORMAL'}")


def example_compare_difficulties():
    """Example: Compare multiple runs with different interference levels"""
    print("\n\n")
    print("=" * 70)
    print("EXAMPLE 4: Difficulty Comparison")
    print("Running multiple simulations to compare outcomes")
    print("=" * 70)
    print()
    
    configs = [
        ("No Interference", False, False),
        ("Light Interference", True, True),
        ("Heavy Interference", True, True),
    ]
    
    results_list = []
    
    for name, enable_player, auto_player in configs:
        print(f"\nRunning: {name}...")
        
        if name == "Heavy Interference":
            # Run with more aggressive settings
            game = DungeonCrawlerGame(num_rooms=8, enable_player=True, auto_player=True)
            # Increase action frequency for heavy interference
            original_auto = game._auto_player_action
            def heavy_auto():
                original_auto()
                if random.random() < 0.3:
                    original_auto()
            game._auto_player_action = heavy_auto
        else:
            game = DungeonCrawlerGame(num_rooms=8, enable_player=enable_player, auto_player=auto_player)
        
        results = game.run_simulation(max_turns=100, verbose=False)
        results_list.append((name, results))
    
    # Print comparison table
    print("\n" + "=" * 90)
    print(f"{'Configuration':<25} {'Victory':<12} {'Turns':<10} {'Suspicion':<12} {'Gold':<10}")
    print("-" * 90)
    
    for name, results in results_list:
        victory = "✓ YES" if results["victory"] else "✗ NO"
        print(f"{name:<25} {victory:<12} {results['turns']:<10} {results['hero_suspicion']:<12} {results['gold_collected']:<10}")
    
    print("=" * 90)


def example_event_tracking():
    """Example: Track and analyze game events"""
    print("\n\n")
    print("=" * 70)
    print("EXAMPLE 5: Event Tracking and Analysis")
    print("Monitor and analyze all game events")
    print("=" * 70)
    print()
    
    game = DungeonCrawlerGame(num_rooms=6, enable_player=True, auto_player=True)
    
    # Run a short simulation
    results = game.run_simulation(max_turns=40, verbose=False)
    
    # Analyze events
    from events import EventType
    
    event_history = game.event_bus.get_history()
    
    print(f"Total events recorded: {len(event_history)}")
    print()
    
    # Count event types
    event_counts = {}
    for event in event_history:
        event_type = event.event_type.value
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
    
    print("Event breakdown:")
    for event_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {event_type}: {count}")
    
    print()
    print("--- Sample Events ---")
    
    # Show some interesting events
    combat_events = game.event_bus.get_history(EventType.HERO_ATTACKED)
    if combat_events:
        print(f"\nCombat actions: {len(combat_events)}")
        if len(combat_events) > 0:
            print(f"  First combat: {combat_events[0].data}")
    
    player_events = game.event_bus.get_history(EventType.PLAYER_ACTION)
    if player_events:
        print(f"\nPlayer interference events: {len(player_events)}")
        for event in player_events[:3]:
            print(f"  - {event.data.get('action')} in room {event.data.get('room')}")
    
    suspicion_events = game.event_bus.get_history(EventType.SUSPICION_INCREASED)
    print(f"\nSuspicion increases: {len(suspicion_events)}")
    
    print()
    print("--- Final Results ---")
    print(f"Outcome: {'VICTORY' if results['victory'] else 'DEFEAT'}")
    print(f"Hero suspicion: {results['hero_suspicion']}%")
    print(f"Player actions: {results['player_actions']}")


def main():
    """Run all examples"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║              DungeonCrawlerAI - Example Scenarios            ║
    ║                                                              ║
    ║  Demonstrating various features and use cases                ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    examples = [
        example_passive_observation,
        example_strategic_interference,
        example_overwhelming_curse,
        example_compare_difficulties,
        example_event_tracking,
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except KeyboardInterrupt:
            print(f"\n\nExample {i} interrupted by user.")
            break
        except Exception as e:
            print(f"\n\nError in example {i}: {e}")
    
    print("\n\n")
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
        sys.exit(0)
