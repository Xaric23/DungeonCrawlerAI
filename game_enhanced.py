"""
Enhanced Game Module for DungeonCrawlerAI.

Extends the base DungeonCrawlerGame with integrated support for all advanced systems:
- Difficulty settings
- Save/Load functionality
- ASCII visualization
- Advanced enemy AI
- Hero archetypes
- Advanced curse powers with synergies
- Player progression and achievements
- Dungeon themes
- Dynamic events
- Item enhancements
"""
import random
from typing import Optional, Dict, Any, List

from models import Hero, TrapType, Enemy
from dungeon import Dungeon
from events import EventBus, Event, EventType
from hero_ai import HeroAI
from behavior_tree import NodeStatus
from game import GameState, DungeonCrawlerGame

from difficulty import Difficulty, DifficultySettings, get_difficulty_settings
from save_system import SaveSystem
from visualization import DungeonVisualizer
from enemy_ai import EnemyAI, EnemyBehavior, EnemyAIContext
from hero_archetypes import HeroArchetype, apply_archetype_to_hero, get_archetype_stats
from advanced_curse_powers import AdvancedCursePowers
from progression import PlayerProfile
from curse_synergies import SynergyTracker
from dungeon_themes import DungeonTheme, apply_theme_to_dungeon, get_theme_config
from dynamic_events import EventManager, DungeonEvent
from item_enhancement import ItemEnhancer


