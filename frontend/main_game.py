"""
Main Game module for the Decision Game.
This module contains the main game class that orchestrates all other modules.
"""

import pygame
import sys
import threading
import time
import os
from datetime import datetime

# Import our modules
from frontend.ui import Button, TextBox, Label, Panel, ScrollArea
from frontend.screens import GameScreens
from frontend.event_handlers import GameEventHandler
from frontend.ui_components import UIComponents
from frontend.game_logic import GameLogic
from frontend.api_client import APIClient
from frontend.voice import VoiceEngine

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
YELLOW = (255, 200, 0)
PRIMARY = (75, 100, 255)
PRIMARY_LIGHT = (150, 175, 255)
PRIMARY_DARK = (50, 75, 200)
SECONDARY = (255, 150, 50)

class DecisionGame:
    """Main Game class that orchestrates all other modules."""
    
    # Game states
    MAIN_MENU = "main_menu"
    LOGIN = "login"
    REGISTER = "register"
    SCENARIO = "scenario"
    LETS_TALK = "lets_talk"
    HISTORY = "history"
    SETTINGS = "settings"
    PERSONALITY_TEST = "personality_test"
    PERSONALITY_RESULT = "personality_result"
    SIMULATION = "simulation"
    SIMULATION_RESULT = "simulation_result"
    SIMULATION_REPORT = "simulation_report"
    LOADING = "loading"  # New loading state
    
    def __init__(self, width=1000, height=600):
        """Initialize the game."""
        pygame.init()
        pygame.font.init()
        
        # Game window properties
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Decision Game")
        
        # Load fonts
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font_medium = pygame.font.SysFont("Arial", 24)
        self.font_large = pygame.font.SysFont("Arial", 32)
        self.font_title = pygame.font.SysFont("Arial", 48)
        
        # Initialize API client
        self.api_client = APIClient()
        
        # Initialize voice engine
        self.voice_engine = VoiceEngine()
        self.voice_active = False
        self.listening = False
        
        # Initial game state
        self.current_state = self.MAIN_MENU
        self.previous_state = None
        self.dark_mode = False
        self.status_message = "Welcome to Decision Game"
        self.status_color = (0, 150, 255)
        self.user = None
        self.token = None
        
        # Loading screen state
        self.is_loading = False
        self.loading_message = "Loading..."
        self.loading_target_state = None
        self.loading_progress = 0
        self.loading_start_time = 0
        self.loading_operation = None
        self.loading_completed = False
        self.loading_animation_frames = 0
        
        # User data
        self.scenario_text = ""
        self.scenario_results = {}
        self.conversation_questions = []
        self.current_question_index = 0
        self.user_responses = []
        self.conversation_complete = False
        self.conversation_summary = {}
        self.past_decisions = []
        
        # MBTI data
        self.mbti_questions = []
        self.current_mbti_index = 0
        self.mbti_answers = {}
        self.mbti_result = {}
        
        # Simulation data
        self.simulation_scenarios = []
        self.current_simulation = None
        self.simulation_results = {}
        
        # Initialize UI components
        self.ui_components = UIComponents(self)
        self.ui_components.initialize_all_components()
        
        # Initialize screens
        self.screens = GameScreens(self)
        
        # Initialize event handler
        self.event_handler = GameEventHandler(self)
        
        # Initialize game logic
        self.game_logic = GameLogic(self)
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            # Handle events
            running = self.event_handler.handle_events()
            
            # Update game state
            self.update()
            
            # Draw screen
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(60)
    
    def update(self):
        """Update game logic."""
        # Update loading progress if we're in loading state
        if self.is_loading:
            self._update_loading()
            
            # If loading is completed and we have a target state, transition immediately
            if self.loading_completed and self.loading_target_state is not None:
                # First clear loading operation to prevent hanging
                self.loading_operation = None
                # Add a small delay to show completion state
                pygame.time.delay(300)
                # Transition to target state
                print(f"Transitioning from loading state to {self.loading_target_state}")
                self.is_loading = False
                self.current_state = self.loading_target_state
                self.loading_target_state = None
        
        # Update UI elements based on current state
        if self.current_state == self.LETS_TALK:
            # TextBox doesn't have an update method, so we'll skip this
            pass
        
        # Update scrollable areas
        if self.current_state == self.HISTORY and hasattr(self, 'history_scroll_area'):
            # Calculate the content height based on the history items
            if hasattr(self, 'decision_history') and self.decision_history:
                content_height = len(self.decision_history) * 100  # Assuming each item is about 100px tall
            else:
                content_height = 100  # Default height if no history
            self.history_scroll_area.update(content_height)
        
        # Update any animations
        pass
    
    def draw(self):
        """Draw the current game screen."""
        # Clear the screen
        bg_color = (30, 30, 40) if self.dark_mode else (245, 245, 250)
        self.screen.fill(bg_color)
        
        # If in loading state, draw loading screen instead of normal UI
        if self.is_loading:
            self.screens.draw_loading_screen()
            pygame.display.flip()
            return
        
        # Draw UI elements based on the current state
        if self.current_state == self.MAIN_MENU:
            self.screens.draw_main_menu()
        elif self.current_state == self.LOGIN:
            self.screens.draw_login_screen()
        elif self.current_state == self.REGISTER:
            self.screens.draw_register_screen()
        elif self.current_state == self.SCENARIO:
            self.screens.draw_scenario_screen()
        elif self.current_state == self.LETS_TALK:
            self.screens.draw_lets_talk_screen()
        elif self.current_state == self.HISTORY:
            self.screens.draw_history_screen()
        elif self.current_state == self.SETTINGS:
            self.screens.draw_settings_screen()
        elif self.current_state == self.PERSONALITY_TEST:
            self.screens.draw_personality_test_screen()
        elif self.current_state == self.PERSONALITY_RESULT:
            self.screens.draw_personality_result_screen()
        elif self.current_state == self.SIMULATION:
            self.screens.draw_simulation_screen()
        elif self.current_state == self.SIMULATION_RESULT:
            self.screens.draw_simulation_result_screen()
        elif self.current_state == self.SIMULATION_REPORT:
            self.screens.draw_simulation_report_screen()
        
        # Draw status message at the bottom
        status_font = self.font_small
        status_text = status_font.render(self.status_message, True, self.status_color)
        status_rect = status_text.get_rect(bottomleft=(10, self.height - 10))
        self.screen.blit(status_text, status_rect)
        
        # Update the display
        pygame.display.flip()
    
    def _update_loading(self):
        """Update loading state and animation."""
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.loading_start_time
        
        # Update loading animation frame counter (30 frames per second)
        self.loading_animation_frames = int(elapsed_time / 33.3) % 8
        
        # If loading operation is active, check if it's completed
        if self.loading_operation is not None and not self.loading_completed:
            # Check if the loading thread has completed
            if not getattr(self.loading_operation, "is_alive", lambda: False)():
                self.loading_completed = True
                self.loading_progress = 100
        else:
            # No operation running or already completed
            # Animate to 100% in 2 seconds
            if elapsed_time < 2000:  # 2 seconds
                self.loading_progress = int(elapsed_time / 2000 * 100)
            else:
                self.loading_progress = 100
                # Auto-complete loading after 2.5 seconds if no operation is specified
                # or if operation is completed but stuck in loading
                if elapsed_time > 2500 and not self.loading_completed:
                    self.loading_completed = True
                elif elapsed_time > 3500:
                    # Emergency exit from loading state if we're stuck
                    print("Emergency exit from loading state - stuck in loading")
                    self.is_loading = False
                    # Return to login as default if stuck
                    if self.current_state != self.LOGIN:
                        self.current_state = self.LOGIN
    
    def start_loading(self, message, target_state=None, operation=None):
        """
        Start loading screen with specified message and target state.
        
        Args:
            message: The loading message to display
            target_state: The state to transition to after loading
            operation: Optional function to run in a separate thread during loading
        """
        self.is_loading = True
        self.loading_message = message
        self.loading_target_state = target_state
        self.loading_progress = 0
        self.loading_start_time = pygame.time.get_ticks()
        self.loading_completed = False
        
        # If an operation is provided, run it in a separate thread
        self.loading_operation = None
        if operation is not None:
            self.loading_operation = threading.Thread(target=operation)
            self.loading_operation.daemon = True
            self.loading_operation.start()
    
    def set_status(self, message, color=(255, 255, 255)):
        """Set the status message and color."""
        self.status_message = message
        self.status_color = color
    
    def toggle_dark_mode(self):
        """Toggle dark mode."""
        self.dark_mode = not self.dark_mode
        status = "enabled" if self.dark_mode else "disabled"
        self.set_status(f"Dark mode {status}", GREEN)
    
    def back_to_previous_state(self):
        """Go back to the previous state."""
        if self.previous_state:
            temp = self.current_state
            self.current_state = self.previous_state
            self.previous_state = temp
        else:
            self.current_state = self.SCENARIO
    
    def change_state(self, new_state, save_previous=True):
        """
        Change the current game state.
        
        Args:
            new_state: The new state to transition to
            save_previous: Whether to save the current state as previous_state
        """
        if save_previous:
            self.previous_state = self.current_state
        self.current_state = new_state
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within a specified width."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Test if adding this word exceeds the width
            test_line = ' '.join(current_line + [word])
            width, _ = font.size(test_line)
            
            if width <= max_width:
                current_line.append(word)
            else:
                # Current line is full, start a new line
                if current_line:  # Avoid empty lines
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def truncate_text(self, text, font, max_width, show_ellipsis=True):
        """Truncate text to fit within a specified width."""
        # Check if the text already fits
        width, _ = font.size(text)
        if width <= max_width:
            return text
        
        # Truncate the text
        ellipsis = "..." if show_ellipsis else ""
        for i in range(len(text), 0, -1):
            truncated = text[:i] + ellipsis
            width, _ = font.size(truncated)
            if width <= max_width:
                return truncated
        
        return ellipsis  # Fallback if everything fails
    
    def draw_text_with_shadow(self, text, font, pos, color, shadow_color=(0, 0, 0), shadow_offset=2):
        """Draw text with a shadow effect."""
        shadow_surface = font.render(text, True, shadow_color)
        shadow_rect = shadow_surface.get_rect(topleft=(pos[0] + shadow_offset, pos[1] + shadow_offset))
        self.screen.blit(shadow_surface, shadow_rect)
        
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(topleft=pos)
        self.screen.blit(text_surface, text_rect)
        
        return text_rect
    
    def draw_wrapped_text(self, text, font, rect, color):
        """
        Draw multiline text within a bounding rectangle.
        
        Args:
            text: The text to render
            font: The pygame font to use
            rect: The rectangle to contain the text
            color: The text color
        """
        words = text.split(' ')
        space_width = font.size(' ')[0]
        current_line = []
        y_offset = 0
        
        for word in words:
            current_line.append(word)
            text_width = sum(font.size(w)[0] for w in current_line) + space_width * (len(current_line) - 1)
            
            if text_width > rect.width:
                # Remove the last word if line is too long
                current_line.pop()
                
                # Render the current line
                if current_line:
                    line_text = ' '.join(current_line)
                    line_surface = font.render(line_text, True, color)
                    line_rect = line_surface.get_rect(topleft=(rect.x, rect.y + y_offset))
                    self.screen.blit(line_surface, line_rect)
                    y_offset += font.get_linesize()
                
                # Start a new line with the word that didn't fit
                current_line = [word]
        
        # Render the last line
        if current_line:
            line_text = ' '.join(current_line)
            line_surface = font.render(line_text, True, color)
            line_rect = line_surface.get_rect(topleft=(rect.x, rect.y + y_offset))
            self.screen.blit(line_surface, line_rect)


def main():
    """Entry point for the game."""
    game = DecisionGame()
    game.run()


if __name__ == "__main__":
    main()