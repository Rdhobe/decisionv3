"""
UI Components module for the Decision Game.
This module contains the UIComponents class for initializing all UI elements.
"""

import pygame
from frontend.ui import Button, TextBox, Label, Panel, ScrollArea

# Color constants
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

class UIComponents:
    """Manages creation and initialization of UI components for the game."""
    
    def __init__(self, game):
        """
        Initialize with a reference to the main game object.
        
        Args:
            game: The main DecisionGame instance
        """
        self.game = game
    
    def initialize_all_components(self):
        """Initialize all UI components for the game."""
        self._initialize_menu_components()
        self._initialize_login_components()
        self._initialize_scenario_components()
        self._initialize_history_components()
        self._initialize_settings_components()
        self._initialize_personality_components()
        self._initialize_simulation_components()
        self._initialize_navigation_components()
    
    def _initialize_menu_components(self):
        """Initialize UI components for the main menu."""
        center_x = self.game.width // 2
        button_width = 200
        button_height = 50
        button_spacing = 20
        first_button_y = 250
        
        # Main menu buttons
        self.game.login_button = Button(
            center_x, first_button_y, 
            button_width, button_height, 
            "Login", 
            color=PRIMARY_LIGHT, 
            hover_color=PRIMARY
        )
        
        self.game.register_button = Button(
            center_x, first_button_y + button_height + button_spacing, 
            button_width, button_height, 
            "Register", 
            color=PRIMARY_LIGHT, 
            hover_color=PRIMARY
        )
        
        self.game.guest_button = Button(
            center_x, first_button_y + 2 * (button_height + button_spacing), 
            button_width, button_height, 
            "Continue as Guest", 
            color=GRAY, 
            hover_color=DARK_GRAY
        )
        
        self.game.quit_button = Button(
            center_x, first_button_y + 3 * (button_height + button_spacing), 
            button_width, button_height, 
            "Quit", 
            color=SECONDARY, 
            hover_color=(255, 100, 50)
        )
    
    def _initialize_login_components(self):
        """Initialize UI components for the login and register screens."""
        center_x = self.game.width // 2
        
        # Login screen components
        self.game.username_box = TextBox(
            center_x, 200, 
            300, 40, 
            placeholder="Username",
            multiline=False
        )
        
        self.game.password_box = TextBox(
            center_x, 270, 
            300, 40, 
            placeholder="Password",
            multiline=False,
            is_password=True
        )
        
        self.game.login_submit_button = Button(
            center_x, 350, 
            200, 50, 
            "Login", 
            color=PRIMARY_LIGHT, 
            hover_color=PRIMARY
        )
        
        # Register screen components
        self.game.register_username_box = TextBox(
            center_x, 150, 
            300, 40, 
            placeholder="Username",
            multiline=False
        )
        
        self.game.register_email_box = TextBox(
            center_x, 210, 
            300, 40, 
            placeholder="Email",
            multiline=False
        )
        
        self.game.register_fullname_box = TextBox(
            center_x, 270, 
            300, 40, 
            placeholder="Full Name",
            multiline=False
        )
        
        self.game.register_password_box = TextBox(
            center_x, 330, 
            300, 40, 
            placeholder="Password",
            multiline=False,
            is_password=True
        )
        
        self.game.register_submit_button = Button(
            center_x, 410, 
            200, 50, 
            "Register", 
            color=PRIMARY_LIGHT, 
            hover_color=PRIMARY
        )
    
    def _initialize_scenario_components(self):
        """Initialize components for the scenario screen."""
        width, height = self.game.width, self.game.height
        center_x = width // 2
        
        # Scenario text box
        self.game.scenario_input_box = TextBox(
            center_x, height // 2 - 50, 
            width - 300, 200, 
            placeholder="Enter your decision scenario here...",
            multiline=True
        )
        
        # Create buttons with proper spacing
        # The buttons were overlapping, so we'll adjust their positions
        button_width = 180
        button_height = 50
        button_spacing = 20
        
        # Left column buttons (for registered users)
        left_x = width * 0.2  # Position at 20% of screen width
        
        # Personality button (top left)
        self.game.personality_button = Button(
            left_x, height - 130, 
            button_width, button_height, 
            "Personality Test", 
            color=PRIMARY_LIGHT
        )
        
        # History button (bottom left)
        self.game.history_button = Button(
            left_x, height - 70, 
            button_width, button_height, 
            "History", 
            color=PRIMARY_LIGHT
        )
        
        # Center buttons (for all users)
        # Let's Talk button (center bottom)
        self.game.lets_talk_button = Button(
            center_x, height - 100, 
            button_width, button_height, 
            "Let's Talk", 
            color=PRIMARY
        )
        
        # Voice button (next to Let's Talk)
        voice_button_width = 50
        self.game.voice_button = Button(
            center_x + button_width/2 + button_spacing, height - 100, 
            voice_button_width, button_height, 
            "🎤", 
            color=SECONDARY
        )
        
        # Right column buttons
        right_x = width * 0.8  # Position at 80% of screen width
        
        # Simulations button (right)
        self.game.simulation_button = Button(
            right_x, height - 100, 
            button_width, button_height, 
            "Simulations", 
            color=PRIMARY_LIGHT
        )
        
        # Settings and logout buttons (top right corner)
        settings_width = 120
        settings_height = 40
        
        # Settings button
        self.game.settings_button = Button(
            width - 90, 95, 
            settings_width, settings_height, 
            "Settings", 
            color=GRAY
        )
        
        # Logout button
        self.game.logout_button = Button(
            width - 90, 45, 
            settings_width, settings_height, 
            "Logout", 
            color=GRAY
        )
        
        # Guest user buttons
        self.game.scenario_login_button = Button(
            right_x, height - 100, 
            button_width, button_height, 
            "Login", 
            color=PRIMARY_LIGHT
        )
        
        self.game.scenario_back_button = Button(
            left_x, height - 100, 
            button_width, button_height, 
            "Back", 
            color=PRIMARY_LIGHT
        )
    
    def _initialize_history_components(self):
        """Initialize UI components for the history screen."""
        # History scroll area
        self.game.history_scroll_area = ScrollArea(
            self.game.width // 2 - 400, 150, 
            800, 400
        )
    
    def _initialize_settings_components(self):
        """Initialize UI components for the settings screen."""
        center_x = self.game.width // 2
        
        # Settings buttons
        self.game.dark_mode_button = Button(
            center_x + 100, 200, 
            100, 40, 
            "OFF",  # Default is OFF
            color=GRAY, 
            hover_color=DARK_GRAY
        )
        
        self.game.sound_button = Button(
            center_x + 100, 260, 
            100, 40, 
            "ON",  # Default is ON
            color=GRAY, 
            hover_color=DARK_GRAY
        )
    
    def _initialize_personality_components(self):
        """Initialize UI components for the personality test screen."""
        # Personality test back button
        self.game.personality_back_button = Button(
            100, 80, 120, 40, 
            "Back",
            color=GRAY,
            hover_color=DARK_GRAY
        )
        
        # Create progress label
        self.game.mbti_progress_label = Label(
            self.game.width // 2, 130,
            "Question 1 of 20", 
            color=DARK_GRAY,
            font_size=24
        )
        
        # Create option buttons
        self.game.mbti_option_buttons = []
        
        # Standard options: Strongly Agree, Agree, Neutral, Disagree, Strongly Disagree
        options = ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
        
        # Create a button for each option
        for i, option in enumerate(options):
            button = Button(
                self.game.width // 2, 280 + i * 60,
                400, 50,
                option,
                color=PRIMARY_LIGHT,
                hover_color=PRIMARY
            )
            self.game.mbti_option_buttons.append(button)
        
        # Create download personality results button
        self.game.download_personality_button = Button(
            self.game.width // 2, 520,
            250, 50,
            "Download Results",
            color=PRIMARY,
            hover_color=PRIMARY_DARK
        )
    
    def _initialize_simulation_components(self):
        """Initialize UI components for simulations."""
        center_x = self.game.width // 2
        
        # Create result panels - these will be populated dynamically
        self.game.simulation_results_panel = Panel(
            center_x, 300,
            700, 400,
            fill_color=WHITE,
            border_color=PRIMARY,
            border_width=2
        )
        
        # Create default scenario buttons - these will be replaced when scenarios are loaded
        self.game.default_scenario_buttons = []
        for i in range(3):
            y_pos = 200 + i * 100
            button = Button(
                center_x, y_pos,
                700, 60,
                f"Scenario {i+1}",
                color=PRIMARY_LIGHT,
                hover_color=PRIMARY
            )
            self.game.default_scenario_buttons.append(button)
    
    def _initialize_navigation_components(self):
        """Initialize navigation components like back buttons."""
        center_x = self.game.width // 2
        
        # Back button dimensions
        back_width = 120
        back_height = 40
        back_y = 30
        back_x = 70
        
        # Back buttons for various screens
        self.game.back_button = Button(
            back_x, back_y,
            back_width, back_height,
            "Back",
            color=GRAY,
            hover_color=DARK_GRAY
        )
        
        self.game.history_back_button = Button(
            back_x, back_y,
            back_width, back_height,
            "Back",
            color=GRAY,
            hover_color=DARK_GRAY
        )
        
        self.game.settings_back_button = Button(
            back_x, back_y,
            back_width, back_height,
            "Back",
            color=GRAY,
            hover_color=DARK_GRAY
        )
        
        self.game.personality_back_button = Button(
            back_x, back_y,
            back_width, back_height,
            "Back",
            color=GRAY,
            hover_color=DARK_GRAY
        )
        
        self.game.simulation_back_button = Button(
            back_x, back_y,
            back_width, back_height,
            "Back",
            color=GRAY,
            hover_color=DARK_GRAY
        )
        
        # Conversation navigation buttons
        self.game.next_question_button = Button(
            center_x + 150, 530,
            150, 50,
            "Next",
            color=PRIMARY_LIGHT,
            hover_color=PRIMARY,
            visible=False
        )
        
        self.game.previous_question_button = Button(
            center_x - 150, 530,
            150, 50,
            "Previous",
            color=GRAY,
            hover_color=DARK_GRAY,
            visible=False
        )
        
        self.game.finish_conversation_button = Button(
            center_x, 530,
            200, 50,
            "Finish",
            color=PRIMARY,
            hover_color=PRIMARY_DARK,
            visible=False
        )
        
        # Post-conversation buttons
        self.game.explore_more_button = Button(
            center_x - 150, 500,
            250, 50,
            "Explore Further",
            color=PRIMARY_LIGHT,
            hover_color=PRIMARY,
            visible=False
        )
        
        self.game.new_topic_button = Button(
            center_x + 150, 500,
            250, 50,
            "New Scenario",
            color=PRIMARY_LIGHT,
            hover_color=PRIMARY,
            visible=False
        )
        
        # Download report buttons
        self.game.download_conversation_button = Button(
            center_x, 550,
            250, 50,
            "Download Summary",
            color=PRIMARY_LIGHT,
            hover_color=PRIMARY,
            visible=False
        ) 