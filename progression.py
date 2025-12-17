"""
Progression System for DungeonCrawlerAI.

Tracks player achievements, statistics, and curse level progression.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class Achievement:
    """Represents an unlockable achievement."""
    
    id: str
    name: str
    description: str
    condition: str
    unlocked: bool = False
    unlock_date: Optional[str] = None
    
    def unlock(self) -> None:
        """Mark this achievement as unlocked."""
        if not self.unlocked:
            self.unlocked = True
            self.unlock_date = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert achievement to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "condition": self.condition,
            "unlocked": self.unlocked,
            "unlock_date": self.unlock_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Achievement":
        """Create achievement from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            condition=data["condition"],
            unlocked=data.get("unlocked", False),
            unlock_date=data.get("unlock_date")
        )


def get_default_achievements() -> List[Achievement]:
    """Return the list of all available achievements."""
    return [
        Achievement(
            id="FIRST_VICTORY",
            name="First Victory",
            description="Win your first game",
            condition="Win your first game"
        ),
        Achievement(
            id="SPEED_DEMON",
            name="Speed Demon",
            description="Win in under 30 turns",
            condition="Win in under 30 turns"
        ),
        Achievement(
            id="MASTER_MANIPULATOR",
            name="Master Manipulator",
            description="Win with hero suspicion > 80%",
            condition="Win with hero suspicion > 80%"
        ),
        Achievement(
            id="STEALTH_MASTER",
            name="Stealth Master",
            description="Win with hero suspicion < 10%",
            condition="Win with hero suspicion < 10%"
        ),
        Achievement(
            id="MUTATION_EXPERT",
            name="Mutation Expert",
            description="Mutate 10 enemies in one game",
            condition="Mutate 10 enemies in one game"
        ),
        Achievement(
            id="CORRUPTION_LORD",
            name="Corruption Lord",
            description="Corrupt 15 items in one game",
            condition="Corrupt 15 items in one game"
        ),
        Achievement(
            id="TRAP_MASTER",
            name="Trap Master",
            description="Trigger 20 traps in one game",
            condition="Trigger 20 traps in one game"
        ),
        Achievement(
            id="NIGHTMARE_CONQUEROR",
            name="Nightmare Conqueror",
            description="Win on Nightmare difficulty",
            condition="Win on Nightmare difficulty"
        ),
        Achievement(
            id="PERFECT_GAME",
            name="Perfect Game",
            description="Win without hero using any potions",
            condition="Win without hero using any potions"
        ),
    ]


