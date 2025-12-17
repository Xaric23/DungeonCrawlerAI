"""
Web Dashboard for DungeonCrawlerAI.

Provides a Flask-based web interface for controlling and monitoring the game.
Includes REST API endpoints for game state, actions, and statistics.
"""

import json
from typing import Optional, Dict, Any

try:
    from flask import Flask, request, jsonify, Response
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from game import DungeonCrawlerGame
from visualization import DungeonVisualizer
from progression import PlayerProfile, get_default_achievements
from hero_archetypes import HeroArchetype, apply_archetype_to_hero
from difficulty import Difficulty, get_difficulty_settings
from models import TrapType


class GameManager:
    """
    Manages the current game instance and provides methods for game control.
    
    Attributes:
        current_game: The currently active DungeonCrawlerGame instance, or None.
        player_profile: The player's progression profile.
    """
    
    def __init__(self):
        """Initialize the GameManager with no active game."""
        self.current_game: Optional[DungeonCrawlerGame] = None
        self.player_profile = PlayerProfile("WebPlayer")
    
    def create_game(self, difficulty: str = "normal", num_rooms: int = 10, archetype: str = "warrior") -> Dict[str, Any]:
        """
        Create a new game with the specified parameters.
        
        Args:
            difficulty: Difficulty level (easy, normal, hard, nightmare).
            num_rooms: Number of rooms in the dungeon.
            archetype: Hero archetype (warrior, rogue, paladin, mage, berserker, ranger).
        
        Returns:
            Dictionary containing the initial game state.
        """
        self.current_game = DungeonCrawlerGame(
            num_rooms=num_rooms,
            enable_player=True,
            auto_player=False
        )
        
        try:
            archetype_enum = HeroArchetype(archetype.lower())
            apply_archetype_to_hero(self.current_game.hero, archetype_enum)
        except (ValueError, KeyError):
            pass
        
        try:
            difficulty_map = {
                "easy": Difficulty.EASY,
                "normal": Difficulty.NORMAL,
                "hard": Difficulty.HARD,
                "nightmare": Difficulty.NIGHTMARE
            }
            if difficulty.lower() in difficulty_map:
                diff_enum = difficulty_map[difficulty.lower()]
                settings = get_difficulty_settings(diff_enum)
                hero = self.current_game.hero
                hero.max_health = int(hero.max_health * settings.hero_hp_multiplier)
                hero.health = hero.max_health
                hero.attack = int(hero.attack * settings.hero_attack_multiplier)
                if self.current_game.player_curse:
                    self.current_game.player_curse.curse_energy = settings.starting_curse_energy
                    self.current_game.player_curse.max_curse_energy = settings.starting_curse_energy
        except (ValueError, KeyError):
            pass
        
        self.current_game.hero.current_room_id = 0
        self.current_game.hero.visited_rooms.append(0)
        self.current_game.dungeon.get_room(0).visited = True
        
        return self.get_state()
    
    def run_turn(self) -> Dict[str, Any]:
        """
        Execute one game turn.
        
        Returns:
            Dictionary containing the updated game state after the turn.
        """
        if not self.current_game:
            return {"error": "No active game. Start a new game first."}
        
        if self.current_game.state.game_over:
            return {"error": "Game is over.", "state": self.get_state()}
        
        self.current_game.run_turn()
        
        return self.get_state()
    
    def execute_action(self, action: str, room_id: int, target_idx: int = 0) -> Dict[str, Any]:
        """
        Execute a curse power action.
        
        Args:
            action: The action to perform (trigger_trap, alter_room, corrupt_loot,
                   mutate_enemy, spawn_trap).
            room_id: The room ID to target.
            target_idx: Index of the target (trap, item, or enemy).
        
        Returns:
            Dictionary containing the result and updated game state.
        """
        if not self.current_game:
            return {"error": "No active game. Start a new game first."}
        
        if not self.current_game.player_curse:
            return {"error": "Player curse is not enabled."}
        
        curse = self.current_game.player_curse
        success = False
        
        if action == "trigger_trap":
            success = curse.trigger_trap(room_id, target_idx)
        elif action == "alter_room":
            success = curse.alter_room(room_id)
        elif action == "corrupt_loot":
            success = curse.corrupt_loot(room_id, target_idx)
        elif action == "mutate_enemy":
            success = curse.mutate_enemy(room_id, target_idx)
        elif action == "spawn_trap":
            trap_type = TrapType.SPIKE
            success = curse.spawn_trap(room_id, trap_type, 20)
        else:
            return {"error": f"Unknown action: {action}"}
        
        return {
            "success": success,
            "action": action,
            "room_id": room_id,
            "target_idx": target_idx,
            "state": self.get_state()
        }
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current game state as a dictionary.
        
        Returns:
            Dictionary containing all relevant game state information.
        """
        if not self.current_game:
            return {"error": "No active game."}
        
        game = self.current_game
        hero = game.hero
        
        rooms_data = []
        for room_id, room in game.dungeon.rooms.items():
            rooms_data.append({
                "id": room_id,
                "type": room.room_type.value,
                "visited": room.visited,
                "altered": room.altered,
                "enemies": len(room.get_alive_enemies()),
                "items": len(room.items),
                "traps": len([t for t in room.traps if not t.triggered]),
                "connections": room.connected_rooms
            })
        
        curse_data = None
        available_actions = {}
        if game.player_curse:
            curse = game.player_curse
            curse_data = {
                "energy": curse.curse_energy,
                "max_energy": curse.max_curse_energy,
                "actions_taken": curse.actions_taken
            }
            available_actions = curse.get_available_actions(hero)
        
        return {
            "turn": game.state.turn,
            "game_over": game.state.game_over,
            "victory": game.state.victory,
            "reason": game.state.reason,
            "hero": {
                "name": hero.name,
                "health": hero.health,
                "max_health": hero.max_health,
                "attack": hero.attack,
                "defense": hero.defense,
                "gold": hero.gold,
                "current_room": hero.current_room_id,
                "visited_rooms": hero.visited_rooms,
                "suspicion": hero.suspicion_level,
                "inventory_count": len(hero.inventory),
                "is_alive": hero.is_alive
            },
            "curse": curse_data,
            "available_actions": available_actions,
            "rooms": rooms_data,
            "event_log": game.event_log[-20:]
        }
    
    def get_ascii_map(self) -> str:
        """
        Get the ASCII representation of the dungeon map.
        
        Returns:
            ASCII string of the dungeon map.
        """
        if not self.current_game:
            return "No active game."
        
        visualizer = DungeonVisualizer(self.current_game.dungeon)
        return visualizer.render_full_display(
            self.current_game.hero,
            self.current_game.player_curse
        )


DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DungeonCrawlerAI Dashboard</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a2e;
            color: #eee;
            margin: 0;
            padding: 20px;
        }
        h1 { color: #e94560; text-align: center; }
        .container { max-width: 1400px; margin: 0 auto; }
        .grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        .panel {
            background: #16213e;
            border: 2px solid #e94560;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .panel h2 { color: #e94560; margin-top: 0; font-size: 1.1em; }
        pre {
            background: #0f0f23;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 12px;
            line-height: 1.4;
            white-space: pre;
        }
        button {
            background: #e94560;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
            font-family: inherit;
        }
        button:hover { background: #ff6b6b; }
        button:disabled { background: #555; cursor: not-allowed; }
        .btn-secondary { background: #4a4e69; }
        .btn-secondary:hover { background: #6c757d; }
        .status-bar {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-bottom: 15px;
        }
        .stat {
            background: #0f0f23;
            padding: 8px 15px;
            border-radius: 4px;
        }
        .stat-label { color: #888; font-size: 0.8em; }
        .stat-value { color: #4ade80; font-weight: bold; }
        .hp-bar, .energy-bar {
            height: 20px;
            background: #333;
            border-radius: 4px;
            overflow: hidden;
            margin: 5px 0;
        }
        .hp-fill { height: 100%; background: #22c55e; transition: width 0.3s; }
        .energy-fill { height: 100%; background: #8b5cf6; transition: width 0.3s; }
        .event-log {
            max-height: 200px;
            overflow-y: auto;
            font-size: 11px;
        }
        .event-log div { padding: 2px 0; border-bottom: 1px solid #333; }
        .controls { display: flex; flex-wrap: wrap; gap: 5px; }
        select, input {
            background: #0f0f23;
            color: #eee;
            border: 1px solid #4a4e69;
            padding: 8px;
            border-radius: 4px;
            font-family: inherit;
        }
        .game-over { text-align: center; font-size: 1.5em; padding: 20px; }
        .victory { color: #4ade80; }
        .defeat { color: #ef4444; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏰 DungeonCrawlerAI Dashboard</h1>
        
        <div class="panel">
            <h2>New Game</h2>
            <div class="controls">
                <select id="difficulty">
                    <option value="easy">Easy</option>
                    <option value="normal" selected>Normal</option>
                    <option value="hard">Hard</option>
                    <option value="nightmare">Nightmare</option>
                </select>
                <select id="archetype">
                    <option value="warrior" selected>Warrior</option>
                    <option value="rogue">Rogue</option>
                    <option value="paladin">Paladin</option>
                    <option value="mage">Mage</option>
                    <option value="berserker">Berserker</option>
                    <option value="ranger">Ranger</option>
                </select>
                <input type="number" id="numRooms" value="10" min="5" max="20" style="width:60px">
                <span style="align-self:center">rooms</span>
                <button onclick="newGame()">Start New Game</button>
            </div>
        </div>
        
        <div id="gameArea" style="display:none;">
            <div class="status-bar">
                <div class="stat">
                    <div class="stat-label">Turn</div>
                    <div class="stat-value" id="turnNum">0</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Hero HP</div>
                    <div class="hp-bar" style="width:150px">
                        <div class="hp-fill" id="hpBar"></div>
                    </div>
                    <div class="stat-value" id="hpText">100/100</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Curse Energy</div>
                    <div class="energy-bar" style="width:150px">
                        <div class="energy-fill" id="energyBar"></div>
                    </div>
                    <div class="stat-value" id="energyText">100/100</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Suspicion</div>
                    <div class="stat-value" id="suspicion">0%</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Gold</div>
                    <div class="stat-value" id="gold">0</div>
                </div>
            </div>
            
            <div class="grid">
                <div>
                    <div class="panel">
                        <h2>Dungeon Map</h2>
                        <pre id="asciiMap">Loading...</pre>
                    </div>
                    
                    <div class="panel">
                        <h2>Game Controls</h2>
                        <button onclick="runTurn()" id="btnTurn">Run Turn</button>
                        <button onclick="runTurns(5)" class="btn-secondary">Run 5 Turns</button>
                        <button onclick="runTurns(10)" class="btn-secondary">Run 10 Turns</button>
                    </div>
                    
                    <div class="panel">
                        <h2>Curse Powers</h2>
                        <div class="controls">
                            <select id="actionRoom"></select>
                            <select id="actionType">
                                <option value="trigger_trap">Trigger Trap (5)</option>
                                <option value="alter_room">Alter Room (20)</option>
                                <option value="corrupt_loot">Corrupt Loot (15)</option>
                                <option value="mutate_enemy">Mutate Enemy (25)</option>
                                <option value="spawn_trap">Spawn Trap (15)</option>
                            </select>
                            <input type="number" id="targetIdx" value="0" min="0" style="width:50px" title="Target Index">
                            <button onclick="executeAction()">Execute</button>
                        </div>
                    </div>
                </div>
                
                <div>
                    <div class="panel">
                        <h2>Hero Status</h2>
                        <div id="heroStatus"></div>
                    </div>
                    
                    <div class="panel">
                        <h2>Event Log</h2>
                        <div class="event-log" id="eventLog"></div>
                    </div>
                </div>
            </div>
            
            <div class="panel" id="gameOverPanel" style="display:none;">
                <div class="game-over" id="gameOverText"></div>
            </div>
        </div>
    </div>
    
    <script>
        let gameState = null;
        
        async function newGame() {
            const difficulty = document.getElementById('difficulty').value;
            const archetype = document.getElementById('archetype').value;
            const numRooms = document.getElementById('numRooms').value;
            
            const resp = await fetch('/api/game/new', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({difficulty, archetype, num_rooms: parseInt(numRooms)})
            });
            gameState = await resp.json();
            document.getElementById('gameArea').style.display = 'block';
            document.getElementById('gameOverPanel').style.display = 'none';
            updateDisplay();
        }
        
        async function runTurn() {
            const resp = await fetch('/api/game/turn', {method: 'POST'});
            gameState = await resp.json();
            updateDisplay();
        }
        
        async function runTurns(n) {
            for (let i = 0; i < n && !gameState?.game_over; i++) {
                await runTurn();
                await new Promise(r => setTimeout(r, 100));
            }
        }
        
        async function executeAction() {
            const action = document.getElementById('actionType').value;
            const room_id = parseInt(document.getElementById('actionRoom').value);
            const target_idx = parseInt(document.getElementById('targetIdx').value);
            
            const resp = await fetch('/api/game/action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action, room_id, target_idx})
            });
            const result = await resp.json();
            if (result.state) gameState = result.state;
            updateDisplay();
        }
        
        async function updateDisplay() {
            if (!gameState) return;
            
            // Update stats
            document.getElementById('turnNum').textContent = gameState.turn;
            
            const hero = gameState.hero;
            const hpPct = (hero.health / hero.max_health) * 100;
            document.getElementById('hpBar').style.width = hpPct + '%';
            document.getElementById('hpText').textContent = hero.health + '/' + hero.max_health;
            document.getElementById('suspicion').textContent = hero.suspicion + '%';
            document.getElementById('gold').textContent = hero.gold;
            
            if (gameState.curse) {
                const energyPct = (gameState.curse.energy / gameState.curse.max_energy) * 100;
                document.getElementById('energyBar').style.width = energyPct + '%';
                document.getElementById('energyText').textContent = gameState.curse.energy + '/' + gameState.curse.max_energy;
            }
            
            // Update hero status
            document.getElementById('heroStatus').innerHTML = `
                <div><b>Name:</b> ${hero.name}</div>
                <div><b>Room:</b> ${hero.current_room}</div>
                <div><b>ATK:</b> ${hero.attack} | <b>DEF:</b> ${hero.defense}</div>
                <div><b>Inventory:</b> ${hero.inventory_count} items</div>
                <div><b>Visited:</b> ${hero.visited_rooms.length} rooms</div>
            `;
            
            // Update room selector
            const roomSelect = document.getElementById('actionRoom');
            roomSelect.innerHTML = gameState.rooms.map(r => 
                `<option value="${r.id}">Room ${r.id} (${r.type})</option>`
            ).join('');
            
            // Update ASCII map
            const mapResp = await fetch('/api/game/map');
            document.getElementById('asciiMap').textContent = await mapResp.text();
            
            // Update event log
            const logDiv = document.getElementById('eventLog');
            logDiv.innerHTML = gameState.event_log.slice().reverse().map(e => `<div>${e}</div>`).join('');
            
            // Check game over
            if (gameState.game_over) {
                document.getElementById('gameOverPanel').style.display = 'block';
                const cls = gameState.victory ? 'victory' : 'defeat';
                const txt = gameState.victory ? '🏆 VICTORY!' : '💀 DEFEAT';
                document.getElementById('gameOverText').innerHTML = 
                    `<span class="${cls}">${txt}</span><br>${gameState.reason}`;
                document.getElementById('btnTurn').disabled = true;
            }
        }
    </script>
</body>
</html>
'''


game_manager = GameManager()


def create_app() -> Optional["Flask"]:
    """
    Create and configure the Flask application.
    
    Returns:
        Flask application instance, or None if Flask is not available.
    """
    if not FLASK_AVAILABLE:
        return None
    
    app = Flask(__name__)
    
    def add_cors_headers(response: Response) -> Response:
        """Add CORS headers to response."""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    app.after_request(add_cors_headers)
    
    @app.route('/')
    def dashboard():
        """Main dashboard page with game state visualization."""
        return DASHBOARD_HTML
    
    @app.route('/api/game/state', methods=['GET'])
    def get_game_state():
        """Get the current game state as JSON."""
        return jsonify(game_manager.get_state())
    
    @app.route('/api/game/map', methods=['GET'])
    def get_game_map():
        """Get the ASCII dungeon map as text."""
        return Response(game_manager.get_ascii_map(), mimetype='text/plain; charset=utf-8')
    
    @app.route('/api/game/new', methods=['POST', 'OPTIONS'])
    def new_game():
        """
        Start a new game.
        
        Request JSON params:
            difficulty: str (easy, normal, hard, nightmare)
            num_rooms: int
            archetype: str (warrior, rogue, paladin, mage, berserker, ranger)
        """
        if request.method == 'OPTIONS':
            return '', 204
        
        data = request.get_json() or {}
        difficulty = data.get('difficulty', 'normal')
        num_rooms = data.get('num_rooms', 10)
        archetype = data.get('archetype', 'warrior')
        
        state = game_manager.create_game(difficulty, num_rooms, archetype)
        return jsonify(state)
    
    @app.route('/api/game/turn', methods=['POST', 'OPTIONS'])
    def execute_turn():
        """Execute one game turn."""
        if request.method == 'OPTIONS':
            return '', 204
        
        state = game_manager.run_turn()
        return jsonify(state)
    
    @app.route('/api/game/action', methods=['POST', 'OPTIONS'])
    def execute_action():
        """
        Execute a curse power action.
        
        Request JSON params:
            action: str (trigger_trap, alter_room, corrupt_loot, mutate_enemy, spawn_trap)
            room_id: int
            target_idx: int (optional, default 0)
        """
        if request.method == 'OPTIONS':
            return '', 204
        
        data = request.get_json() or {}
        action = data.get('action', '')
        room_id = data.get('room_id', 0)
        target_idx = data.get('target_idx', 0)
        
        result = game_manager.execute_action(action, room_id, target_idx)
        return jsonify(result)
    
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Get player statistics."""
        profile = game_manager.player_profile
        return jsonify({
            "username": profile.username,
            "total_games": profile.total_games,
            "total_victories": profile.total_victories,
            "total_defeats": profile.total_defeats,
            "win_rate": profile.get_win_rate(),
            "curse_level": profile.curse_level,
            "curse_experience": profile.curse_experience,
            "xp_for_next_level": profile._xp_for_next_level(),
            "total_turns_played": profile.total_turns_played,
            "fastest_victory_turns": profile.fastest_victory_turns,
            "highest_suspicion_victory": profile.highest_suspicion_victory,
            "total_enemies_mutated": profile.total_enemies_mutated,
            "total_items_corrupted": profile.total_items_corrupted,
            "total_traps_triggered": profile.total_traps_triggered
        })
    
    @app.route('/api/achievements', methods=['GET'])
    def get_achievements():
        """Get the list of achievements."""
        profile = game_manager.player_profile
        return jsonify({
            "achievements": [a.to_dict() for a in profile.achievements]
        })
    
    return app


def run_server(host: str = "0.0.0.0", port: int = 5000) -> None:
    """
    Run the Flask development server.
    
    Args:
        host: Host address to bind to.
        port: Port number to listen on.
    """
    if not FLASK_AVAILABLE:
        print("ERROR: Flask is not installed. Install it with: pip install flask")
        return
    
    app = create_app()
    if app:
        print(f"Starting DungeonCrawlerAI Web Dashboard on http://{host}:{port}")
        app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    run_server()