class EnhancedDungeonCrawlerGame:
    """
    Enhanced game controller integrating all advanced systems.
    
    Provides a fully-featured dungeon crawler experience with difficulty scaling,
    themed dungeons, dynamic events, advanced AI, and progression tracking.
    
    Attributes:
        dungeon: The dungeon instance.
        hero: The hero character.
        hero_ai: AI controller for hero behavior.
        curse: Advanced curse powers system.
        state: Current game state.
        difficulty: Selected difficulty level.
        theme: Optional dungeon theme.
        visualizer: ASCII visualization renderer.
        event_manager: Dynamic event system.
        synergy_tracker: Curse synergy detector.
        item_enhancer: Item enhancement system.
        player_profile: Player progression data.
    """
    
    def __init__(
        self,
        num_rooms: int = 10,
        enable_player: bool = True,
        auto_player: bool = False,
        difficulty: Difficulty = Difficulty.NORMAL,
        hero_archetype: Optional[HeroArchetype] = None,
        theme: Optional[DungeonTheme] = None,
        enable_events: bool = True,
        player_profile: Optional[PlayerProfile] = None
    ):
        """
        Initialize the enhanced game with all integrated systems.
        
        Args:
            num_rooms: Number of rooms in the dungeon.
            enable_player: Whether player curse actions are enabled.
            auto_player: Whether player actions are automated.
            difficulty: Game difficulty level.
            hero_archetype: Optional hero class/archetype.
            theme: Optional dungeon theme for themed enemies/traps.
            enable_events: Whether dynamic events are enabled.
            player_profile: Optional player profile for progression tracking.
        """
        self.event_bus = EventBus()
        self.dungeon = Dungeon(num_rooms)
        self.hero = Hero("Brave Adventurer")
        self.state = GameState()
        self.enable_player = enable_player
        self.auto_player = auto_player
        self.max_turns = 200
        
        self.difficulty = difficulty
        self.difficulty_settings = get_difficulty_settings(difficulty)
        
        self.theme = theme
        self.enable_events = enable_events
        self.hero_archetype = hero_archetype
        
        if hero_archetype:
            apply_archetype_to_hero(self.hero, hero_archetype)
        
        self.apply_difficulty_settings()
        
        if theme:
            apply_theme_to_dungeon(self.dungeon, theme)
        
        self.hero_ai = HeroAI(self.hero, self.dungeon, self.event_bus)
        
        self.curse: Optional[AdvancedCursePowers] = None
        if enable_player:
            self.curse = AdvancedCursePowers(self.dungeon, self.event_bus)
            self.curse.curse_energy = self.difficulty_settings.starting_curse_energy
        
        self.visualizer = DungeonVisualizer(self.dungeon)
        self.event_manager = EventManager(self.event_bus) if enable_events else None
        self.synergy_tracker = SynergyTracker(self.event_bus)
        self.item_enhancer = ItemEnhancer()
        self.save_system = SaveSystem()
        
        self.player_profile = player_profile
        
        self._enemy_ais: Dict[int, List[EnemyAI]] = {}
        self._initialize_enemy_ais()
        
        self._enhance_dungeon_items()
        
        self.event_bus.subscribe(EventType.HERO_DIED, self._on_hero_died)
        self.event_bus.subscribe(EventType.ROOM_ENTERED, self._on_room_entered)
        self.event_bus.subscribe(EventType.ENEMY_DIED, self._on_enemy_died)
        self.event_bus.subscribe(EventType.PLAYER_ACTION, self._on_player_action)
        
        self.event_log: List[str] = []
        
        self._game_stats = {
            "enemies_mutated": 0,
            "items_corrupted": 0,
            "traps_triggered": 0,
            "hero_potions_used": 0,
            "synergies_triggered": 0,
            "events_occurred": 0,
        }
    
    def _initialize_enemy_ais(self) -> None:
        """Initialize AI controllers for all enemies in the dungeon."""
        for room_id, room in self.dungeon.rooms.items():
            self._enemy_ais[room_id] = []
            for enemy in room.enemies:
                behavior = self._determine_enemy_behavior(enemy, room)
                ai = EnemyAI(enemy, behavior, self.event_bus)
                self._enemy_ais[room_id].append(ai)
    
    def _determine_enemy_behavior(self, enemy: Enemy, room) -> EnemyBehavior:
        """Determine appropriate AI behavior for an enemy based on context."""
        if room.room_type.value == "boss":
            return EnemyBehavior.BOSS
        
        if enemy.enemy_type.value == "dragon":
            return EnemyBehavior.BOSS
        elif enemy.enemy_type.value == "goblin":
            return EnemyBehavior.COWARDLY
        elif enemy.enemy_type.value == "orc":
            return EnemyBehavior.AGGRESSIVE
        else:
            return random.choice([
                EnemyBehavior.AGGRESSIVE,
                EnemyBehavior.DEFENSIVE,
                EnemyBehavior.TACTICAL
            ])
    
    def _enhance_dungeon_items(self) -> None:
        """Apply random enhancements to items throughout the dungeon."""
        for room in self.dungeon.rooms.values():
            for item in room.items:
                if random.random() < 0.3:
                    enhancement = self.item_enhancer.get_random_enhancement()
                    self.item_enhancer.enhance_item(item, enhancement)
    
    def apply_difficulty_settings(self) -> None:
        """Apply difficulty modifiers to hero and game systems."""
        settings = self.difficulty_settings
        
        self.hero.max_health = int(self.hero.max_health * settings.hero_hp_multiplier)
        self.hero.health = self.hero.max_health
        self.hero.attack = int(self.hero.attack * settings.hero_attack_multiplier)
        
        for room in self.dungeon.rooms.values():
            for enemy in room.enemies:
                enemy.attack = int(enemy.attack * settings.enemy_damage_multiplier)
            for trap in room.traps:
                trap.damage = int(trap.damage * settings.trap_damage_multiplier)
    
    def _on_hero_died(self, event: Event) -> None:
        """Handle hero death event."""
        self.state.hero_alive = False
        self.state.game_over = True
        self.state.reason = "Hero was defeated!"
        self.log("=== GAME OVER: Hero has fallen! ===")
    
    def _on_room_entered(self, event: Event) -> None:
        """Handle room entry event."""
        room_id = event.data.get("room")
        self._check_boss_victory(room_id)
    
    def _on_enemy_died(self, event: Event) -> None:
        """Handle enemy death event."""
        room_id = event.data.get("room")
        self._check_boss_victory(room_id)
    
    def _on_player_action(self, event: Event) -> None:
        """Track player actions for statistics."""
        action = event.data.get("action", "")
        
        if action == "mutate_enemy":
            self._game_stats["enemies_mutated"] += 1
        elif action in ["corrupt_loot", "mass_corruption"]:
            self._game_stats["items_corrupted"] += 1
        elif action == "trigger_trap":
            self._game_stats["traps_triggered"] += 1
        elif action == "synergy_triggered":
            self._game_stats["synergies_triggered"] += 1
    
    def _check_boss_victory(self, room_id: Optional[int]) -> None:
        """Check if the boss room has been cleared for victory."""
        if room_id is None:
            return
        room = self.dungeon.get_room(room_id)
        if room and room.room_type.value == "boss":
            if len(room.get_alive_enemies()) == 0:
                self.state.game_over = True
                self.state.victory = True
                self.state.reason = "Hero defeated the boss!"
    
    def log(self, message: str) -> None:
        """Add a message to the event log."""
        self.event_log.append(f"[Turn {self.state.turn}] {message}")
    
    def save_game(self, filepath: str) -> bool:
        """
        Save the current game state to a file.
        
        Args:
            filepath: Path to the save file.
            
        Returns:
            True if save was successful, False otherwise.
        """
        game_data = {
            "turn": self.state.turn,
            "hero_data": self.save_system.serialize_hero(self.hero),
            "dungeon_data": self.save_system.serialize_dungeon(self.dungeon),
            "player_curse_data": self.save_system.serialize_curse(self.curse) if self.curse else {},
            "event_history": [],
            "difficulty": self.difficulty.value,
            "theme": self.theme.value if self.theme else None,
            "hero_archetype": self.hero_archetype.value if self.hero_archetype else None,
            "game_stats": self._game_stats.copy(),
            "game_over": self.state.game_over,
            "victory": self.state.victory,
            "reason": self.state.reason,
        }
        return self.save_system.save_game(filepath, game_data)
    
    def load_game(self, filepath: str) -> bool:
        """
        Load a game state from a file.
        
        Args:
            filepath: Path to the save file.
            
        Returns:
            True if load was successful, False otherwise.
        """
        data = self.save_system.load_game(filepath)
        if data is None:
            return False
        
        try:
            self.state.turn = data.get("turn", 0)
            self.state.game_over = data.get("game_over", False)
            self.state.victory = data.get("victory", False)
            self.state.reason = data.get("reason", "")
            
            if data.get("hero_data"):
                self.hero = self.save_system.deserialize_hero(data["hero_data"])
            
            if data.get("dungeon_data"):
                self.dungeon = self.save_system.deserialize_dungeon(
                    data["dungeon_data"], self.event_bus
                )
                self.visualizer = DungeonVisualizer(self.dungeon)
            
            if data.get("player_curse_data") and self.enable_player:
                self.curse = self.save_system.deserialize_curse(
                    data["player_curse_data"], self.dungeon, self.event_bus
                )
            
            if data.get("game_stats"):
                self._game_stats.update(data["game_stats"])
            
            self.hero_ai = HeroAI(self.hero, self.dungeon, self.event_bus)
            self._initialize_enemy_ais()
            
            return True
        except Exception as e:
            print(f"Error restoring game state: {e}")
            return False
    
    def get_visual_display(self) -> str:
        """
        Get the full ASCII visualization of the current game state.
        
        Returns:
            Complete ASCII display including map, hero status, and curse status.
        """
        return self.visualizer.render_full_display(self.hero, self.curse)
    
    def run_enhanced_turn(self) -> bool:
        """
        Execute one turn with all enhanced systems active.
        
        Includes dynamic events, enemy AI, synergy checking, and curse effects.
        
        Returns:
            True if game should continue, False if game over.
        """
        if self.state.game_over:
            return False
        
        if self.state.turn >= self.max_turns:
            self.state.game_over = True
            self.state.reason = "Turn limit reached"
            self.log("=== GAME OVER: Turn limit reached ===")
            return False
        
        self.state.turn += 1
        
        if self.event_manager and self.enable_events:
            triggered_event = self.event_manager.tick()
            if triggered_event:
                self._game_stats["events_occurred"] += 1
                self.log(f"EVENT: {triggered_event.name} - {triggered_event.description}")
                self.event_manager.apply_event_effects(
                    triggered_event, self.hero, self.curse, self.dungeon
                )
        
        if self.curse and self.curse.is_hero_frozen():
            self.log("Hero is frozen and cannot act!")
        else:
            status = self.hero_ai.tick()
            
            if status == NodeStatus.FAILURE and not self.hero.is_alive:
                self.event_bus.publish(Event(
                    EventType.HERO_DIED,
                    {"hero": self.hero.name}
                ))
                return False
        
        if self.hero.current_room_id is not None:
            self._run_enemy_ai_turn()
        
        if self.curse:
            regen = self.difficulty_settings.curse_energy_regen
            if self.event_manager:
                modifiers = self.event_manager.get_active_modifiers()
                regen = int(regen * modifiers.get("curse_energy_regen_modifier", 1.0))
            self.curse.regenerate_energy(regen)
            self.curse.advance_turn()
            
            if self.auto_player:
                self._auto_player_action()
        
        synergy = self.synergy_tracker.check_synergies()
        if synergy and self.curse:
            self.log(f"SYNERGY: {synergy.name} triggered!")
            self.synergy_tracker.apply_synergy_bonus(synergy, self.curse)
        
        if self.difficulty_settings.suspicion_decay_rate > 0:
            self.hero.suspicion_level = max(
                0, 
                self.hero.suspicion_level - self.difficulty_settings.suspicion_decay_rate
            )
        
        return not self.state.game_over
    
    def _run_enemy_ai_turn(self) -> None:
        """Execute AI for all enemies in the hero's current room."""
        room_id = self.hero.current_room_id
        if room_id is None:
            return
        
        room = self.dungeon.get_room(room_id)
        if room is None:
            return
        
        if room_id not in self._enemy_ais:
            return
        
        alive_enemies = room.get_alive_enemies()
        
        for ai in self._enemy_ais[room_id]:
            if not ai.enemy.is_alive:
                continue
            
            if self.curse and self.curse.is_enemy_charmed(room_id, room.enemies.index(ai.enemy)):
                continue
            
            context = EnemyAIContext(
                enemy=ai.enemy,
                room=room,
                hero=self.hero,
                event_bus=self.event_bus,
                nearby_allies=[e for e in alive_enemies if e != ai.enemy]
            )
            ai.tick(context)
    
    def _auto_player_action(self) -> None:
        """Automatically perform curse actions for simulation."""
        if not self.curse or self.hero.current_room_id is None:
            return
        
        if random.random() < 0.3:
            room_ids = list(self.dungeon.rooms.keys())
            if not room_ids:
                return
            
            room_id = random.choice(room_ids)
            room = self.dungeon.get_room(room_id)
            if not room:
                return
            
            actions = []
            if room.traps and self.curse.is_power_available("trigger_trap"):
                actions.append("trigger_trap")
            if not room.altered and self.curse.is_power_available("alter_room"):
                actions.append("alter_room")
            if room.items and self.curse.is_power_available("corrupt_loot"):
                actions.append("corrupt_loot")
            if room.enemies and self.curse.is_power_available("mutate_enemy"):
                actions.append("mutate_enemy")
            if self.curse.is_power_available("spawn_trap"):
                actions.append("spawn_trap")
            
            if actions:
                action = random.choice(actions)
                self._execute_auto_action(action, room_id, room)
    
    def _execute_auto_action(self, action: str, room_id: int, room) -> None:
        """Execute a specific auto action."""
        if action == "trigger_trap" and room.traps:
            self.curse.trigger_trap(room_id, 0)
            self.synergy_tracker.track_power("trigger_trap")
        elif action == "alter_room":
            self.curse.alter_room(room_id)
            self.synergy_tracker.track_power("alter_room")
        elif action == "corrupt_loot" and room.items:
            self.curse.corrupt_loot(room_id, 0)
            self.synergy_tracker.track_power("corrupt_loot")
        elif action == "mutate_enemy" and room.enemies:
            for i, enemy in enumerate(room.enemies):
                if enemy.is_alive and not enemy.is_mutated:
                    self.curse.mutate_enemy(room_id, i)
                    self.synergy_tracker.track_power("mutate_enemy")
                    break
        elif action == "spawn_trap":
            trap_type = random.choice(list(TrapType))
            self.curse.spawn_trap(room_id, trap_type, random.randint(15, 25))
            self.synergy_tracker.track_power("spawn_trap")
    
    def run_simulation(self, max_turns: Optional[int] = None, verbose: bool = True) -> dict:
        """
        Run the full game simulation with enhanced systems.
        
        Args:
            max_turns: Maximum number of turns (None for default).
            verbose: Whether to print progress.
            
        Returns:
            Dictionary with game results and statistics.
        """
        if max_turns:
            self.max_turns = max_turns
        
        self.event_bus.publish(Event(
            EventType.GAME_STARTED,
            {"num_rooms": self.dungeon.num_rooms}
        ))
        
        if verbose:
            print(f"=== Enhanced DungeonCrawlerAI Simulation ===")
            print(f"Difficulty: {self.difficulty.name}")
            print(f"Dungeon: {self.dungeon.num_rooms} rooms")
            if self.theme:
                print(f"Theme: {get_theme_config(self.theme).name}")
            if self.hero_archetype:
                print(f"Hero Archetype: {self.hero_archetype.value.title()}")
            print(f"Hero: {self.hero}")
            if self.curse:
                print(f"Curse Powers: Enabled (Auto: {self.auto_player})")
            print(f"Dynamic Events: {'Enabled' if self.enable_events else 'Disabled'}")
            print("=" * 50)
            print()
        
        while self.run_enhanced_turn():
            if verbose and self.state.turn % 10 == 0:
                print(f"Turn {self.state.turn}: {self.hero}")
                if self.curse:
                    print(f"  {self.curse}")
                if self.event_manager and self.event_manager.active_events:
                    print(f"  Active Events: {[e.name for e in self.event_manager.active_events]}")
        
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
            print("=" * 50)
            print("=== Game Over ===")
            print(f"Turns: {self.state.turn}")
            print(f"Result: {'VICTORY' if self.state.victory else 'DEFEAT'}")
            print(f"Reason: {self.state.reason}")
            print(f"Hero Final State: {self.hero}")
            if self.curse:
                print(f"Curse Actions Taken: {self.curse.actions_taken}")
            print(f"Synergies Triggered: {self._game_stats['synergies_triggered']}")
            print(f"Events Occurred: {self._game_stats['events_occurred']}")
            print("=" * 50)
        
        results = self.get_results()
        
        if self.player_profile:
            profile_result = {
                "victory": self.state.victory,
                "turns": self.state.turn,
                "suspicion": self.hero.suspicion_level,
                "enemies_mutated": self._game_stats["enemies_mutated"],
                "items_corrupted": self._game_stats["items_corrupted"],
                "traps_triggered": self._game_stats["traps_triggered"],
                "difficulty": self.difficulty.name,
                "hero_potions_used": self._game_stats["hero_potions_used"],
                "xp_earned": self._calculate_xp_earned(),
            }
            achievements = self.player_profile.add_game_result(profile_result)
            results["new_achievements"] = [a.name for a in achievements]
        
        return results
    
    def _calculate_xp_earned(self) -> int:
        """Calculate XP earned based on game performance."""
        xp = 10
        if self.state.victory:
            xp += 50
        xp += self.state.turn // 5
        xp += self._game_stats["synergies_triggered"] * 10
        
        difficulty_multipliers = {
            Difficulty.EASY: 0.5,
            Difficulty.NORMAL: 1.0,
            Difficulty.HARD: 1.5,
            Difficulty.NIGHTMARE: 2.0,
        }
        xp = int(xp * difficulty_multipliers.get(self.difficulty, 1.0))
        return xp
    
    def get_results(self) -> dict:
        """
        Get current game results without running simulation.
        
        Returns:
            Dictionary containing comprehensive game state and statistics.
        """
        return {
            "turns": self.state.turn,
            "victory": self.state.victory,
            "hero_alive": self.hero.is_alive,
            "hero_health": self.hero.health,
            "hero_suspicion": self.hero.suspicion_level,
            "player_actions": self.curse.actions_taken if self.curse else 0,
            "rooms_visited": len(self.hero.visited_rooms),
            "gold_collected": self.hero.gold,
            "reason": self.state.reason,
            "difficulty": self.difficulty.name,
            "theme": self.theme.value if self.theme else None,
            "archetype": self.hero_archetype.value if self.hero_archetype else None,
            "game_stats": self._game_stats.copy(),
            "synergy_stats": self.synergy_tracker.get_synergy_stats(),
        }
    
    def get_game_state_summary(self) -> str:
        """
        Get a text summary of the current game state.
        
        Returns:
            Multi-line string summarizing the game state.
        """
        lines = [
            f"Turn: {self.state.turn}",
            f"Difficulty: {self.difficulty.name}",
            f"Hero: {self.hero}",
        ]
        
        if self.hero.current_room_id is not None:
            room = self.dungeon.get_room(self.hero.current_room_id)
            if room:
                lines.append(f"Current Room: {room}")
        
        if self.curse:
            lines.append(f"Curse: {self.curse}")
        
        if self.event_manager and self.event_manager.active_events:
            events = ", ".join(e.name for e in self.event_manager.active_events)
            lines.append(f"Active Events: {events}")
        
        progress = self.synergy_tracker.get_progress_toward_synergies()
        active_progress = [
            f"{name}: {info['percentage']}%"
            for name, info in progress.items()
            if info['percentage'] > 0
        ]
        if active_progress:
            lines.append(f"Synergy Progress: {', '.join(active_progress)}")
        
        return "\n".join(lines)
    
    def print_event_log(self, last_n: Optional[int] = None) -> None:
        """
        Print the event log to console.
        
        Args:
            last_n: Only print the last N events (None for all).
        """
        events = self.event_log[-last_n:] if last_n else self.event_log
        for event in events:
            print(event)