class PlayerProfile:
    """
    Tracks player progression, statistics, and achievements.
    
    Attributes:
        username: Player's display name.
        total_games: Total number of games played.
        total_victories: Total number of wins.
        total_defeats: Total number of losses.
        total_turns_played: Cumulative turns across all games.
        highest_suspicion_victory: Highest hero suspicion at victory.
        fastest_victory_turns: Fewest turns to achieve victory.
        total_enemies_mutated: Cumulative enemies mutated.
        total_items_corrupted: Cumulative items corrupted.
        total_traps_triggered: Cumulative traps triggered.
        curse_level: Current curse power level.
        curse_experience: Current XP towards next level.
        achievements: List of all achievements.
        unlocked_powers: List of unlocked curse power IDs.
        unlocked_themes: List of unlocked visual theme IDs.
    """
    
    XP_PER_LEVEL = 100
    XP_SCALING = 1.5
    
    def __init__(
        self,
        username: str,
        total_games: int = 0,
        total_victories: int = 0,
        total_defeats: int = 0,
        total_turns_played: int = 0,
        highest_suspicion_victory: int = 0,
        fastest_victory_turns: int = 999,
        total_enemies_mutated: int = 0,
        total_items_corrupted: int = 0,
        total_traps_triggered: int = 0,
        curse_level: int = 1,
        curse_experience: int = 0,
        achievements: Optional[List[Achievement]] = None,
        unlocked_powers: Optional[List[str]] = None,
        unlocked_themes: Optional[List[str]] = None
    ):
        """Initialize a player profile."""
        self.username = username
        self.total_games = total_games
        self.total_victories = total_victories
        self.total_defeats = total_defeats
        self.total_turns_played = total_turns_played
        self.highest_suspicion_victory = highest_suspicion_victory
        self.fastest_victory_turns = fastest_victory_turns
        self.total_enemies_mutated = total_enemies_mutated
        self.total_items_corrupted = total_items_corrupted
        self.total_traps_triggered = total_traps_triggered
        self.curse_level = curse_level
        self.curse_experience = curse_experience
        self.achievements = achievements if achievements else get_default_achievements()
        self.unlocked_powers = unlocked_powers if unlocked_powers else []
        self.unlocked_themes = unlocked_themes if unlocked_themes else ["default"]
    
    def add_game_result(self, result: Dict[str, Any]) -> List[Achievement]:
        """
        Update statistics from a game result and return newly unlocked achievements.
        
        Args:
            result: Dictionary containing game result data with keys:
                - victory (bool): Whether the player won
                - turns (int): Number of turns played
                - suspicion (int): Hero's final suspicion level (0-100)
                - enemies_mutated (int): Enemies mutated this game
                - items_corrupted (int): Items corrupted this game
                - traps_triggered (int): Traps triggered this game
                - difficulty (str): Game difficulty
                - hero_potions_used (int): Potions the hero consumed
                - xp_earned (int): Experience points earned
        
        Returns:
            List of newly unlocked achievements.
        """
        self.total_games += 1
        self.total_turns_played += result.get("turns", 0)
        self.total_enemies_mutated += result.get("enemies_mutated", 0)
        self.total_items_corrupted += result.get("items_corrupted", 0)
        self.total_traps_triggered += result.get("traps_triggered", 0)
        
        if result.get("victory", False):
            self.total_victories += 1
            turns = result.get("turns", 999)
            suspicion = result.get("suspicion", 0)
            
            if turns < self.fastest_victory_turns:
                self.fastest_victory_turns = turns
            if suspicion > self.highest_suspicion_victory:
                self.highest_suspicion_victory = suspicion
        else:
            self.total_defeats += 1
        
        self.gain_experience(result.get("xp_earned", 10))
        
        return self.check_achievements(result)
    
    def check_achievements(self, result: Dict[str, Any]) -> List[Achievement]:
        """
        Check and unlock achievements based on game result.
        
        Args:
            result: Dictionary containing game result data.
        
        Returns:
            List of newly unlocked achievements.
        """
        newly_unlocked = []
        victory = result.get("victory", False)
        
        for achievement in self.achievements:
            if achievement.unlocked:
                continue
            
            unlocked = False
            
            if achievement.id == "FIRST_VICTORY":
                unlocked = self.total_victories >= 1
            
            elif achievement.id == "SPEED_DEMON":
                unlocked = victory and result.get("turns", 999) < 30
            
            elif achievement.id == "MASTER_MANIPULATOR":
                unlocked = victory and result.get("suspicion", 0) > 80
            
            elif achievement.id == "STEALTH_MASTER":
                unlocked = victory and result.get("suspicion", 100) < 10
            
            elif achievement.id == "MUTATION_EXPERT":
                unlocked = result.get("enemies_mutated", 0) >= 10
            
            elif achievement.id == "CORRUPTION_LORD":
                unlocked = result.get("items_corrupted", 0) >= 15
            
            elif achievement.id == "TRAP_MASTER":
                unlocked = result.get("traps_triggered", 0) >= 20
            
            elif achievement.id == "NIGHTMARE_CONQUEROR":
                unlocked = victory and result.get("difficulty", "").lower() == "nightmare"
            
            elif achievement.id == "PERFECT_GAME":
                unlocked = victory and result.get("hero_potions_used", 1) == 0
            
            if unlocked:
                achievement.unlock()
                newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def gain_experience(self, amount: int) -> None:
        """
        Add experience points and handle level ups.
        
        Args:
            amount: Amount of XP to add.
        """
        self.curse_experience += amount
        xp_needed = self._xp_for_next_level()
        
        while self.curse_experience >= xp_needed:
            self.curse_experience -= xp_needed
            self.curse_level += 1
            xp_needed = self._xp_for_next_level()
    
    def _xp_for_next_level(self) -> int:
        """Calculate XP needed for next level."""
        return int(self.XP_PER_LEVEL * (self.XP_SCALING ** (self.curse_level - 1)))
    
    def get_level_progress(self) -> tuple:
        """
        Get current level progress.
        
        Returns:
            Tuple of (current_xp, xp_needed_for_next_level).
        """
        return (self.curse_experience, self._xp_for_next_level())
    
    def get_win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.total_games == 0:
            return 0.0
        return (self.total_victories / self.total_games) * 100
    
    def get_achievement_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """Get an achievement by its ID."""
        for achievement in self.achievements:
            if achievement.id == achievement_id:
                return achievement
        return None
    
    def save_profile(self, filepath: str) -> None:
        """
        Save player profile to a JSON file.
        
        Args:
            filepath: Path to save the profile.
        """
        data = {
            "username": self.username,
            "total_games": self.total_games,
            "total_victories": self.total_victories,
            "total_defeats": self.total_defeats,
            "total_turns_played": self.total_turns_played,
            "highest_suspicion_victory": self.highest_suspicion_victory,
            "fastest_victory_turns": self.fastest_victory_turns,
            "total_enemies_mutated": self.total_enemies_mutated,
            "total_items_corrupted": self.total_items_corrupted,
            "total_traps_triggered": self.total_traps_triggered,
            "curse_level": self.curse_level,
            "curse_experience": self.curse_experience,
            "achievements": [a.to_dict() for a in self.achievements],
            "unlocked_powers": self.unlocked_powers,
            "unlocked_themes": self.unlocked_themes
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_profile(cls, filepath: str) -> "PlayerProfile":
        """
        Load a player profile from a JSON file.
        
        Args:
            filepath: Path to the profile file.
        
        Returns:
            Loaded PlayerProfile instance.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        achievements = [Achievement.from_dict(a) for a in data.get("achievements", [])]
        
        return cls(
            username=data["username"],
            total_games=data.get("total_games", 0),
            total_victories=data.get("total_victories", 0),
            total_defeats=data.get("total_defeats", 0),
            total_turns_played=data.get("total_turns_played", 0),
            highest_suspicion_victory=data.get("highest_suspicion_victory", 0),
            fastest_victory_turns=data.get("fastest_victory_turns", 999),
            total_enemies_mutated=data.get("total_enemies_mutated", 0),
            total_items_corrupted=data.get("total_items_corrupted", 0),
            total_traps_triggered=data.get("total_traps_triggered", 0),
            curse_level=data.get("curse_level", 1),
            curse_experience=data.get("curse_experience", 0),
            achievements=achievements if achievements else None,
            unlocked_powers=data.get("unlocked_powers"),
            unlocked_themes=data.get("unlocked_themes")
        )
