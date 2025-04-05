# Android compatibility
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if running on Android and initialize
try:
    import android_adapter
    android_adapter.init_android()
    android_adapter.request_android_permissions()
except ImportError:
    pass  # Not on Android or android_adapter not available

"""
Main entry point for the Decision Game.
This module initializes and starts the game.
"""

import os
import sys
import pygame
from frontend.main_game import DecisionGame

def initialize_backend():
    """Initialize any backend components needed for the game."""
    # This ensures the backend modules are accessible to the frontend
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if backend_dir not in sys.path:
        sys.path.append(backend_dir)
    
    # Initialize the database connection
    try:
        from database import init_db
        init_db()
        print("Database initialized")
    except ImportError:
        print("Running in frontend-only mode (no backend database)")
    except Exception as e:
        print(f"Database initialization error: {e}")

def main():
    """Initialize and start the game."""
    # Initialize pygame
    pygame.init()
    
    # Initialize backend components
    initialize_backend()
    
    # Create and run the game
    game = DecisionGame()
    game.run() 

if __name__ == "__main__":
    main() 