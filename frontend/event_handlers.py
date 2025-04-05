"""
Event handlers module for the Decision Game.
This module contains the GameEventHandler class that handles user input and events.
"""

import pygame
import sys
import pymongo
import hashlib
from bson import ObjectId
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

class GameEventHandler:
    """Handles user input and events for the game."""
    
    def __init__(self, game):
        """
        Initialize with a reference to the main game object.
        
        Args:
            game: The main DecisionGame instance
        """
        self.game = game
    
    def handle_events(self):
        """
        Handle all pygame events and return whether the game should continue running.
        
        Returns:
            True if game should continue, False if it should quit
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            # Handle text input for TextBox widgets
            if event.type == pygame.KEYDOWN:
                self._handle_text_input(event)
                
                # Additional handling for history search box
                if self.game.current_state == self.game.HISTORY and hasattr(self.game, 'history_search_box'):
                    if self.game.history_search_box.active:
                        if event.key == pygame.K_RETURN:
                            self.handle_history_search()
                        elif event.key == pygame.K_ESCAPE:
                            self.game.history_search_box.set_text("")
                
            # Handle mouse motion for hover effects
            if event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)
                
            # Handle mouse events
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._handle_mouse_click(mouse_pos)
                
        return True
    
    def _handle_text_input(self, event):
        """Handle keyboard input based on current state."""
        # Handle text input for the active TextBox
        if self.game.current_state == self.game.LOGIN:
            self.game.username_box.handle_event(event)
            self.game.password_box.handle_event(event)
            
            # Handle Enter key for login
            if event.key == pygame.K_RETURN:
                self._handle_login_button_click(event.pos)
        
        elif self.game.current_state == self.game.REGISTER:
            self.game.register_username_box.handle_event(event)
            self.game.register_password_box.handle_event(event)
            self.game.register_email_box.handle_event(event)
            self.game.register_fullname_box.handle_event(event)
            
            # Handle Enter key for registration
            if event.key == pygame.K_RETURN:
                self._handle_register_button_click(event.pos)
        
        elif self.game.current_state == self.game.SCENARIO:
            self.game.scenario_input_box.handle_event(event)
            
            # Handle Enter key for scenario submission
            if event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_CTRL):
                self._analyze_scenario()
        
        elif self.game.current_state == self.game.LETS_TALK:
            if hasattr(self.game, 'response_input'):
                self.game.response_input.handle_event(event)
                
                # Handle Enter key for response submission
                if event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_CTRL):
                    self._submit_response()
    
    def _handle_mouse_motion(self, pos):
        """Handle mouse motion events for hover effects."""
        # Update button hover states based on current screen
        if self.game.current_state == self.game.MAIN_MENU:
            if hasattr(self.game, 'start_button'):
                self.game.start_button.update(pos)
            if hasattr(self.game, 'login_menu_button'):
                self.game.login_menu_button.update(pos)
            if hasattr(self.game, 'register_menu_button'):
                self.game.register_menu_button.update(pos)
                
        elif self.game.current_state == self.game.SCENARIO:
            if hasattr(self.game, 'analyze_button'):
                self.game.analyze_button.update(pos)
                
        # Add hover updates for other screens as needed
    
    def _handle_mouse_click(self, pos):
        """Handle mouse click events."""
        # Dispatch to the appropriate handler based on current state
        if self.game.current_state == self.game.MAIN_MENU:
            self._handle_main_menu_click(pos)
            
        elif self.game.current_state == self.game.LOGIN:
            self._handle_login_button_click(pos)
            
        elif self.game.current_state == self.game.REGISTER:
            self._handle_register_button_click(pos)
            
        elif self.game.current_state == self.game.SCENARIO:
            self._handle_scenario_click(pos)
            
        elif self.game.current_state == self.game.LETS_TALK:
            self._handle_conversation_click(pos)
            
        elif self.game.current_state == self.game.HISTORY:
            self._handle_history_screen_click(pos)
            
        elif self.game.current_state == self.game.SETTINGS:
            self._handle_settings_click(pos)
            
        elif self.game.current_state == self.game.PERSONALITY_TEST:
            self._handle_personality_test_click(pos)
            
        elif self.game.current_state == self.game.PERSONALITY_RESULT:
            self._handle_personality_result_click(pos)
            
        elif self.game.current_state == self.game.SIMULATION:
            self._handle_simulation_click(pos)
            
        elif self.game.current_state == self.game.SIMULATION_RESULT:
            self._handle_simulation_result_click(pos)
            
        elif self.game.current_state == self.game.SIMULATION_REPORT:
            self._handle_simulation_report_click(pos)
    
    def _handle_main_menu_click(self, mouse_pos):
        """Handle clicks on the main menu screen."""
        if self.game.login_button.is_clicked(mouse_pos):
            self.game.current_state = self.game.LOGIN
            self.game.set_status("Please log in")
        
        elif self.game.register_button.is_clicked(mouse_pos):
            self.game.current_state = self.game.REGISTER
            self.game.set_status("Create a new account")
        
        elif self.game.guest_button.is_clicked(mouse_pos):
            self.game.user = "Guest"
            self.game.current_state = self.game.SCENARIO
            self.game.set_status("Logged in as Guest. Limited features available.", YELLOW)
        
        elif self.game.quit_button.is_clicked(mouse_pos):
            pygame.quit()
            sys.exit()
    
    def _handle_login_button_click(self, mouse_pos):
        """Handle login button click."""
        # Make sure mouse events are handled for input fields
        self.game.username_box.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': mouse_pos}))
        self.game.password_box.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': mouse_pos}))
        
        # Handle login button click - fix the button name to match UI components
        if hasattr(self.game, 'login_submit_button') and self.game.login_submit_button.is_clicked(mouse_pos):
            username = self.game.username_box.get_text()
            password = self.game.password_box.get_text()
            
            if not username or not password:
                self.game.set_status("Please enter username and password", (255, 150, 0))
                return
                
            # For testing without database, allow test login
            if username == "test" and password == "test":
                print("Test login accepted")
                self.game.user = "Test User"
                self.game.token = "test_token_123"
                self.game.current_state = self.game.SCENARIO
                self.game.set_status("Welcome, Test User!", (0, 255, 0))
                return
                
            # Start loading screen for login
            self.game.start_loading(
                message="Logging in...",
                target_state=self.game.SCENARIO,  # Only transition to SCENARIO on success
                operation=lambda: self._perform_login(username, password)
            )
        
        # Handle back button click
        elif hasattr(self.game, 'back_button') and self.game.back_button.is_clicked(mouse_pos):
            self.game.current_state = self.game.MAIN_MENU
            self.game.set_status("Welcome to Decision Game")
    
    def _perform_login(self, username, password):
        """Perform login in a separate thread for the loading screen."""
        # Login via API client
        print(f"Attempting login for user: {username}")
        try:
            result = self.game.api_client.login(username, password)
            
            if "access_token" in result:
                # Login successful
                print(f"Login successful for user: {username}")
                self.game.user = username
                self.game.token = result["access_token"]
                # Set the token in the API client
                self.game.api_client.set_token(result["access_token"])
                self.game.set_status(f"Welcome, {username}!", (0, 255, 0))
                # Keep the target state as SCENARIO for successful login
            else:
                # Login failed, set error message
                error_msg = result.get("error", "Invalid username or password")
                print(f"Login failed: {error_msg}")
                self.game.set_status(f"Login failed: {error_msg}", (255, 0, 0))
                # For failed login, explicitly set target state to LOGIN
                self.game.loading_target_state = self.game.LOGIN
                # Force loading to complete
                self.game.loading_completed = True
        except Exception as e:
            print(f"Exception during login: {str(e)}")
            self.game.set_status(f"Login error: {str(e)}", (255, 0, 0))
            # For login error, explicitly set target state to LOGIN
            self.game.loading_target_state = self.game.LOGIN
            self.game.loading_completed = True
    
    def _handle_register_button_click(self, mouse_pos):
        """Handle register button click."""
        # Make sure mouse events are handled for input fields
        self.game.register_username_box.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': mouse_pos}))
        self.game.register_password_box.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': mouse_pos}))
        self.game.register_email_box.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': mouse_pos}))
        self.game.register_fullname_box.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': mouse_pos}))
        
        # Handle register button click - fix the button name to match UI components
        if hasattr(self.game, 'register_submit_button') and self.game.register_submit_button.is_clicked(mouse_pos):
            # Get registration fields
            username = self.game.register_username_box.get_text()
            email = self.game.register_email_box.get_text()
            password = self.game.register_password_box.get_text()
            fullname = self.game.register_fullname_box.get_text()
            
            # Validate fields
            if not username or not email or not password or not fullname:
                self.game.set_status("Please fill in all fields", (255, 150, 0))
                return
            
            # For testing without a database
            if username.lower() == "test":
                print("Creating test account")
                test_user = {
                    "_id": "test_id_123",
                    "username": username,
                    "email": email,
                    "fullname": fullname,
                    "password": hashlib.sha256(password.encode()).hexdigest(),
                    "created_at": "2023-04-05"
                }
                # Add directly to local_users if using local storage
                if hasattr(self.game.api_client.db_manager, 'use_local_storage') and self.game.api_client.db_manager.use_local_storage:
                    # Check if user already exists in local storage
                    for user in self.game.api_client.db_manager.local_users:
                        if user.get("username") == username:
                            self.game.current_state = self.game.LOGIN
                            self.game.set_status(f"Test user {username} already exists. Please login.", (0, 255, 0))
                            return
                    # Add test user to local storage
                    self.game.api_client.db_manager.local_users.append(test_user)
                    print(f"Added test user {username} directly to local storage")
                    print(f"Password hash: {test_user['password'][:15]}...")
                
                self.game.current_state = self.game.LOGIN
                self.game.set_status(f"Test account {username} created! Please login.", (0, 255, 0))
                return
                
            # Start loading screen for registration
            self.game.start_loading(
                message="Creating your account...",
                target_state=self.game.LOGIN,
                operation=lambda: self._perform_registration(username, email, password, fullname)
            )
        
        # Handle back button click
        elif hasattr(self.game, 'back_button') and self.game.back_button.is_clicked(mouse_pos):
            self.game.current_state = self.game.MAIN_MENU
            self.game.set_status("Welcome to Decision Game")
    
    def _perform_registration(self, username, email, password, fullname):
        """Perform registration in a separate thread for the loading screen."""
        # Register via game logic
        self.game.game_logic.register(username, password, email, fullname)
    
    def _handle_scenario_click(self, mouse_pos):
        """Handle clicks on the scenario screen."""
        # Handle scenario input box click
        self.game.scenario_input_box.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': mouse_pos}))
        
        # Handle button clicks
        if self.game.lets_talk_button.is_clicked(mouse_pos):
            self._analyze_scenario()
        
        elif self.game.voice_button.is_clicked(mouse_pos):
            self.game.game_logic.toggle_voice()
        
        elif self.game.settings_button.is_clicked(mouse_pos):
            self.game.previous_state = self.game.current_state
            self.game.current_state = self.game.SETTINGS
        
        # Guest user navigation buttons
        elif self.game.user == "Guest":
            if hasattr(self.game, 'scenario_login_button') and self.game.scenario_login_button.is_clicked(mouse_pos):
                self.game.user = None
                self.game.current_state = self.game.LOGIN
                self.game.set_status("Please login to access more features")
            
            elif hasattr(self.game, 'scenario_back_button') and self.game.scenario_back_button.is_clicked(mouse_pos):
                self.game.user = None
                self.game.current_state = self.game.MAIN_MENU
                self.game.set_status("Welcome to Decision Game")
        
        # Only show these buttons if not a guest
        if self.game.user and self.game.user != "Guest":
            if self.game.personality_button.is_clicked(mouse_pos):
                self.game.game_logic.start_personality_test()
            
            elif self.game.simulation_button.is_clicked(mouse_pos):
                self.game.previous_state = self.game.current_state
                self.game.current_state = self.game.SIMULATION
                self.game.game_logic.load_simulations()
            
            elif self.game.history_button.is_clicked(mouse_pos):
                self._handle_history_click()
            
            elif self.game.logout_button.is_clicked(mouse_pos):
                self.game.game_logic.logout()
    
    def _handle_conversation_click(self, mouse_pos):
        """Handle clicks on the Let's Talk conversation screen."""
        # Handle back button
        if self.game.back_button.is_clicked(mouse_pos):
            self.game.current_state = self.game.SCENARIO
        
        # Handle conversation state
        if self.game.conversation_complete:
            # Handle completed conversation
            if self.game.explore_more_button.is_clicked(mouse_pos):
                self.game.game_logic.explore_more()
            
            elif self.game.new_topic_button.is_clicked(mouse_pos):
                self.game.game_logic.start_new_topic()
            
            elif hasattr(self.game, 'download_conversation_button') and self.game.download_conversation_button.is_clicked(mouse_pos):
                self.game.game_logic.download_report("conversation")
        else:
            # Handle active conversation
            if hasattr(self.game, 'response_input'):
                self.game.response_input.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': mouse_pos}))
            
            if self.game.next_question_button.is_clicked(mouse_pos):
                self._submit_response()
            
            if hasattr(self.game, 'previous_question_button') and self.game.previous_question_button.is_clicked(mouse_pos):
                if self.game.current_question_index > 0:
                    self.game.current_question_index -= 1
                    self.game.previous_question_button.visible = (self.game.current_question_index > 0)
    
    def _handle_history_click(self):
        """Handle click on the history button."""
        # Start loading screen for history
        self.game.start_loading(
            message="Loading your decision history...",
            target_state=self.game.HISTORY,
            operation=lambda: self._load_history_data()
        )
    
    def handle_history_screen_events(self, event):
        """Handle events in the history screen."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle search button
                if hasattr(self.game, 'history_search_button') and self.game.history_search_button.is_clicked(mouse_pos):
                    self.handle_history_search()
                    
                # Handle sort buttons
                if hasattr(self.game, 'sort_date_button') and self.game.sort_date_button.is_clicked(mouse_pos):
                    self.handle_sort_history("date")
                    
                if hasattr(self.game, 'sort_length_button') and self.game.sort_length_button.is_clicked(mouse_pos):
                    self.handle_sort_history("length")
                    
                # Handle back button
                if self.game.back_button.is_clicked(mouse_pos):
                    self.game.back_to_previous_state()
                    
        # Handle text input in search box
        if event.type == pygame.KEYDOWN and hasattr(self.game, 'history_search_box'):
            if self.game.history_search_box.active:
                if event.key == pygame.K_RETURN:
                    self.handle_history_search()
                elif event.key == pygame.K_ESCAPE:
                    self.game.history_search_box.set_text("")
                else:
                    self.game.history_search_box.handle_key_event(event)
    
    def _handle_settings_click(self, mouse_pos):
        """Handle clicks on the settings screen."""
        if self.game.settings_back_button.is_clicked(mouse_pos):
            if self.game.previous_state:
                self.game.current_state = self.game.previous_state
            else:
                self.game.current_state = self.game.SCENARIO
        
        elif self.game.dark_mode_button.is_clicked(mouse_pos):
            self.game.toggle_dark_mode()
            # Update button text
            self.game.dark_mode_button.text = "ON" if self.game.dark_mode else "OFF"
        
        elif self.game.sound_button.is_clicked(mouse_pos):
            # Toggle sound if implemented
            self.game.sound_button.text = "ON" if self.game.sound_button.text == "OFF" else "OFF"
            self.game.set_status(f"Sound: {self.game.sound_button.text}")
    
    def _handle_personality_test_click(self, mouse_pos):
        """Handle clicks on the personality test screen."""
        if self.game.personality_back_button.is_clicked(mouse_pos):
            self.game.current_state = self.game.SCENARIO
            return
        
        # Check if questions are loaded
        if not self.game.mbti_questions or len(self.game.mbti_questions) == 0:
            # If no questions, try to load them again
            self.game.game_logic.start_personality_test()
            return
            
        # Update the progress label text to show current question number
        total_questions = len(self.game.mbti_questions)
        if hasattr(self.game, 'mbti_progress_label'):
            current_question_num = self.game.current_mbti_index + 1
            self.game.mbti_progress_label.text = f"Question {current_question_num} of {total_questions}"
        
        # Check if option buttons are clicked
        if hasattr(self.game, 'mbti_option_buttons'):
            for i, button in enumerate(self.game.mbti_option_buttons):
                if button.is_clicked(mouse_pos):
                    # Save the current question index to check if we need to update UI
                    old_index = self.game.current_mbti_index
                    
                    # Answer current question - this will internally increment current_mbti_index
                    self.game.game_logic.answer_mbti_question(i)
                    
                    # Force update the display to show only the current question
                    # This ensures we only see one question at a time
                    if self.game.current_mbti_index < total_questions and old_index != self.game.current_mbti_index:
                        # Update the question text
                        current_question = self.game.mbti_questions[self.game.current_mbti_index]
                        # Update progress label for the next question
                        self.game.mbti_progress_label.text = f"Question {self.game.current_mbti_index + 1} of {total_questions}"
                        print(f"Moving to question {self.game.current_mbti_index + 1} of {total_questions}")
                    break
    
    def _handle_personality_result_click(self, mouse_pos):
        """Handle clicks on the personality result screen."""
        if self.game.personality_back_button.is_clicked(mouse_pos):
            self.game.current_state = self.game.SCENARIO
        
        if hasattr(self.game, 'download_personality_button') and self.game.download_personality_button.is_clicked(mouse_pos):
            self.game.game_logic.download_report("personality")
    
    def _handle_simulation_click(self, mouse_pos):
        """Handle clicks on the simulation screen."""
        if self.game.simulation_back_button.is_clicked(mouse_pos):
            self.game.current_state = self.game.SCENARIO
        
        # Check if simulation scenario buttons are clicked
        if hasattr(self.game, 'simulation_scenarios'):
            for scenario in self.game.simulation_scenarios:
                if "button" in scenario and scenario["button"].is_clicked(mouse_pos):
                    self.game.current_simulation = scenario
                    self.game.current_state = self.game.SIMULATION_RESULT
                    # This would need additional logic to load the simulation
                    self.game.set_status(f"Loading simulation: {scenario.get('title', 'Unknown')}", BLUE)
                    break
    
    def _handle_simulation_result_click(self, mouse_pos):
        """Handle clicks on the simulation result screen."""
        if self.game.simulation_back_button.is_clicked(mouse_pos):
            self.game.current_state = self.game.SIMULATION
        
        # Handle guest user login button
        if self.game.user == "Guest" and hasattr(self.game, 'simulation_login_button'):
            if self.game.simulation_login_button.is_clicked(mouse_pos):
                self.game.user = None
                self.game.current_state = self.game.LOGIN
                self.game.set_status("Please login or register to access all features")
        
        # Handle simulation choice buttons for registered users
        elif hasattr(self.game, 'simulation_choice_buttons'):
            for i, button in enumerate(self.game.simulation_choice_buttons):
                if button.is_clicked(mouse_pos):
                    # Process the chosen simulation option
                    self.game.game_logic.process_simulation_choice(i)
    
    def _handle_simulation_report_click(self, mouse_pos):
        """Handle clicks on the simulation report screen."""
        # Handle back button click
        if hasattr(self.game, 'simulation_report_back_button') and self.game.simulation_report_back_button.is_clicked(mouse_pos):
            self.game.current_state = self.game.SIMULATION
        
        # Handle try again button click
        if hasattr(self.game, 'simulation_try_again_button') and self.game.simulation_try_again_button.is_clicked(mouse_pos):
            self.game.current_state = self.game.SIMULATION_RESULT
        
        # Handle download report button click
        if hasattr(self.game, 'download_simulation_button') and self.game.download_simulation_button.is_clicked(mouse_pos):
            self.game.game_logic.download_report("simulation")
    
    def _analyze_scenario(self):
        """Process scenario analysis by calling the game logic method."""
        self.game.game_logic.analyze_scenario()
    
    def _submit_response(self):
        """Process user response in conversation mode."""
        if hasattr(self.game, 'response_input'):
            response = self.game.response_input.get_text()
            print(f"Submitting response: '{response}'")
            if response:
                self.game.game_logic.answer_current_question(response)
            else:
                self.game.set_status("Please enter a response", (255, 150, 0))

    def _load_history_data(self):
        """Load history data in a separate thread for the loading screen."""
        # Load history data
        self.game.game_logic.load_decision_history()
        
        # Set up history screen UI
        center_x = self.game.width // 2
        
        # Create search components if they don't exist
        if not hasattr(self.game, 'history_search_box'):
            self.game.history_search_box = TextBox(center_x, 100, 300, 40, 
                                              placeholder="Search your decisions...")
        
        if not hasattr(self.game, 'history_search_button'):
            self.game.history_search_button = Button(center_x + 180, 100, 120, 40, 
                                               "Search", align="left")
        
        # Create history scroll area if it doesn't exist
        if not hasattr(self.game, 'history_scroll_area'):
            self.game.history_scroll_area = ScrollArea(center_x - 350, 150, 700, 350)
            
        # Create sort buttons if they don't exist
        if not hasattr(self.game, 'sort_date_button'):
            self.game.sort_date_button = Button(center_x - 200, 100, 120, 40, 
                                         "Sort by Date", align="center")
            
        if not hasattr(self.game, 'sort_length_button'):
            self.game.sort_length_button = Button(center_x - 350, 100, 140, 40, 
                                          "Sort by Length", align="center")
    
    def handle_history_search(self):
        """Handle search in history screen using text index."""
        if not hasattr(self.game, 'history_search_box'):
            return
            
        search_text = self.game.history_search_box.get_text()
        if not search_text or not self.game.user or self.game.user == "Guest":
            return
        
        # Start loading screen for search
        self.game.start_loading(
            message=f"Searching for '{search_text}'...",
            target_state=self.game.HISTORY,
            operation=lambda: self._perform_history_search(search_text)
        )
    
    def _perform_history_search(self, search_text):
        """Perform history search in a separate thread for the loading screen."""
        try:
            user_id = self.game.game_logic.get_user_id_from_token(self.game.token)
            if not user_id:
                self.game.set_status("Could not retrieve user information", (255, 0, 0))
                return
                
            # Use the search function with text index
            results = self.game.api_client.search_scenarios(user_id, search_text, limit=20)
            
            # Format for display
            formatted_results = []
            for scenario in results:
                formatted_results.append({
                    "date": scenario.get("analysis_date"),
                    "scenario_text": scenario.get("scenario_text", ""),
                    "word_count": scenario.get("word_count", 0),
                    "id": scenario.get("_id")
                })
                
            self.game.past_decisions = formatted_results
            self.game.set_status(f"Found {len(formatted_results)} matching decisions", (0, 255, 0))
            
        except Exception as e:
            print(f"Error searching decisions: {e}")
            self.game.set_status(f"Error searching: {str(e)}", (255, 0, 0))
    
    def handle_sort_history(self, sort_by="date"):
        """Handle sorting history with database indexing."""
        if not self.game.user or self.game.user == "Guest":
            return
            
        try:
            user_id = self.game.game_logic.get_user_id_from_token(self.game.token)
            if not user_id:
                self.game.set_status("Could not retrieve user information", (255, 0, 0))
                return
                
            # Sort options
            if sort_by == "date":
                # Default sort is by date
                scenarios = self.game.api_client.get_user_scenarios(user_id, limit=20)
                self.game.set_status("Sorted by date (newest first)", (0, 255, 0))
            else:  # sort_by == "length"
                # Use proper encapsulation with the API method for word count sorting
                scenarios = self.game.api_client.get_scenarios_by_word_count(user_id, limit=20)
                self.game.set_status("Sorted by length (longest first)", (0, 255, 0))
                
            # Format for display
            formatted_decisions = []
            for scenario in scenarios:
                formatted_decisions.append({
                    "date": scenario.get("analysis_date"),
                    "scenario_text": scenario.get("scenario_text", ""),
                    "word_count": scenario.get("word_count", 0),
                    "id": scenario.get("_id")
                })
                
            self.game.past_decisions = formatted_decisions
            
        except Exception as e:
            print(f"Error sorting decisions: {e}")
            self.game.set_status(f"Error sorting: {str(e)}", (255, 0, 0))

    def _handle_history_screen_click(self, pos):
        """Handle clicks in the history screen."""
        # Handle search button
        if hasattr(self.game, 'history_search_button') and self.game.history_search_button.is_clicked(pos):
            self.handle_history_search()
            
        # Handle sort buttons
        if hasattr(self.game, 'sort_date_button') and self.game.sort_date_button.is_clicked(pos):
            self.handle_sort_history("date")
            
        if hasattr(self.game, 'sort_length_button') and self.game.sort_length_button.is_clicked(pos):
            self.handle_sort_history("length")
            
        # Handle back button
        if hasattr(self.game, 'back_button') and self.game.back_button.is_clicked(pos):
            self.game.back_to_previous_state()
            
        # Activate search box if clicked
        if hasattr(self.game, 'history_search_box'):
            self.game.history_search_box.active = self.game.history_search_box.rect.collidepoint(pos)
            
        # Handle scroll area
        if hasattr(self.game, 'history_scroll_area'):
            self.game.history_scroll_area.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': pos, 'button': 1})) 