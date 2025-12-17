"""
Multi-Hero Mode for DungeonCrawlerAI.
Manages multiple AI-controlled heroes competing or cooperating in the dungeon.
"""
import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from models import Hero, RoomType
from dungeon import Dungeon
from events import EventBus, Event, EventType
from hero_ai import HeroAI
from hero_archetypes import HeroArchetype, apply_archetype_to_hero


class GameMode(Enum):
    """Available multi-hero game modes."""
    RACE = "RACE"
    SURVIVAL = "SURVIVAL"
    COOP = "COOP"


@dataclass
class MultiHeroGameState:
    """
    Tracks the state of a multi-hero game.
    
    Attributes:
        turn: Current turn number.
        active_heroes: Number of heroes still alive.
        winner: The winning hero, if any.
        game_mode: The current game mode.
    """
    turn: int
    active_heroes: int
    winner: Optional[Hero]
    game_mode: str


class MultiHeroGame:
    """
    Manages a multi-hero dungeon game with multiple AI-controlled heroes.
    
    Supports different game modes where heroes can race, survive, or cooperate.
    """
    
    def __init__(self, num_heroes: int, dungeon: Dungeon, event_bus: EventBus,
                 game_mode: GameMode = GameMode.RACE,
                 archetypes: Optional[List[HeroArchetype]] = None):
        """
        Initialize a multi-hero game.
        
        Args:
            num_heroes: Number of heroes to create.
            dungeon: The dungeon instance for the game.
            event_bus: Event bus for game events.
            game_mode: The game mode (RACE, SURVIVAL, or COOP).
            archetypes: Optional list of archetypes to assign. If None, random.
        """
        self.dungeon = dungeon
        self.event_bus = event_bus
        self.game_mode = game_mode
        self.turn = 0
        
        self.heroes: List[Hero] = []
        self.hero_ais: List[HeroAI] = []
        self.hero_archetypes: List[HeroArchetype] = []
        self.eliminated_heroes: List[Hero] = []
        
        self._create_heroes(num_heroes, archetypes)
    
    def _create_heroes(self, num_heroes: int,
                       archetypes: Optional[List[HeroArchetype]] = None) -> List[Hero]:
        """
        Create heroes with specified or random archetypes.
        
        Args:
            num_heroes: Number of heroes to create.
            archetypes: Optional list of archetypes. If None or insufficient,
                        random archetypes are assigned.
        
        Returns:
            List of created Hero instances.
        """
        available_archetypes = list(HeroArchetype)
        
        for i in range(num_heroes):
            hero = Hero(name=f"Hero_{i + 1}")
            
            if archetypes and i < len(archetypes):
                archetype = archetypes[i]
            else:
                archetype = random.choice(available_archetypes)
            
            apply_archetype_to_hero(hero, archetype)
            self.heroes.append(hero)
            self.hero_archetypes.append(archetype)
            
            hero_ai = HeroAI(hero, self.dungeon, self.event_bus)
            self.hero_ais.append(hero_ai)
        
        return self.heroes
    
    def create_heroes(self, num_heroes: int,
                      archetypes: Optional[List[HeroArchetype]] = None) -> List[Hero]:
        """
        Public method to create additional heroes.
        
        Args:
            num_heroes: Number of heroes to create.
            archetypes: Optional list of archetypes to assign.
        
        Returns:
            List of newly created Hero instances.
        """
        return self._create_heroes(num_heroes, archetypes)
    
    def run_all_heroes_turn(self) -> List[dict]:
        """
        Execute one turn for all active heroes.
        
        Returns:
            List of action dictionaries describing each hero's action.
        """
        self.turn += 1
        actions = []
        
        for i, (hero, hero_ai) in enumerate(zip(self.heroes, self.hero_ais)):
            if hero not in self.eliminated_heroes and hero.is_alive:
                previous_room = hero.current_room_id
                previous_health = hero.health
                
                status = hero_ai.tick()
                
                action = {
                    "hero": hero.name,
                    "archetype": self.hero_archetypes[i].value,
                    "turn": self.turn,
                    "status": status.name,
                    "room": hero.current_room_id,
                    "previous_room": previous_room,
                    "health": hero.health,
                    "health_change": hero.health - previous_health,
                    "is_alive": hero.is_alive,
                }
                actions.append(action)
                
                if not hero.is_alive:
                    self.eliminate_hero(hero)
        
        self._check_hero_collisions()
        
        return actions
    
    def get_leading_hero(self) -> Optional[Hero]:
        """
        Get the hero closest to the boss room.
        
        Returns:
            The hero with the highest room ID visited, or None if no active heroes.
        """
        active_heroes = [h for h in self.heroes if h not in self.eliminated_heroes and h.is_alive]
        
        if not active_heroes:
            return None
        
        boss_room_id = self.dungeon.num_rooms - 1
        
        def distance_to_boss(hero: Hero) -> int:
            if hero.current_room_id is None:
                return boss_room_id
            return boss_room_id - hero.current_room_id
        
        return min(active_heroes, key=distance_to_boss)
    
    def get_hero_rankings(self) -> List[Tuple[Hero, int, int]]:
        """
        Get heroes ranked by progress and health.
        
        Returns:
            List of tuples (hero, rooms_visited, current_health) sorted by progress.
        """
        rankings = []
        
        for hero in self.heroes:
            rooms_visited = len(hero.visited_rooms)
            rankings.append((hero, rooms_visited, hero.health))
        
        rankings.sort(key=lambda x: (-x[1], -x[2]))
        
        return rankings
    
    def check_hero_collision(self, hero1: Hero, hero2: Hero) -> bool:
        """
        Check if two heroes are in the same room.
        
        Args:
            hero1: First hero to check.
            hero2: Second hero to check.
        
        Returns:
            True if both heroes are in the same room, False otherwise.
        """
        if hero1.current_room_id is None or hero2.current_room_id is None:
            return False
        return hero1.current_room_id == hero2.current_room_id
    
    def _check_hero_collisions(self):
        """Check for and handle all hero collisions."""
        active_heroes = [h for h in self.heroes if h not in self.eliminated_heroes and h.is_alive]
        
        for i, hero1 in enumerate(active_heroes):
            for hero2 in active_heroes[i + 1:]:
                if self.check_hero_collision(hero1, hero2):
                    self.handle_hero_interaction(hero1, hero2)
    
    def handle_hero_interaction(self, hero1: Hero, hero2: Hero):
        """
        Handle interaction when two heroes meet in the same room.
        
        In RACE mode: Heroes compete for loot, faster hero gets priority.
        In SURVIVAL mode: Heroes may fight each other.
        In COOP mode: Heroes share benefits.
        
        Args:
            hero1: First hero in the interaction.
            hero2: Second hero in the interaction.
        """
        room = self.dungeon.get_room(hero1.current_room_id)
        if room is None:
            return
        
        self.event_bus.publish(Event(
            EventType.ROOM_ENTERED,
            {"interaction": "hero_collision", "hero1": hero1.name, "hero2": hero2.name, "room": room.room_id}
        ))
        
        if self.game_mode == GameMode.RACE:
            if room.items:
                faster_hero = hero1 if hero1.attack >= hero2.attack else hero2
                slower_hero = hero2 if faster_hero == hero1 else hero1
                
                if room.items:
                    item = room.items.pop(0)
                    faster_hero.add_item(item)
                    self.event_bus.publish(Event(
                        EventType.HERO_LOOTED,
                        {"hero": faster_hero.name, "item": item.name, "competed_with": slower_hero.name}
                    ))
        
        elif self.game_mode == GameMode.SURVIVAL:
            attacker = hero1 if random.random() < 0.5 else hero2
            defender = hero2 if attacker == hero1 else hero1
            
            damage = max(1, attacker.attack - defender.defense)
            defender.take_damage(damage)
            
            self.event_bus.publish(Event(
                EventType.HERO_ATTACKED,
                {"attacker": attacker.name, "defender": defender.name, "damage": damage}
            ))
            
            if not defender.is_alive:
                self.eliminate_hero(defender)
        
        elif self.game_mode == GameMode.COOP:
            if hero1.health < hero2.health:
                heal_amount = min(10, hero2.health // 4)
                hero1.heal(heal_amount)
            elif hero2.health < hero1.health:
                heal_amount = min(10, hero1.health // 4)
                hero2.heal(heal_amount)
    
    def eliminate_hero(self, hero: Hero):
        """
        Remove a hero from active play.
        
        Args:
            hero: The hero to eliminate.
        """
        if hero not in self.eliminated_heroes:
            self.eliminated_heroes.append(hero)
            self.event_bus.publish(Event(
                EventType.HERO_DIED,
                {"hero": hero.name, "room": hero.current_room_id, "turn": self.turn}
            ))
    
    def get_game_state(self) -> MultiHeroGameState:
        """
        Get the current game state.
        
        Returns:
            MultiHeroGameState with current game information.
        """
        active = len([h for h in self.heroes if h not in self.eliminated_heroes and h.is_alive])
        winner = self._determine_winner()
        
        return MultiHeroGameState(
            turn=self.turn,
            active_heroes=active,
            winner=winner,
            game_mode=self.game_mode.value
        )
    
    def _determine_winner(self) -> Optional[Hero]:
        """
        Determine if there's a winner based on game mode.
        
        Returns:
            The winning hero, or None if game is ongoing.
        """
        active_heroes = [h for h in self.heroes if h not in self.eliminated_heroes and h.is_alive]
        boss_room_id = self.dungeon.num_rooms - 1
        boss_room = self.dungeon.get_room(boss_room_id)
        
        if self.game_mode == GameMode.RACE:
            for hero in active_heroes:
                if hero.current_room_id == boss_room_id:
                    if boss_room and not boss_room.get_alive_enemies():
                        return hero
        
        elif self.game_mode == GameMode.SURVIVAL:
            if len(active_heroes) == 1:
                return active_heroes[0]
            if len(active_heroes) == 0:
                return None
        
        elif self.game_mode == GameMode.COOP:
            all_in_boss = all(h.current_room_id == boss_room_id for h in active_heroes)
            if all_in_boss and boss_room and not boss_room.get_alive_enemies():
                if len(active_heroes) == len(self.heroes):
                    return active_heroes[0]
        
        return None
    
    def is_game_over(self) -> bool:
        """
        Check if the game has ended.
        
        Returns:
            True if the game is over, False otherwise.
        """
        state = self.get_game_state()
        
        if state.winner is not None:
            return True
        
        if state.active_heroes == 0:
            return True
        
        if self.game_mode == GameMode.COOP:
            if len(self.eliminated_heroes) > 0:
                return True
        
        return False
