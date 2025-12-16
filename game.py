"""
Main game simulation for DungeonCrawlerAI.
Orchestrates the hero AI, player curse, and game loop.
"""
import random
from typing import Optional
from models import Hero, TrapType
from dungeon import Dungeon
from events import EventBus, Event, EventType
from hero_ai import HeroAI
from player_curse import PlayerCurse
from behavior_tree import NodeStatus


class GameState:
    """Tracks the current state of the game"""
    def __init__(self):
        self.turn = 0
        self.hero_alive = True
        self.game_over = False
        self.victory = False
        self.reason = ""


class DungeonCrawlerGame:
    """Main game controller"""
    
    def __init__(self, num_rooms: int = 10, enable_player: bool = True, auto_player: bool = False):
        """
        Initialize the game.
        
        Args:
            num_rooms: Number of rooms in the dungeon
            enable_player: Whether to enable player curse actions
            auto_player: Whether player actions are automated (for simulation)
        """
        self.event_bus = EventBus()
        self.dungeon = Dungeon(num_rooms)
        self.hero = Hero("Brave Adventurer")
        self.hero_ai = HeroAI(self.hero, self.dungeon, self.event_bus)
        self.player_curse = PlayerCurse(self.dungeon, self.event_bus) if enable_player else None
        self.state = GameState()
        self.enable_player = enable_player
        self.auto_player = auto_player
        self.max_turns = 200  # Prevent infinite loops
        
        # Subscribe to important events
        self.event_bus.subscribe(EventType.HERO_DIED, self._on_hero_died)
        self.event_bus.subscribe(EventType.ROOM_ENTERED, self._on_room_entered)
        
        # Event log for display
        self.event_log = []
    
    def _on_hero_died(self, event: Event):
        """Handle hero death"""
        self.state.hero_alive = False
        self.state.game_over = True
        self.state.reason = "Hero was defeated!"
        self.log("=== GAME OVER: Hero has fallen! ===")
    
    def _on_room_entered(self, event: Event):
        """Track room entries"""
        room_id = event.data.get("room")
        room = self.dungeon.get_room(room_id)
        
        # Check if hero reached boss room and cleared it
        if room and room.room_type.value == "boss":
            if len(room.get_alive_enemies()) == 0:
                self.state.game_over = True
                self.state.victory = True
                self.state.reason = "Hero defeated the boss!"
    
    def log(self, message: str):
        """Add message to event log"""
        self.event_log.append(f"[Turn {self.state.turn}] {message}")
    
    def run_turn(self) -> bool:
        """
        Execute one turn of the game.
        Returns True if game should continue, False if game over.
        """
        if self.state.game_over:
            return False
        
        self.state.turn += 1
        
        # Check turn limit
        if self.state.turn > self.max_turns:
            self.state.game_over = True
            self.state.reason = "Turn limit reached"
            self.log("=== GAME OVER: Turn limit reached ===")
            return False
        
        # Hero AI takes action
        status = self.hero_ai.tick()
        
        if status == NodeStatus.FAILURE and not self.hero.is_alive:
            self.event_bus.publish(Event(
                EventType.HERO_DIED,
                {"hero": self.hero.name}
            ))
            return False
        
        # Player curse regenerates energy
        if self.player_curse:
            self.player_curse.regenerate_energy(5)
            
            # Auto-player takes random actions
            if self.auto_player:
                self._auto_player_action()
        
        return not self.state.game_over
    
    def _auto_player_action(self):
        """Automatically perform player actions (for simulation)"""
        if not self.player_curse or self.hero.current_room_id is None:
            return
        
        # Random chance to take an action
        if random.random() < 0.3:  # 30% chance per turn
            available_actions = self.player_curse.get_available_actions(self.hero)
            
            if available_actions:
                # Choose a random room and action
                room_id = random.choice(list(available_actions.keys()))
                action = random.choice(available_actions[room_id])
                
                # Execute the action
                if action.startswith("trigger_trap"):
                    trap_idx = int(action.split("_")[-1])
                    self.player_curse.trigger_trap(room_id, trap_idx)
                elif action == "alter_room":
                    self.player_curse.alter_room(room_id)
                elif action.startswith("corrupt_item"):
                    item_idx = int(action.split("_")[-1])
                    self.player_curse.corrupt_loot(room_id, item_idx)
                elif action.startswith("mutate_enemy"):
                    enemy_idx = int(action.split("_")[-1])
                    self.player_curse.mutate_enemy(room_id, enemy_idx)
                elif action == "spawn_trap":
                    trap_type = random.choice(list(TrapType))
                    self.player_curse.spawn_trap(room_id, trap_type, random.randint(15, 25))
    
    def run_simulation(self, max_turns: Optional[int] = None, verbose: bool = True) -> dict:
        """
        Run the full game simulation.
        
        Args:
            max_turns: Maximum number of turns (None for default)
            verbose: Whether to print progress
        
        Returns:
            Dictionary with game results
        """
        if max_turns:
            self.max_turns = max_turns
        
        self.event_bus.publish(Event(
            EventType.GAME_STARTED,
            {"num_rooms": self.dungeon.num_rooms}
        ))
        
        if verbose:
            print(f"=== DungeonCrawlerAI Simulation Started ===")
            print(f"Dungeon: {self.dungeon.num_rooms} rooms")
            print(f"Hero: {self.hero}")
            if self.player_curse:
                print(f"Player Curse: Enabled (Auto: {self.auto_player})")
            print(f"=" * 50)
            print()
        
        # Main game loop
        while self.run_turn():
            if verbose and self.state.turn % 10 == 0:
                print(f"Turn {self.state.turn}: {self.hero}")
                if self.player_curse:
                    print(f"  {self.player_curse}")
        
        # Game ended
        self.event_bus.publish(Event(
            EventType.GAME_ENDED,
            {
                "turns": self.state.turn,
                "victory": self.state.victory,
                "reason": self.state.reason
            }
        ))
        
        if verbose:
            print()
            print(f"=" * 50)
            print(f"=== Game Over ===")
            print(f"Turns: {self.state.turn}")
            print(f"Result: {'VICTORY' if self.state.victory else 'DEFEAT'}")
            print(f"Reason: {self.state.reason}")
            print(f"Hero Final State: {self.hero}")
            if self.player_curse:
                print(f"Player Actions Taken: {self.player_curse.actions_taken}")
            print(f"Hero Suspicion Level: {self.hero.suspicion_level}%")
            print(f"=" * 50)
        
        return {
            "turns": self.state.turn,
            "victory": self.state.victory,
            "hero_alive": self.hero.is_alive,
            "hero_health": self.hero.health,
            "hero_suspicion": self.hero.suspicion_level,
            "player_actions": self.player_curse.actions_taken if self.player_curse else 0,
            "rooms_visited": len(self.hero.visited_rooms),
            "gold_collected": self.hero.gold,
            "reason": self.state.reason
        }
    
    def get_game_state_summary(self) -> str:
        """Get a summary of the current game state"""
        lines = []
        lines.append(f"Turn: {self.state.turn}")
        lines.append(f"Hero: {self.hero}")
        
        if self.hero.current_room_id is not None:
            room = self.dungeon.get_room(self.hero.current_room_id)
            if room:
                lines.append(f"Current Room: {room}")
        
        if self.player_curse:
            lines.append(f"Player: {self.player_curse}")
        
        return "\n".join(lines)
    
    def print_event_log(self, last_n: Optional[int] = None):
        """Print the event log"""
        events = self.event_log[-last_n:] if last_n else self.event_log
        for event in events:
            print(event)
