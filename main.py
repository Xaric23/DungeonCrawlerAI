#!/usr/bin/env python3
"""
Main entry point for DungeonCrawlerAI.
Demonstrates the game simulation with different configurations.
"""
import sys
from game import DungeonCrawlerGame


def run_basic_simulation():
    """Run a basic simulation without player interference"""
    print("=" * 60)
    print("SCENARIO 1: Hero explores dungeon alone (no player curse)")
    print("=" * 60)
    print()
    
    game = DungeonCrawlerGame(num_rooms=10, enable_player=False)
    results = game.run_simulation(max_turns=100, verbose=True)
    
    return results


def run_with_auto_player():
    """Run simulation with automated player curse actions"""
    print("\n\n")
    print("=" * 60)
    print("SCENARIO 2: Hero vs. Automated Player Curse")
    print("=" * 60)
    print()
    
    game = DungeonCrawlerGame(num_rooms=10, enable_player=True, auto_player=True)
    results = game.run_simulation(max_turns=100, verbose=True)
    
    return results


def run_interactive_demo():
    """Run an interactive demo where player can choose actions"""
    from events import Event, EventType
    
    print("\n\n")
    print("=" * 60)
    print("SCENARIO 3: Interactive Player Curse Demo")
    print("=" * 60)
    print()
    
    game = DungeonCrawlerGame(num_rooms=8, enable_player=True, auto_player=False)
    
    # Start the game
    game.event_bus.publish(Event(
        EventType.GAME_STARTED,
        {"num_rooms": game.dungeon.num_rooms}
    ))
    
    print(f"Dungeon: {game.dungeon.num_rooms} rooms")
    print(f"Hero: {game.hero}")
    print(f"You control the dungeon as a curse!")
    print()
    
    # Run a few turns to let hero get started
    for _ in range(3):
        game.run_turn()
    
    print(game.get_game_state_summary())
    print()
    
    # Show available actions
    if game.player_curse:
        available = game.player_curse.get_available_actions(game.hero)
        print("Available curse actions:")
        for room_id, actions in available.items():
            room = game.dungeon.get_room(room_id)
            print(f"  Room {room_id} ({room.room_type.value}): {', '.join(actions)}")
    
    # Continue simulation
    print("\nContinuing simulation...")
    while game.run_turn():
        if game.state.turn % 5 == 0:
            print(f"\nTurn {game.state.turn}:")
            print(game.get_game_state_summary())
        
        if game.state.turn > 50:
            break
    
    print("\n=== Interactive Demo Complete ===")
    return game.run_simulation(max_turns=0, verbose=True)  # Just get results


def main():
    """Main function"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         DungeonCrawlerAI - Reverse Dungeon Crawler       ║
    ║                                                          ║
    ║  The hero is AI-controlled and explores autonomously.   ║
    ║  You play as the dungeon's curse, trying to stop them!  ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Run different scenarios
    results = []
    
    # Scenario 1: No player interference
    result1 = run_basic_simulation()
    results.append(("No Player", result1))
    
    # Scenario 2: Automated player curse
    result2 = run_with_auto_player()
    results.append(("Auto Player", result2))
    
    # Scenario 3: Interactive demo
    result3 = run_interactive_demo()
    results.append(("Interactive", result3))
    
    # Print comparison
    print("\n\n")
    print("=" * 60)
    print("RESULTS COMPARISON")
    print("=" * 60)
    print()
    print(f"{'Scenario':<20} {'Victory':<10} {'Turns':<8} {'Suspicion':<12} {'Gold':<8}")
    print("-" * 60)
    
    for name, result in results:
        victory = "✓ YES" if result["victory"] else "✗ NO"
        print(f"{name:<20} {victory:<10} {result['turns']:<8} {result['hero_suspicion']:<12} {result['gold_collected']:<8}")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
        sys.exit(0)
