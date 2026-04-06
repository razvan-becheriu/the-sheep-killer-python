from dataclasses import dataclass
from typing import Optional, Any
from core.state import StateManager # Import StateManager

@dataclass
class Globals:
    window: Any = None
    gl_context: Any = None
    media_manager: Any = None
    state_manager: StateManager = None # Add state_manager to Globals
    game_list: Any = None # To hold the game entities (BaseList instance)
    keystate: Any = None
    screen_width: int = 1920
    screen_height: int = 1080
    loop_running: bool = True

# Single global instance
global_vars = Globals()
