"""
Game logic for the Decision Game.
This module contains the core game logic and functions for handling different scenarios.
"""

import time
from datetime import datetime
import random
import threading

# Import UI components
from frontend.ui import Button, TextBox

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


class GameLogic:
    """Handles core game functionality and business logic."""
    
    def __init__(self, game):
        """
        Initialize with a reference to the main game object.
        
        Args:
            game: The main DecisionGame instance
        """
        self.game = game
    
    def register(self, username, password, email, fullname):
        """
        Register a new user.
        
        Args:
            username: The username
            password: The password
            email: The email
            fullname: The full name
        """
        try:
            print(f"\nAttempting to register user: {username}")
            # Call the API to register
            result = self.game.api_client.register(username, email, fullname, password)
                
            # Check if registration was successful
            if result.get("status_code") == 200:
                print(f"Registration successful for {username}")
                self.game.set_status("Registration successful! Please login.", (0, 255, 0))
                # Store registration in local storage for testing
                user_id = result.get("user_id")
                print(f"User ID: {user_id}")
            else:
                error_msg = result.get("detail", "Registration failed. Try a different username or email.")
                print(f"Registration failed: {error_msg}")
                self.game.set_status(f"Registration failed: {error_msg}", (255, 0, 0))
                
                # If loading state is active during registration failure
                if self.game.is_loading:
                    self.game.loading_target_state = self.game.REGISTER
                    self.game.loading_completed = True
                    
        except Exception as e:
            error_msg = str(e)
            print(f"Registration error: {error_msg}")
            self.game.set_status(f"Registration error: {error_msg}", (255, 0, 0))
            
            # If loading state is active during error
            if self.game.is_loading:
                self.game.loading_target_state = self.game.REGISTER
                self.game.loading_completed = True
    
    def logout(self):
        """Log out the current user"""
        # Clear user data
        self.game.user = None
        self.game.token = None
        
        # Clear any sensitive user data
        self.game.scenario_text = ""
        self.game.scenario_results = {}
        self.game.conversation_questions = []
        self.game.current_question_index = 0
        self.game.user_responses = []
        self.game.conversation_complete = False
        self.game.conversation_summary = {}
        self.game.past_decisions = []
        
        # Clear token in API client
        if hasattr(self.game.api_client, 'clear_token'):
            self.game.api_client.clear_token()
        
        # Return to main menu
        self.game.current_state = self.game.MAIN_MENU
        self.game.set_status("Logged out successfully", GREEN)
    
    def analyze_scenario(self):
        """Analyze the scenario text and get results."""
        scenario_text = self.game.scenario_input_box.get_text()
        
        # Debug print to see what's in the text box
        print(f"Scenario text: '{scenario_text}'")
        print(f"Placeholder: '{self.game.scenario_input_box.placeholder}'")
        
        if not scenario_text or scenario_text.strip() == "":
            self.game.set_status("Please enter a scenario first", (255, 150, 0))
            return
            
        # Store scenario text for later reference
        self.game.scenario_text = scenario_text
        
        # Start loading screen
        self.game.start_loading(
            message="Analyzing your scenario...",
            target_state=self.game.LETS_TALK,
            operation=lambda: self._perform_scenario_analysis(scenario_text)
        )
    
    def _perform_scenario_analysis(self, scenario_text):
        """Perform the scenario analysis in a separate thread for the loading screen."""
        try:
            # Use the API client if logged in
            if self.game.user and self.game.token and self.game.user != "Guest":
                result = self.game.api_client.analyze_scenario(scenario_text)
                if result:
                    self.game.scenario_results = result
                    
                    # Save to database using indexed function
                    user_id = self.get_user_id_from_token(self.game.token)
                    if user_id:
                        scenario_id = self.game.api_client.save_scenario_analysis(
                            user_id, 
                            scenario_text, 
                            result
                        )
                        if scenario_id:
                            print(f"Saved scenario analysis with ID: {scenario_id}")
                    
                    self.game.set_status("Analysis complete", (0, 255, 0))
                else:
                    self.game.set_status("Failed to analyze scenario", (255, 0, 0))
            else:
                # Generate mock results for guest users
                self.game.scenario_results = self.generate_guest_results(scenario_text)
                self.game.set_status("Guest analysis complete", (0, 255, 0))
            
            # Initialize conversation
            self.game.conversation_questions = self.generate_conversation_questions(scenario_text)
            self.game.current_question_index = 0
            self.game.user_responses = []
            self.game.conversation_complete = False
            
            # Set up the conversation UI
            self.setup_conversation_ui()
            
        except Exception as e:
            print(f"Error analyzing scenario: {e}")
            self.game.set_status(f"Error: {str(e)}", (255, 0, 0))
    
    def get_user_id_from_token(self, token):
        """Get user ID from token using the API client for encapsulation."""
        if not token:
            return None
            
        try:
            # Use the api_client method for proper encapsulation
            return self.game.api_client.get_user_id_from_token(token)
        except Exception as e:
            print(f"Error getting user ID from token: {e}")
            return None
            
    def load_decision_history(self):
        """Load decision history using indexed database queries."""
        if not self.game.user or not self.game.token or self.game.user == "Guest":
            self.game.past_decisions = []
            self.game.set_status("Login to view your decision history", (255, 150, 0))
            return
            
        try:
            user_id = self.get_user_id_from_token(self.game.token)
            if not user_id:
                self.game.past_decisions = []
                self.game.set_status("Could not retrieve user information", (255, 0, 0))
                return
                
            # Get scenarios using indexed query
            scenarios = self.game.api_client.get_user_scenarios(user_id, limit=20)
            
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
            self.game.set_status(f"Loaded {len(formatted_decisions)} past decisions", (0, 255, 0))
            
        except Exception as e:
            print(f"Error loading decision history: {e}")
            self.game.set_status(f"Error loading history: {str(e)}", (255, 0, 0))
            self.game.past_decisions = []
    
    def generate_guest_results(self, scenario_text):
        """Generate mock analysis results for guest users."""
        # This is a placeholder implementation - in a real app, this would 
        # likely use a local model or simplified algorithm
        
        # Split the scenario into words and get some basic metrics
        words = scenario_text.split()
        word_count = len(words)
        
        # Generate some random questions based on common decision frameworks
        questions = [
            "What are your main priorities in this situation?",
            "What alternatives have you considered?",
            "What are the potential risks of each option?",
            "How might this decision affect others around you?",
            "What information do you still need to make this decision?"
        ]
        
        # Generate some generic perspectives
        perspectives = [
            "Consider how this decision aligns with your long-term goals.",
            "Think about how this decision might look in hindsight a year from now.",
            "Examine this situation from the perspective of someone you admire.",
            "Consider the ethical implications of each possible choice."
        ]
        
        # Generate a simple action plan
        action_plan = [
            "List all available options and their pros/cons.",
            "Gather any missing information you identified earlier.",
            "Consult with someone you trust about this decision.",
            "Set a deadline for making the final decision."
        ]
        
        # Return a dictionary with analysis results
        return {
            "questions": questions,
            "perspectives": perspectives,
            "action_plan": action_plan,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "word_count": word_count
        }
    
    def setup_conversation_ui(self):
        """Initialize the UI for conversation mode."""
        # Create a new text box for user responses
        center_x = self.game.width // 2
        self.game.response_input = TextBox(center_x, 480, 700, 80, 
                                       placeholder="Type your response here...",
                                       multiline=True)
        
        # Initialize navigation buttons
        self.game.next_question_button.visible = True
        if hasattr(self.game, 'previous_question_button'):
            self.game.previous_question_button.visible = self.game.current_question_index > 0
        
        # Hide explore options initially
        if hasattr(self.game, 'explore_more_button'):
            self.game.explore_more_button.visible = False
        if hasattr(self.game, 'new_topic_button'):
            self.game.new_topic_button.visible = False
    
    def generate_conversation_questions(self, scenario_text):
        """Generate a sequence of conversation questions based on the scenario."""
        # In a real app, this would use an AI model to generate questions
        # This is a placeholder implementation
        return [
            "Can you tell me more about what's making this decision difficult for you?",
            "What are the main options you're considering?",
            "What would be the ideal outcome of this decision?",
            "Have you faced similar decisions before? How did those turn out?",
            "What values or principles are important to you in making this decision?"
        ]
    
    def answer_current_question(self, response):
        """Process the user's response to the current question."""
        # Add response to list
        print(f"Processing response: '{response}'")
        self.game.user_responses.append(response)
        
        # Clear the response input
        self.game.response_input.set_text("")
        
        # Move to next question
        self.game.current_question_index += 1
        
        # Check if we've reached the end of the questions
        if self.game.current_question_index >= len(self.game.conversation_questions):
            self.complete_conversation()
        else:
            print(f"Moving to question {self.game.current_question_index+1}")
            # Update previous button visibility
            if hasattr(self.game, 'previous_question_button'):
                self.game.previous_question_button.visible = True
    
    def complete_conversation(self):
        """Complete the conversation and generate a summary."""
        self.game.conversation_complete = True
        
        # Hide navigation buttons
        self.game.next_question_button.visible = False
        self.game.previous_question_button.visible = False
        
        # Show finish button
        self.game.finish_conversation_button.visible = False
        
        # Show explore options
        self.game.explore_more_button.visible = True
        self.game.new_topic_button.visible = True
        
        # Generate conversation summary
        self.game.conversation_summary = self.generate_conversation_summary()
        
        # Set status
        self.game.set_status("Conversation complete! Here's your decision clarity summary.", (0, 200, 0))
    
    def generate_conversation_summary(self):
        """Generate a summary of the conversation and insights gained."""
        # This would use AI in a real app - this is a placeholder
        clarity_levels = ["Low", "Moderate", "Good", "High", "Excellent"]
        
        return {
            "clarity_level": random.choice(clarity_levels),
            "key_insights": [
                "You seem to value long-term outcomes over short-term gains.",
                "Financial considerations appear to be a significant factor in your decision.",
                "Your responses indicate a preference for collaborative approaches."
            ],
            "suggested_next_steps": [
                "Consider creating a pros and cons list for each option.",
                "Discuss your options with trusted advisors.",
                "Set a firm deadline for making your final decision."
            ]
        }
    
    def explore_more(self):
        """Continue the conversation with more in-depth questions."""
        # Reset conversation state for more questions
        self.game.conversation_complete = False
        
        # Generate new questions
        additional_questions = [
            "Let's explore further. What aspect of this decision causes you the most stress?",
            "What information would help you feel more confident in your decision?",
            "How would you feel if you chose differently from what others expect?"
        ]
        
        # Extend the questions list
        self.game.conversation_questions.extend(additional_questions)
        
        # Reset UI for conversation
        self.game.next_question_button.visible = True
        self.game.previous_question_button.visible = True
        self.game.explore_more_button.visible = False
        self.game.new_topic_button.visible = False
    
    def start_new_topic(self):
        """Reset to allow the user to enter a new scenario."""
        self.game.current_state = self.game.SCENARIO
        self.game.scenario_input_box.set_text("")
        self.game.set_status("Ready for a new decision scenario", (0, 150, 255))
    
    def start_personality_test(self):
        """Start the personality test."""
        # Start loading screen
        self.game.start_loading(
            message="Preparing personality test questions...",
            target_state=self.game.PERSONALITY_TEST,
            operation=lambda: self._load_personality_test()
        )
        
    def _load_personality_test(self):
        """Load personality test questions in a separate thread for the loading screen."""
        try:
            # Get MBTI questions from API
            response = self.game.api_client.get_mbti_questions()
            
            if response and len(response) > 0:
                # Store the questions
                self.game.mbti_questions = response
                self.game.set_status("Personality test loaded", (0, 255, 0))
            else:
                # If API call fails or returns empty, use fallback questions
                self.game.mbti_questions = self._generate_mbti_questions()
                self.game.set_status("Using local personality test questions", (255, 200, 0))
            
            # Reset answers and current index
            self.game.mbti_answers = {}
            self.game.current_mbti_index = 0
                
        except Exception as e:
            print(f"Error starting personality test: {e}")
            # Use fallback questions on error
            self.game.mbti_questions = self._generate_mbti_questions()
            self.game.set_status("Using local personality test questions", (255, 200, 0))
    
    def _generate_mbti_questions(self):
        """Generate 20 MBTI questions for personality assessment."""
        options = ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
        
        return [
            {
                "id": 1,
                "question": "You find it easy to introduce yourself to other people.",
                "options": options,
                "dimension": "E-I"  # Extraversion vs. Introversion
            },
            {
                "id": 2,
                "question": "You often get so lost in thoughts that you ignore or forget your surroundings.",
                "options": options,
                "dimension": "N-S"  # Intuition vs. Sensing
            },
            {
                "id": 3,
                "question": "You try to respond to emails as soon as possible and cannot stand a messy inbox.",
                "options": options,
                "dimension": "J-P"  # Judging vs. Perceiving
            },
            {
                "id": 4,
                "question": "You find it easy to stay relaxed under pressure.",
                "options": options,
                "dimension": "T-F"  # Thinking vs. Feeling
            },
            {
                "id": 5,
                "question": "You do not usually initiate conversations.",
                "options": options,
                "dimension": "I-E"  # Introversion vs. Extraversion
            },
            {
                "id": 6,
                "question": "You rarely worry about how your actions affect other people.",
                "options": options,
                "dimension": "T-F"  # Thinking vs. Feeling
            },
            {
                "id": 7,
                "question": "Your home and work environments are quite tidy.",
                "options": options,
                "dimension": "J-P"  # Judging vs. Perceiving
            },
            {
                "id": 8,
                "question": "You do not mind being at the center of attention.",
                "options": options,
                "dimension": "E-I"  # Extraversion vs. Introversion
            },
            {
                "id": 9,
                "question": "You consider yourself more practical than creative.",
                "options": options,
                "dimension": "S-N"  # Sensing vs. Intuition
            },
            {
                "id": 10,
                "question": "People can rarely upset you.",
                "options": options,
                "dimension": "T-F"  # Thinking vs. Feeling
            },
            {
                "id": 11,
                "question": "Your travel plans are usually well thought out.",
                "options": options,
                "dimension": "J-P"  # Judging vs. Perceiving
            },
            {
                "id": 12,
                "question": "It is often difficult for you to relate to other people's feelings.",
                "options": options,
                "dimension": "T-F"  # Thinking vs. Feeling
            },
            {
                "id": 13,
                "question": "Your mood can change very quickly.",
                "options": options,
                "dimension": "F-T"  # Feeling vs. Thinking
            },
            {
                "id": 14,
                "question": "You prefer to follow a schedule rather than be spontaneous.",
                "options": options,
                "dimension": "J-P"  # Judging vs. Perceiving
            },
            {
                "id": 15,
                "question": "You rarely feel insecure.",
                "options": options,
                "dimension": "T-F"  # Thinking vs. Feeling
            },
            {
                "id": 16,
                "question": "You avoid making phone calls when possible.",
                "options": options,
                "dimension": "I-E"  # Introversion vs. Extraversion
            },
            {
                "id": 17,
                "question": "You often spend time exploring unrealistic yet intriguing ideas.",
                "options": options,
                "dimension": "N-S"  # Intuition vs. Sensing
            },
            {
                "id": 18,
                "question": "You prefer to complete one project before starting another.",
                "options": options,
                "dimension": "J-P"  # Judging vs. Perceiving
            },
            {
                "id": 19,
                "question": "In social situations, you rarely feel awkward or out of place.",
                "options": options,
                "dimension": "E-I"  # Extraversion vs. Introversion
            },
            {
                "id": 20,
                "question": "You value objective facts more than personal feelings when making decisions.",
                "options": options,
                "dimension": "T-F"  # Thinking vs. Feeling
            }
        ]
    
    def answer_mbti_question(self, option_index):
        """Record answer for current MBTI question and move to next question."""
        # Check if we have questions
        if not self.game.mbti_questions or self.game.current_mbti_index >= len(self.game.mbti_questions):
            return
            
        # Get current question
        current_question = self.game.mbti_questions[self.game.current_mbti_index]
        question_id = current_question.get("id", self.game.current_mbti_index + 1)
        
        # Save the answer (0 = Strongly Agree, 4 = Strongly Disagree)
        self.game.mbti_answers[question_id] = option_index
                
        # Move to next question
        self.game.current_mbti_index += 1
                
        # If all questions answered, process results
        if self.game.current_mbti_index >= len(self.game.mbti_questions):
        # Process results
            self.submit_mbti_answers()
        else:
            # Update status message
            question_num = self.game.current_mbti_index + 1
            total_questions = len(self.game.mbti_questions)
            self.game.set_status(f"Question {question_num} of {total_questions}", (0, 150, 255))
    
    def submit_mbti_answers(self):
        """Submit MBTI answers and get results."""
        try:
            # If user is logged in, use API to submit answers
            if self.game.user and self.game.token and self.game.user != "Guest":
                self.game.start_loading(
                    message="Analyzing your personality profile...",
                    target_state=self.game.PERSONALITY_RESULT,
                    operation=lambda: self._submit_mbti_to_api()
                )
            else:
                # For guest users or if API fails, generate results locally
                self.game.start_loading(
                    message="Generating your personality profile...",
                    target_state=self.game.PERSONALITY_RESULT,
                    operation=lambda: self._generate_local_mbti_result()
                )
        except Exception as e:
            print(f"Error submitting MBTI answers: {e}")
            self.game.set_status(f"Error processing personality test: {str(e)}", (255, 0, 0))
    
    def _submit_mbti_to_api(self):
        """Submit MBTI answers to API and get results."""
        try:
            # Submit answers to API
            result = self.game.api_client.submit_mbti_answers(self.game.mbti_answers)
        
            if result:
                self.game.mbti_result = result
                self.game.set_status("Personality results ready", (0, 255, 0))
            else:
                # If API call fails, fall back to local processing
                self._generate_local_mbti_result()
        except Exception as e:
            print(f"API error for MBTI: {e}")
            # Fall back to local processing
            self._generate_local_mbti_result()
    
    def _generate_local_mbti_result(self):
        """Generate MBTI results locally based on answers."""
        # Process the answers to determine MBTI type
        e_score = i_score = s_score = n_score = t_score = f_score = j_score = p_score = 0
        
        for question_id, answer in self.game.mbti_answers.items():
            # Find the question in mbti_questions
            question = None
            for q in self.game.mbti_questions:
                if q.get("id") == question_id:
                    question = q
                    break
            
            if not question or "dimension" not in question:
                continue
                
            # Get the dimension this question measures
            dimension = question.get("dimension", "")
            
            # Convert answer (0=Strongly Agree to 4=Strongly Disagree) to score (-2 to +2)
            score = 2 - answer
            
            # Apply score to the appropriate dimension
            if dimension == "E-I":
                e_score += score
            elif dimension == "I-E":
                i_score += score
            elif dimension == "S-N":
                s_score += score
            elif dimension == "N-S":
                n_score += score
            elif dimension == "T-F":
                t_score += score
            elif dimension == "F-T":
                f_score += score
            elif dimension == "J-P":
                j_score += score
            elif dimension == "P-J":
                p_score += score
        
        # Determine overall type
        type_code = ""
        type_code += "E" if e_score > i_score else "I"
        type_code += "S" if s_score > n_score else "N"
        type_code += "T" if t_score > f_score else "F"
        type_code += "J" if j_score > p_score else "P"
        
        # Generate result object
        self.game.mbti_result = self._get_mbti_type_description(type_code)
        self.game.set_status(f"Your personality type: {type_code}", (0, 255, 0))
    
    def _get_mbti_type_description(self, type_code):
        """Get description for MBTI type."""
        # Basic descriptions for each type
        descriptions = {
            "INTJ": {
                "type": "INTJ",
                "description": "The Architect. Strategic thinkers with a plan for everything. Independent, analytical and driven by ideas.",
                "strengths": ["Strategic thinking", "Independent", "Analytical", "Determined", "Knowledgeable"],
                "weaknesses": ["Overly critical", "Dismissive of emotions", "Sometimes judgmental", "Perfectionistic"],
                "career_matches": ["Scientific research", "Engineering", "Law", "Architecture", "Strategic planning"]
            },
            "INTP": {
                "type": "INTP",
                "description": "The Logician. Innovative inventors with an unquenchable thirst for knowledge. Values ideas, connections and complex problems.",
                "strengths": ["Analytical", "Original thinking", "Open-minded", "Objective", "Honest"],
                "weaknesses": ["Disconnected", "Insensitive", "Indecisive", "Procrastination"],
                "career_matches": ["Computer programming", "Scientific research", "Academia", "Writing", "Engineering"]
            },
            "ENTJ": {
                "type": "ENTJ",
                "description": "The Commander. Bold, imaginative and strong-willed leaders, always finding a way – or making one. Values efficiency, competence and results.",
                "strengths": ["Confident leadership", "Strategic thinking", "Efficient", "Charismatic", "Strong-willed"],
                "weaknesses": ["Impatient", "Stubborn", "Arrogant", "Insensitive"],
                "career_matches": ["Business leadership", "Management", "Law", "Engineering", "Strategic development"]
            },
            "ENTP": {
                "type": "ENTP",
                "description": "The Debater. Smart and curious thinkers who view life as an ongoing debate. Values ideas, innovation and challenging conventions.",
                "strengths": ["Innovative", "Quick thinking", "Adaptable", "Knowledgeable", "Excellent brainstorming"],
                "weaknesses": ["Argumentative", "Insensitive", "Easily bored", "Procrastination"],
                "career_matches": ["Entrepreneurship", "Debate/politics", "Advertising", "Creative fields", "Technology"]
            },
            "INFJ": {
                "type": "INFJ",
                "description": "The Advocate. Quiet and mystical, yet very inspiring and tireless idealists. Values harmony, growth and authenticity.",
                "strengths": ["Creative", "Insightful", "Principled", "Passionate", "Altruistic"],
                "weaknesses": ["Sensitive to criticism", "Perfectionism", "Burnout", "Difficult to get to know"],
                "career_matches": ["Counseling", "Teaching", "Healthcare", "Non-profit work", "Writing"]
            },
            "INFP": {
                "type": "INFP",
                "description": "The Mediator. Poetic, kind and altruistic people, always eager to help a good cause. Values authenticity, harmony and depth of feeling.",
                "strengths": ["Empathetic", "Gentle", "Creative", "Passionate", "Idealistic"],
                "weaknesses": ["Impractical", "Self-isolating", "Emotional", "Difficult to get to know"],
                "career_matches": ["Counseling", "Social work", "Writing", "Teaching", "Arts"]
            },
            "ENFJ": {
                "type": "ENFJ",
                "description": "The Protagonist. Charismatic and inspiring leaders, able to mesmerize their listeners. Values authentic connections and helping others develop.",
                "strengths": ["Charismatic", "Empathetic", "Natural leader", "Reliable", "Passionate"],
                "weaknesses": ["Overly idealistic", "Too selfless", "Approval-seeking", "Inflexible"],
                "career_matches": ["Teaching", "Counseling", "Human resources", "Public relations", "Sales"]
            },
            "ENFP": {
                "type": "ENFP",
                "description": "The Campaigner. Enthusiastic, creative and sociable free spirits, who can always find a reason to smile. Values innovation, possibilities and connections.",
                "strengths": ["Enthusiastic", "Creative", "Sociable", "Empathetic", "Independent"],
                "weaknesses": ["Unfocused", "Disorganized", "People-pleasing", "Overthinking"],
                "career_matches": ["Counseling", "Teaching", "Arts", "Entertainment", "Human resources"]
            },
            "ISTJ": {
                "type": "ISTJ",
                "description": "The Logistician. Practical and fact-minded individuals, whose reliability cannot be doubted. Values tradition, responsibility and a stable structure.",
                "strengths": ["Honest", "Direct", "Responsible", "Calm", "Practical"],
                "weaknesses": ["Stubborn", "Insensitive", "Judgment", "Always by the book"],
                "career_matches": ["Finance", "Accounting", "Engineering", "Law enforcement", "Administration"]
            },
            "ISFJ": {
                "type": "ISFJ",
                "description": "The Defender. Very dedicated and warm protectors, always ready to defend their loved ones. Values security, tradition and helping others.",
                "strengths": ["Supportive", "Reliable", "Patient", "Loyal", "Observant"],
                "weaknesses": ["Taking things personally", "Overworking", "Neglecting self", "Reluctant to change"],
                "career_matches": ["Healthcare", "Education", "Social work", "Administration", "Customer service"]
            },
            "ESTJ": {
                "type": "ESTJ",
                "description": "The Executive. Excellent administrators, unsurpassed at managing things – or people. Values structure, tradition and clear expectations.",
                "strengths": ["Dedicated", "Organized", "Practical", "Reliable", "Honest"],
                "weaknesses": ["Inflexible", "Judgmental", "Stubborn", "Difficulty with emotions"],
                "career_matches": ["Business management", "Military", "Law enforcement", "Legal professions", "Project management"]
            },
            "ESFJ": {
                "type": "ESFJ",
                "description": "The Consul. Extraordinarily caring, social and popular people, always eager to help. Values harmony, social connection and being of service.",
                "strengths": ["Supportive", "Reliable", "Conscientious", "Practical", "Warm"],
                "weaknesses": ["Needing approval", "Too selfless", "Inflexible", "Sensitive to criticism"],
                "career_matches": ["Teaching", "Healthcare", "Social work", "Human resources", "Administration"]
            },
            "ISTP": {
                "type": "ISTP",
                "description": "The Virtuoso. Bold and practical experimenters, masters of all kinds of tools. Values efficiency, logic and freedom to tackle problems in their own way.",
                "strengths": ["Logical", "Practical", "Adaptable", "Spontaneous", "Technical skills"],
                "weaknesses": ["Stubbornness", "Insensitive", "Risk-taking", "Reserved", "Easily bored"],
                "career_matches": ["Engineering", "Mechanics", "Computer science", "Law enforcement", "Construction"]
            },
            "ISFP": {
                "type": "ISFP",
                "description": "The Adventurer. Flexible and charming artists, always ready to explore and experience something new. Values personal freedom, authentic expression and sensory experiences.",
                "strengths": ["Sensitive", "Creative", "Open-minded", "Passionate", "Imaginative"],
                "weaknesses": ["Unpredictable", "Easily stressed", "Fiercely independent", "Conflict avoidant"],
                "career_matches": ["Arts", "Music", "Design", "Healthcare", "Culinary arts"]
            },
            "ESTP": {
                "type": "ESTP",
                "description": "The Entrepreneur. Smart, energetic and very perceptive people, who truly enjoy living on the edge. Values action, immediate results and practical solutions.",
                "strengths": ["Energetic", "Rational", "Action-oriented", "Perceptive", "Sociable"],
                "weaknesses": ["Impatient", "Risk-prone", "Unstructured", "Blunt", "Insensitive"],
                "career_matches": ["Sales", "Marketing", "Entrepreneurship", "Emergency services", "Sports"]
            },
            "ESFP": {
                "type": "ESFP",
                "description": "The Entertainer. Spontaneous, energetic and enthusiastic people – life is never boring around them. Values experiences, people and making every moment count.",
                "strengths": ["Bold", "Friendly", "Practical", "Observant", "Excellent people skills"],
                "weaknesses": ["Sensitive", "Easily bored", "Poor planning", "Conflict avoidant"],
                "career_matches": ["Entertainment", "Sales", "Teaching", "Customer service", "Hospitality"]
            }
        }
        
        # Return the description for the given type, or a default if not found
        return descriptions.get(type_code, {
            "type": type_code,
            "description": "Your unique personality type. Each person has a distinct combination of preferences that shapes their worldview and approach to life.",
            "strengths": ["Unique perspective", "Individual talents", "Personal insights", "Special skills", "Your authentic approach"],
            "weaknesses": ["Personal growth areas", "Individual challenges", "Aspects to develop", "Potential blind spots"],
            "career_matches": ["Careers matching your specific strengths", "Roles that value your unique skills", "Positions aligned with your personality"]
        })
    
    # Additional game logic methods would go here
    def load_simulations(self):
        """Load available simulation scenarios."""
        try:
            if self.game.api_client and self.game.token:
                scenarios = self.game.api_client.get_simulation_scenarios()
                if scenarios:
                    self.game.simulation_scenarios = scenarios
                    
                    # Initialize buttons for each scenario
                    center_x = self.game.width // 2
                    for i, scenario in enumerate(self.game.simulation_scenarios):
                        y_pos = 200 + i * 100
                        button = Button(center_x, y_pos, 700, 60, scenario["title"], 
                                      color=PRIMARY_LIGHT, hover_color=PRIMARY)
                        scenario["button"] = button
                    
                    self.game.set_status("Simulations loaded successfully", GREEN)
                else:
                    # Fallback to mock scenarios
                    self._load_mock_simulations()
            else:
                # Use mock scenarios for testing
                self._load_mock_simulations()
        except Exception as e:
            print(f"Error loading simulations: {e}")
            self.game.set_status(f"Error: {str(e)}", RED)
            self._load_mock_simulations()
    
    def _load_mock_simulations(self):
        """Load mock simulation scenarios for demonstration."""
        self.game.simulation_scenarios = [
            {
                "id": 1,
                "title": "Career Decision Simulation",
                "description": "Practice making a career change decision with different outcomes."
            },
            {
                "id": 2,
                "title": "Investment Decision Simulation",
                "description": "Explore different investment strategies and see potential outcomes."
            },
            {
                "id": 3,
                "title": "Life Balance Decision Simulation",
                "description": "Practice balancing work, family, and personal growth decisions."
            }
        ]
        
        # Create buttons for mock scenarios
        center_x = self.game.width // 2
        for i, scenario in enumerate(self.game.simulation_scenarios):
            y_pos = 200 + i * 100
            button = Button(center_x, y_pos, 700, 60, scenario["title"], 
                          color=PRIMARY_LIGHT, hover_color=PRIMARY)
            scenario["button"] = button
        
        self.game.set_status("Demo simulations loaded", BLUE)
    
    def toggle_voice(self):
        """Toggle voice input on/off"""
        if not hasattr(self.game, 'voice_engine'):
            self.game.set_status("Voice recognition is not available", (255, 100, 0))
            return
            
        if not self.game.voice_engine.is_available():
            # If we're here, it means we couldn't use either real or fallback mode
            # Show detailed error information
            error_details = self.game.voice_engine.get_error_details()
            print("Voice recognition error details:")
            print(error_details)
            
            # Display more specific error message
            if "no default input device" in self.game.voice_engine.last_error:
                self.game.set_status("No microphone detected. Please check your audio settings.", (255, 100, 0))
            elif "pyaudio" in self.game.voice_engine.last_error.lower():
                self.game.set_status("PyAudio error. Voice recognition unavailable.", (255, 100, 0))
            else:
                self.game.set_status("Microphone not detected. Check your audio settings.", (255, 100, 0))
                
            # Show a more detailed message in the console
            print("To use voice recognition, please make sure:")
            print("1. You have a working microphone connected")
            print("2. PyAudio is properly installed")
            print("3. The application has permission to access your microphone")
            print(f"Error: {self.game.voice_engine.last_error}")
            return
            
        # If currently active, disable it
        if self.game.voice_active:
            self.game.voice_active = False
            if hasattr(self.game, 'voice_button'):
                self.game.voice_button.text = "Voice Input"
                self.game.voice_button.color = (75, 100, 255)  # Default color
            self.game.set_status("Voice input disabled", (255, 180, 0))
            
            # Stop any ongoing listening
            if self.game.listening and hasattr(self.game, 'voice_engine'):
                self.game.voice_engine.stop_listening()
        else:
            # If we're turning it on
            self.game.voice_active = True
            if hasattr(self.game, 'voice_button'):
                self.game.voice_button.text = "Starting..."
                self.game.voice_button.color = (0, 180, 0)  # Green
                
            # Check if we're using fallback mode
            if self.game.voice_engine.use_fallback:
                self.game.set_status("Starting simulated voice input (no microphone detected)", (255, 150, 0))
            else:
                self.game.set_status("Initializing voice recognition...", (0, 180, 0))
            
            # Start listening immediately
            threading.Thread(target=self.listen_for_voice, daemon=True).start()
    
    def listen_for_voice(self):
        """Listen for voice input in a separate thread"""
        if not hasattr(self.game, 'voice_engine') or not self.game.voice_active:
            return
            
        try:
            self.game.listening = True
            
            # Change button appearance during listening
            if hasattr(self.game, 'voice_button'):
                self.game.voice_button.text = "Listening..."
                self.game.voice_button.color = (255, 100, 100)  # Red while listening
            
            # Check if we're using fallback mode
            using_fallback = self.game.voice_engine.use_fallback
            
            if using_fallback:
                self.game.set_status("Using simulated voice input...", (0, 150, 255))
            else:
                self.game.set_status("Listening to your voice input...", (0, 150, 255))
            
            # Get voice input
            text = self.game.voice_engine.listen()
            
            if text:
                # Update the appropriate text box based on current state
                if self.game.current_state == self.game.SCENARIO:
                    print(f"Setting voice input in scenario box: '{text}'")
                    self.game.scenario_input_box.set_text(text)
                    # Force refresh the display to show the updated text
                    self.game.draw()
                elif self.game.current_state == self.game.LETS_TALK and hasattr(self.game, 'response_input'):
                    print(f"Setting voice input in response box: '{text}'")
                    self.game.response_input.set_text(text)
                    # Force refresh the display to show the updated text
                    self.game.draw()
                
                if using_fallback:
                    self.game.set_status(f"Simulated voice text: {text[:30]}{'...' if len(text) > 30 else ''}", (0, 200, 0))
                else:
                    self.game.set_status(f"Voice captured: {text[:30]}{'...' if len(text) > 30 else ''}", (0, 200, 0))
            else:
                self.game.set_status("Could not understand voice input. Please try again.", (255, 100, 100))
        except Exception as e:
            print(f"Voice input error: {e}")
            self.game.set_status(f"Voice input error: {str(e)}", (255, 0, 0))
        finally:
            self.game.listening = False
            # Reset voice button appearance
            if hasattr(self.game, 'voice_button'):
                if self.game.voice_active:
                    if self.game.voice_engine.use_fallback:
                        self.game.voice_button.text = "Simulated Voice"
                        self.game.voice_button.color = (255, 160, 0)  # Orange for simulated
                    else:
                        self.game.voice_button.text = "Voice Active"
                        self.game.voice_button.color = (0, 180, 0)  # Green for active
                else:
                    self.game.voice_button.text = "Voice Input"
                    self.game.voice_button.color = (75, 100, 255)  # Default color
    
    def download_report(self, report_type):
        """Download a report based on the specified type"""
        try:
            if not hasattr(self.game, 'api_client') or not self.game.api_client:
                self.game.set_status("Cannot download report without being logged in", YELLOW)
                return
                
            if report_type == "personality" and hasattr(self.game, 'mbti_result'):
                # Download personality report
                filename = f"personality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                success = self.game.api_client.download_personality_report(self.game.mbti_result, filename)
                if success:
                    self.game.set_status(f"Report downloaded as {filename}", GREEN)
                else:
                    self.game.set_status("Failed to download report", RED)
            
            elif report_type == "conversation" and hasattr(self.game, 'conversation_summary'):
                # Download conversation summary
                filename = f"conversation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                success = self.game.api_client.download_conversation_report(self.game.conversation_summary, filename)
                if success:
                    self.game.set_status(f"Report downloaded as {filename}", GREEN)
                else:
                    self.game.set_status("Failed to download report", RED)
            
            elif report_type == "simulation" and hasattr(self.game, 'simulation_report'):
                # Download simulation summary
                filename = f"simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                success = self.game.api_client.download_conversation_report(self.game.simulation_report, filename)
                if success:
                    self.game.set_status(f"Report downloaded as {filename}", GREEN)
                else:
                    self.game.set_status("Failed to download report", RED)
            
            else:
                self.game.set_status("No report data available to download", YELLOW)
                
        except Exception as e:
            print(f"Download error: {e}")
            self.game.set_status(f"Download error: {str(e)}", RED)
    
    def process_simulation_choice(self, choice_index):
        """Process a simulation choice and generate a report.
        
        Args:
            choice_index: The index of the chosen option (0 for A, 1 for B)
        """
        try:
            if not hasattr(self.game, 'current_simulation'):
                self.game.set_status("No simulation selected", YELLOW)
                return
                
            scenario = self.game.current_simulation
            choice_label = 'A' if choice_index == 0 else 'B'
            choice_name = "Conservative Approach" if choice_index == 0 else "Bold Approach"
            
            # Generate a simulation report based on the choice
            self.game.simulation_report = {
                "scenario_title": scenario.get("title", "Unnamed Scenario"),
                "scenario_description": scenario.get("description", "No description available."),
                "choice": choice_name,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "outcomes": self._generate_choice_outcomes(choice_index),
                "recommendations": self._generate_recommendations(choice_index),
                "risk_assessment": self._generate_risk_assessment(choice_index),
                "long_term_impact": self._generate_long_term_impact(choice_index)
            }
            
            # Transition to report screen
            self.game.current_state = self.game.SIMULATION_REPORT
            self.game.set_status(f"Choice {choice_label} selected - Report generated", GREEN)
            
        except Exception as e:
            print(f"Error processing simulation choice: {e}")
            self.game.set_status(f"Error: {str(e)}", RED)
    
    def _generate_choice_outcomes(self, choice_index):
        """Generate outcomes based on the chosen option."""
        if choice_index == 0:  # Conservative approach
            return [
                "Stable progression in your career path",
                "Limited initial financial growth but consistent returns",
                "Lower stress levels due to reduced uncertainty",
                "Improved work-life balance in the short term"
            ]
        else:  # Bold approach
            return [
                "Accelerated career advancement opportunities",
                "Higher potential financial rewards with increased volatility",
                "Expanded professional network and visibility",
                "Development of adaptive skills through challenging situations"
            ]
            
    def _generate_recommendations(self, choice_index):
        """Generate recommendations based on the choice."""
        if choice_index == 0:  # Conservative approach
            return [
                "Develop a 5-year skill development plan to maintain competitiveness",
                "Allocate 10-15% of resources to experimental projects",
                "Build depth in your primary expertise area",
                "Create a contingency fund for unexpected opportunities"
            ]
        else:  # Bold approach
            return [
                "Establish clear milestones and evaluation points",
                "Create a strong support network for guidance",
                "Develop stress management techniques",
                "Maintain connections to your previous career path"
            ]
            
    def _generate_risk_assessment(self, choice_index):
        """Generate risk assessment based on the choice."""
        if choice_index == 0:  # Conservative approach
            return {
                "financial_risk": "Low",
                "career_risk": "Low to Medium",
                "opportunity_cost": "Medium to High",
                "primary_concerns": [
                    "Potential for stagnation",
                    "Missing emerging opportunities",
                    "Slower skill diversification"
                ]
            }
        else:  # Bold approach
            return {
                "financial_risk": "Medium to High",
                "career_risk": "Medium to High",
                "opportunity_cost": "Low",
                "primary_concerns": [
                    "Initial adjustment period challenges",
                    "Potential for burnout if not managed",
                    "Higher variability in outcomes"
                ]
            }
            
    def _generate_long_term_impact(self, choice_index):
        """Generate long-term impact assessment based on the choice."""
        if choice_index == 0:  # Conservative approach
            return {
                "career_trajectory": "Steady upward progression with predictable milestones",
                "skill_development": "Deep expertise in specific domains",
                "work_life_balance": "More consistent and predictable",
                "satisfaction_factors": [
                    "Stability and security",
                    "Mastery of specific skills",
                    "Consistent work environment"
                ]
            }
        else:  # Bold approach
            return {
                "career_trajectory": "Non-linear with potential for rapid advancement",
                "skill_development": "Broader skill set with adaptability focus",
                "work_life_balance": "More variable, requiring intentional management",
                "satisfaction_factors": [
                    "Novel experiences and challenges",
                    "Diverse network connections",
                    "Potential for breakthrough achievements"
                ]
            } 