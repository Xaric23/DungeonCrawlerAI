"""
ASCII Map Visualization for DungeonCrawlerAI.
Provides visual representation of the dungeon, hero status, and curse energy.

Example output:
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │ [E] 0   │─────│ [N] 1   │─────│ [N] 2   │
    │  @      │     │ E:2 I:1 │     │ T:1     │
    │ ✓       │     │         │     │         │
    └─────────┘     └─────────┘     └─────────┘
                          │
                    ┌─────────┐
                    │ [T] 3   │
                    │ E:2 I:4 │
                    │         │
                    └─────────┘

    Hero: Adventurer    HP: ████████░░ 80/100
    Curse Energy:       CE: ██████████ 100/100
"""
from typing import Optional, List, Dict, Tuple
from models import Room, RoomType, Hero, Item, Enemy, Trap
from dungeon import Dungeon


class DungeonVisualizer:
    """
    Renders ASCII visualization of the dungeon and game state.
    
    Provides methods to display:
    - Full dungeon map with room connections
    - Hero position and status
    - Curse energy levels
    - Room details including enemies, items, and traps
    """
    
    ROOM_TYPE_SYMBOLS = {
        RoomType.ENTRANCE: "E",
        RoomType.NORMAL: "N",
        RoomType.TREASURE: "T",
        RoomType.BOSS: "B",
        RoomType.TRAP: "X",
    }
    
    ROOM_WIDTH = 11
    ROOM_HEIGHT = 5
    
    def __init__(self, dungeon: Dungeon):
        """
        Initialize the visualizer with a dungeon.
        
        Args:
            dungeon: The Dungeon instance to visualize
        """
        self.dungeon = dungeon
    
    def render_map(self, hero_room_id: Optional[int] = None, show_details: bool = True) -> str:
        """
        Creates an ASCII representation of the dungeon map.
        
        Args:
            hero_room_id: Room ID where the hero is located (marked with @)
            show_details: If True, show enemy/item/trap counts in rooms
            
        Returns:
            ASCII string representation of the dungeon map
            
        Example:
            ┌─────────┐     ┌─────────┐
            │ [E] 0 @ │─────│ [N] 1   │
            │ E:0 I:0 │     │ E:2 I:1 │
            │ ✓       │     │         │
            └─────────┘     └─────────┘
        """
        lines = []
        lines.append("=" * 60)
        lines.append("                    DUNGEON MAP")
        lines.append("=" * 60)
        lines.append("")
        
        rooms_per_row = 4
        room_ids = sorted(self.dungeon.rooms.keys())
        
        for row_start in range(0, len(room_ids), rooms_per_row):
            row_rooms = room_ids[row_start:row_start + rooms_per_row]
            lines.extend(self._render_room_row(row_rooms, hero_room_id, show_details))
            
            if row_start + rooms_per_row < len(room_ids):
                lines.append(self._render_vertical_connections(row_rooms, room_ids[row_start + rooms_per_row:row_start + 2 * rooms_per_row]))
            
            lines.append("")
        
        lines.append("")
        lines.append("Legend: [E]=Entrance [N]=Normal [T]=Treasure [B]=Boss [X]=Trap")
        lines.append("        @ =Hero  ✓=Visited  E:n=Enemies  I:n=Items  T:n=Traps")
        
        return "\n".join(lines)
    
    def _render_room_row(self, room_ids: List[int], hero_room_id: Optional[int], show_details: bool) -> List[str]:
        """Render a row of rooms."""
        top_lines = []
        mid1_lines = []
        mid2_lines = []
        mid3_lines = []
        bot_lines = []
        
        for i, room_id in enumerate(room_ids):
            room = self.dungeon.get_room(room_id)
            if not room:
                continue
            
            is_hero_here = room_id == hero_room_id
            room_symbol = self.ROOM_TYPE_SYMBOLS.get(room.room_type, "?")
            hero_marker = " @" if is_hero_here else "  "
            visited_marker = "✓" if room.visited else " "
            altered_marker = "*" if room.altered else " "
            
            top_lines.append("┌─────────┐")
            mid1_lines.append(f"│ [{room_symbol}] {room_id:<2}{hero_marker}│")
            
            if show_details:
                enemies = len(room.get_alive_enemies())
                items = len(room.items)
                traps = len([t for t in room.traps if not t.triggered])
                mid2_lines.append(f"│E:{enemies:<1} I:{items:<1} T:{traps:<1}│")
            else:
                mid2_lines.append("│         │")
            
            mid3_lines.append(f"│ {visited_marker}     {altered_marker} │")
            bot_lines.append("└─────────┘")
            
            if i < len(room_ids) - 1:
                next_room_id = room_ids[i + 1]
                if next_room_id in room.connected_rooms:
                    top_lines.append("     ")
                    mid1_lines.append("─────")
                    mid2_lines.append("     ")
                    mid3_lines.append("     ")
                    bot_lines.append("     ")
                else:
                    top_lines.append("     ")
                    mid1_lines.append("     ")
                    mid2_lines.append("     ")
                    mid3_lines.append("     ")
                    bot_lines.append("     ")
        
        return [
            "".join(top_lines),
            "".join(mid1_lines),
            "".join(mid2_lines),
            "".join(mid3_lines),
            "".join(bot_lines),
        ]
    
    def _render_vertical_connections(self, upper_rooms: List[int], lower_rooms: List[int]) -> str:
        """Render vertical connections between room rows."""
        connections = []
        room_spacing = self.ROOM_WIDTH + 5
        
        for i, room_id in enumerate(upper_rooms):
            room = self.dungeon.get_room(room_id)
            if not room:
                connections.append(" " * room_spacing)
                continue
            
            has_down_connection = False
            for lower_id in lower_rooms:
                if lower_id in room.connected_rooms:
                    has_down_connection = True
                    break
            
            if has_down_connection:
                padding = " " * 5
                connections.append(padding + "│" + " " * (room_spacing - 6))
            else:
                connections.append(" " * room_spacing)
        
        return "".join(connections)
    
    def render_room_details(self, room_id: int) -> str:
        """
        Shows detailed information about a specific room.
        
        Args:
            room_id: The ID of the room to display
            
        Returns:
            Detailed ASCII representation of the room contents
            
        Example:
            ╔══════════════════════════════════════╗
            ║ Room 3 - TREASURE                    ║
            ╠══════════════════════════════════════╣
            ║ Status: Visited, Altered             ║
            ╠══════════════════════════════════════╣
            ║ Enemies (2):                         ║
            ║   • Orc (HP: 50/50, ATK: 12)        ║
            ║   • Skeleton (HP: 40/40, ATK: 10)   ║
            ╠══════════════════════════════════════╣
            ║ Items (3):                           ║
            ║   • Gold Coins (value: 100)         ║
            ║   • Health Potion (value: 30)       ║
            ╠══════════════════════════════════════╣
            ║ Traps (1):                           ║
            ║   • Spike Trap (dmg: 15) [ARMED]    ║
            ╠══════════════════════════════════════╣
            ║ Connections: 2, 4, 5                 ║
            ╚══════════════════════════════════════╝
        """
        room = self.dungeon.get_room(room_id)
        if not room:
            return f"Room {room_id} not found."
        
        width = 42
        lines = []
        
        lines.append("╔" + "═" * width + "╗")
        room_type = room.room_type.value.upper()
        title = f" Room {room_id} - {room_type}"
        lines.append("║" + title.ljust(width) + "║")
        lines.append("╠" + "═" * width + "╣")
        
        status_parts = []
        if room.visited:
            status_parts.append("Visited")
        else:
            status_parts.append("Unvisited")
        if room.altered:
            status_parts.append("Altered")
        status = " Status: " + ", ".join(status_parts)
        lines.append("║" + status.ljust(width) + "║")
        
        lines.append("╠" + "═" * width + "╣")
        alive_enemies = room.get_alive_enemies()
        lines.append("║" + f" Enemies ({len(alive_enemies)}):".ljust(width) + "║")
        if alive_enemies:
            for enemy in alive_enemies:
                mutation = " [MUTATED]" if enemy.is_mutated else ""
                enemy_line = f"   • {enemy.name} (HP:{enemy.health}/{enemy.max_health}, ATK:{enemy.attack}){mutation}"
                lines.append("║" + enemy_line[:width].ljust(width) + "║")
        else:
            lines.append("║" + "   (none)".ljust(width) + "║")
        
        lines.append("╠" + "═" * width + "╣")
        lines.append("║" + f" Items ({len(room.items)}):".ljust(width) + "║")
        if room.items:
            for item in room.items:
                quality = f" [{item.quality.value}]" if item.quality.value != "normal" else ""
                item_line = f"   • {item.name} (value: {item.value}){quality}"
                lines.append("║" + item_line[:width].ljust(width) + "║")
        else:
            lines.append("║" + "   (none)".ljust(width) + "║")
        
        lines.append("╠" + "═" * width + "╣")
        lines.append("║" + f" Traps ({len(room.traps)}):".ljust(width) + "║")
        if room.traps:
            for trap in room.traps:
                status = "TRIGGERED" if trap.triggered else "ARMED"
                trap_line = f"   • {trap.trap_type.value.title()} (dmg: {trap.damage}) [{status}]"
                lines.append("║" + trap_line[:width].ljust(width) + "║")
        else:
            lines.append("║" + "   (none)".ljust(width) + "║")
        
        lines.append("╠" + "═" * width + "╣")
        connections = ", ".join(str(c) for c in sorted(room.connected_rooms))
        lines.append("║" + f" Connections: {connections}".ljust(width) + "║")
        
        lines.append("╚" + "═" * width + "╝")
        
        return "\n".join(lines)
    
    def render_hero_status(self, hero: Hero) -> str:
        """
        Shows hero health bar and stats.
        
        Args:
            hero: The Hero instance to display
            
        Returns:
            ASCII representation of hero status with health bar
            
        Example:
            ┌──────────────────────────────────────┐
            │ HERO: Adventurer                     │
            ├──────────────────────────────────────┤
            │ HP:  ████████░░░░░░░░░░░░  40/100   │
            │ ATK: 15    DEF: 5    GOLD: 150      │
            │ Room: 3    Suspicion: ██░░░ 25%     │
            │ Inventory: 3 items                   │
            └──────────────────────────────────────┘
        """
        width = 42
        lines = []
        
        lines.append("┌" + "─" * width + "┐")
        lines.append("│" + f" HERO: {hero.name}".ljust(width) + "│")
        lines.append("├" + "─" * width + "┤")
        
        hp_bar = self._create_progress_bar(hero.health, hero.max_health, 20)
        hp_line = f" HP:  {hp_bar}  {hero.health}/{hero.max_health}"
        lines.append("│" + hp_line.ljust(width) + "│")
        
        stats_line = f" ATK: {hero.attack:<4} DEF: {hero.defense:<4} GOLD: {hero.gold}"
        lines.append("│" + stats_line.ljust(width) + "│")
        
        suspicion_bar = self._create_progress_bar(hero.suspicion_level, 100, 5)
        room_str = str(hero.current_room_id) if hero.current_room_id is not None else "?"
        status_line = f" Room: {room_str:<3}  Suspicion: {suspicion_bar} {hero.suspicion_level}%"
        lines.append("│" + status_line.ljust(width) + "│")
        
        inv_line = f" Inventory: {len(hero.inventory)} items"
        lines.append("│" + inv_line.ljust(width) + "│")
        
        lines.append("└" + "─" * width + "┘")
        
        return "\n".join(lines)
    
    def render_curse_status(self, curse) -> str:
        """
        Shows curse energy bar and available actions.
        
        Args:
            curse: The PlayerCurse instance to display
            
        Returns:
            ASCII representation of curse status with energy bar
            
        Example:
            ┌──────────────────────────────────────┐
            │ CURSE POWERS                         │
            ├──────────────────────────────────────┤
            │ Energy: ██████████████░░░░░░  70/100│
            │ Actions taken: 5                     │
            └──────────────────────────────────────┘
        """
        width = 42
        lines = []
        
        lines.append("┌" + "─" * width + "┐")
        lines.append("│" + " CURSE POWERS".ljust(width) + "│")
        lines.append("├" + "─" * width + "┤")
        
        energy_bar = self._create_progress_bar(curse.curse_energy, curse.max_curse_energy, 20)
        energy_line = f" Energy: {energy_bar}  {curse.curse_energy}/{curse.max_curse_energy}"
        lines.append("│" + energy_line.ljust(width) + "│")
        
        actions_line = f" Actions taken: {curse.actions_taken}"
        lines.append("│" + actions_line.ljust(width) + "│")
        
        lines.append("├" + "─" * width + "┤")
        lines.append("│" + " Ability Costs:".ljust(width) + "│")
        lines.append("│" + "   Trigger Trap: 5   Corrupt Loot: 15".ljust(width) + "│")
        lines.append("│" + "   Alter Room: 20    Mutate Enemy: 25".ljust(width) + "│")
        lines.append("│" + "   Spawn Trap: 15".ljust(width) + "│")
        
        lines.append("└" + "─" * width + "┘")
        
        return "\n".join(lines)
    
    def render_full_display(self, hero: Hero, curse=None) -> str:
        """
        Renders the complete game display with map, hero status, and curse status.
        
        Args:
            hero: The Hero instance
            curse: Optional PlayerCurse instance
            
        Returns:
            Complete ASCII game display
            
        Example:
            ============================================================
                                DUNGEON MAP
            ============================================================
            
            ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
            │ [E] 0   │─────│ [N] 1   │─────│ [N] 2 @ │─────│ [T] 3   │
            │E:0 I:0 T:0│     │E:2 I:1 T:0│     │E:0 I:0 T:1│     │E:2 I:4 T:0│
            │ ✓       │     │ ✓       │     │ ✓       │     │         │
            └─────────┘     └─────────┘     └─────────┘     └─────────┘

            ┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐
            │ HERO: Adventurer                     │  │ CURSE POWERS                         │
            │ HP:  ████████░░░░░░░░░░░░  40/100   │  │ Energy: ██████████████░░░░░░  70/100│
            └──────────────────────────────────────┘  └──────────────────────────────────────┘
        """
        lines = []
        
        lines.append(self.render_map(hero.current_room_id, show_details=True))
        lines.append("")
        lines.append("─" * 60)
        lines.append("")
        
        lines.append(self.render_hero_status(hero))
        lines.append("")
        
        if curse is not None:
            lines.append(self.render_curse_status(curse))
            lines.append("")
        
        if hero.current_room_id is not None:
            lines.append("─" * 60)
            lines.append(" CURRENT ROOM DETAILS:")
            lines.append("─" * 60)
            lines.append(self.render_room_details(hero.current_room_id))
        
        return "\n".join(lines)
    
    def _create_progress_bar(self, current: int, maximum: int, width: int = 10) -> str:
        """
        Creates an ASCII progress bar.
        
        Args:
            current: Current value
            maximum: Maximum value
            width: Width of the bar in characters
            
        Returns:
            ASCII progress bar string like "████████░░"
        """
        if maximum <= 0:
            return "░" * width
        
        ratio = max(0, min(1, current / maximum))
        filled = int(ratio * width)
        empty = width - filled
        
        return "█" * filled + "░" * empty


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    from dungeon import Dungeon
    from models import Hero
    
    dungeon = Dungeon(num_rooms=8)
    visualizer = DungeonVisualizer(dungeon)
    
    hero = Hero("Brave Knight")
    hero.current_room_id = 0
    hero.visited_rooms = [0]
    dungeon.get_room(0).visited = True
    
    print(visualizer.render_full_display(hero))
