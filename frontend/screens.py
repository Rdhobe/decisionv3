"""
Game screens module for the Decision Game.
This module contains the GameScreens class that handles drawing all screens.
"""

import pygame
import sys
from datetime import datetime
from frontend.ui import (
    Button, TextBox, Label, Panel, ScrollArea,
    WHITE, BLACK, GRAY, BLUE, RED, GREEN, LIGHT_GRAY, DARK_GRAY, YELLOW,
    PRIMARY, PRIMARY_LIGHT, PRIMARY_DARK, SECONDARY, ACCENT,
    POP_PURPLE, POP_PINK, POP_YELLOW, GRADIENT_TOP, GRADIENT_BOTTOM, PANEL_RADIUS
)
import math

class GameScreens:
    """Handles drawing all game screens."""
    
    def __init__(self, game):
        """
        Initialize with a reference to the main game object.
        
        Args:
            game: The main DecisionGame instance
        """
        self.game = game
    
    def draw_main_menu(self):
        """Draw the main menu screen."""
        # Draw title
        title_text = self.game.font_title.render("Decision Game", True, PRIMARY)
        title_rect = title_text.get_rect(center=(self.game.width // 2, 100))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = self.game.font_medium.render("Make better decisions", True, PRIMARY_DARK)
        subtitle_rect = subtitle_text.get_rect(center=(self.game.width // 2, 150))
        self.game.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw menu buttons
        self.game.login_button.draw(self.game.screen)
        self.game.register_button.draw(self.game.screen)
        self.game.guest_button.draw(self.game.screen)
        self.game.quit_button.draw(self.game.screen)
    
    def draw_login_screen(self):
        """Draw the login screen."""
        # Draw title
        title_text = self.game.font_large.render("Login", True, PRIMARY)
        title_rect = title_text.get_rect(center=(self.game.width // 2, 100))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw input fields
        self.game.username_box.draw(self.game.screen)
        self.game.password_box.draw(self.game.screen)
        
        # Draw buttons
        self.game.login_submit_button.draw(self.game.screen)
        self.game.back_button.draw(self.game.screen)
    
    def draw_register_screen(self):
        """Draw the registration screen."""
        # Draw title
        title_text = self.game.font_large.render("Register", True, PRIMARY)
        title_rect = title_text.get_rect(center=(self.game.width // 2, 80))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw input fields
        self.game.register_username_box.draw(self.game.screen)
        self.game.register_email_box.draw(self.game.screen)
        self.game.register_fullname_box.draw(self.game.screen)
        self.game.register_password_box.draw(self.game.screen)
        
        # Draw buttons
        self.game.register_submit_button.draw(self.game.screen)
        self.game.back_button.draw(self.game.screen)
    
    def draw_scenario_screen(self):
        """Draw the scenario screen."""
        width, height = self.game.width, self.game.height
        
        # Draw the title
        title_text = "Welcome, " + self.game.user
        title_surface = self.game.font_large.render(title_text, True, (75, 100, 255))
        title_rect = title_surface.get_rect(center=(width // 2, 80))
        self.game.screen.blit(title_surface, title_rect)
        
        # Draw scenario input instructions
        instr_text = "Enter your decision scenario below:"
        instr_surface = self.game.font_medium.render(instr_text, True, (0, 0, 0))
        instr_rect = instr_surface.get_rect(center=(width // 2, 130))
        self.game.screen.blit(instr_surface, instr_rect)
        
        # Draw scenario input box
        if hasattr(self.game, 'scenario_input_box'):
            self.game.scenario_input_box.draw(self.game.screen)
        
        # Draw navigation and action buttons
        # Draw the main action button (Let's Talk) for all users
        if hasattr(self.game, 'lets_talk_button'):
            self.game.lets_talk_button.draw(self.game.screen)
            
        if hasattr(self.game, 'voice_button'):
            self.game.voice_button.draw(self.game.screen)
            
        if hasattr(self.game, 'settings_button'):
            self.game.settings_button.draw(self.game.screen)
        
        # Draw buttons based on user type
        if self.game.user == "Guest":
            # For guest users, show login and back buttons
            if hasattr(self.game, 'scenario_login_button'):
                self.game.scenario_login_button.draw(self.game.screen)
                
            if hasattr(self.game, 'scenario_back_button'):
                self.game.scenario_back_button.draw(self.game.screen)
        else:
            # For logged in users, show advanced features
            if hasattr(self.game, 'personality_button'):
                self.game.personality_button.draw(self.game.screen)
                
            if hasattr(self.game, 'simulation_button'):
                self.game.simulation_button.draw(self.game.screen)
                
            if hasattr(self.game, 'history_button'):
                self.game.history_button.draw(self.game.screen)
                
            if hasattr(self.game, 'logout_button'):
                self.game.logout_button.draw(self.game.screen)
    
    def draw_lets_talk_screen(self):
        """Draw the conversation screen."""
        # Draw title
        title_text = self.game.font_large.render("Let's Talk Through Your Decision", True, PRIMARY)
        title_rect = title_text.get_rect(center=(self.game.width // 2, 80))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw back button
        self.game.back_button.draw(self.game.screen)
        
        # If conversation is complete, show summary
        if self.game.conversation_complete:
            self._draw_conversation_summary()
        else:
            self._draw_conversation_questions()
    
    def _draw_conversation_questions(self):
        """Draw the conversation questions and input area."""
        # Draw current question
        if self.game.conversation_questions and self.game.current_question_index < len(self.game.conversation_questions):
            question = self.game.conversation_questions[self.game.current_question_index]
            
            # Create a rectangle for the question area
            question_rect = pygame.Rect(150, 150, 700, 100)
            
            # Draw the wrapped text
            self.game.draw_wrapped_text(question, self.game.font_medium, question_rect, PRIMARY_DARK)
            
            # Draw input box for response
            if hasattr(self.game, 'response_input'):
                self.game.response_input.draw(self.game.screen)
            
            # Draw navigation buttons
            self.game.next_question_button.draw(self.game.screen)
            if hasattr(self.game, 'previous_question_button'):
                self.game.previous_question_button.draw(self.game.screen)
    
    def _draw_conversation_summary(self):
        """Draw the conversation summary."""
        summary = self.game.conversation_summary
        
        # Draw summary panel
        summary_panel = pygame.Rect(150, 150, 700, 300)
        pygame.draw.rect(self.game.screen, WHITE, summary_panel)
        pygame.draw.rect(self.game.screen, PRIMARY, summary_panel, 2)
        
        # Draw clarity level
        clarity_text = f"Decision Clarity: {summary.get('clarity_level', 'Moderate')}"
        clarity_surface = self.game.font_medium.render(clarity_text, True, PRIMARY)
        clarity_rect = clarity_surface.get_rect(topleft=(170, 170))
        self.game.screen.blit(clarity_surface, clarity_rect)
        
        # Draw key insights
        insights_text = "Key Insights:"
        insights_surface = self.game.font_medium.render(insights_text, True, DARK_GRAY)
        self.game.screen.blit(insights_surface, (170, 210))
        
        for i, insight in enumerate(summary.get('key_insights', [])):
            insight_surface = self.game.font_small.render(f"• {insight}", True, BLACK)
            self.game.screen.blit(insight_surface, (190, 240 + i * 25))
        
        # Draw next steps
        steps_text = "Suggested Next Steps:"
        steps_surface = self.game.font_medium.render(steps_text, True, DARK_GRAY)
        self.game.screen.blit(steps_surface, (170, 330))
        
        for i, step in enumerate(summary.get('suggested_next_steps', [])):
            step_surface = self.game.font_small.render(f"• {step}", True, BLACK)
            self.game.screen.blit(step_surface, (190, 360 + i * 25))
        
        # Draw buttons
        self.game.explore_more_button.draw(self.game.screen)
        self.game.new_topic_button.draw(self.game.screen)
        
        # Draw download button if logged in
        if self.game.user and self.game.user != "Guest":
            self.game.download_conversation_button.draw(self.game.screen)
    
    def draw_history_screen(self):
        """Draw the decision history screen."""
        # Draw title
        title_text = self.game.font_large.render("Your Decision History", True, PRIMARY)
        title_rect = title_text.get_rect(center=(self.game.width // 2, 80))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw back button
        self.game.history_back_button.draw(self.game.screen)
        
        # Draw history items in a scroll area
        if hasattr(self.game, 'history_scroll_area'):
            self.game.history_scroll_area.draw(self.game.screen)
    
    def draw_settings_screen(self):
        """Draw the settings screen."""
        # Draw title
        title_text = self.game.font_large.render("Settings", True, PRIMARY)
        title_rect = title_text.get_rect(center=(self.game.width // 2, 80))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw back button
        self.game.settings_back_button.draw(self.game.screen)
        
        # Draw dark mode toggle
        dark_mode_label = self.game.font_medium.render("Dark Mode:", True, DARK_GRAY)
        self.game.screen.blit(dark_mode_label, (300, 200))
        
        dark_mode_status = "ON" if self.game.dark_mode else "OFF"
        self.game.dark_mode_button.text = dark_mode_status
        self.game.dark_mode_button.draw(self.game.screen)
        
        # Draw sound settings
        sound_label = self.game.font_medium.render("Sound:", True, DARK_GRAY)
        self.game.screen.blit(sound_label, (300, 260))
        
        self.game.sound_button.draw(self.game.screen)
    
    def draw_personality_test_screen(self):
        """Draw the personality test screen."""
        # Draw title
        title_text = self.game.font_large.render("Personality Test", True, PRIMARY)
        title_rect = title_text.get_rect(center=(self.game.width // 2, 80))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw back button
        self.game.personality_back_button.draw(self.game.screen)
        
        # Check if questions have been loaded
        if hasattr(self.game, 'mbti_questions') and self.game.mbti_questions:
            # Draw progress label
            if hasattr(self.game, 'mbti_progress_label'):
                self.game.mbti_progress_label.draw(self.game.screen)
            
            # Only process if we have a valid index
            if (self.game.current_mbti_index < len(self.game.mbti_questions)):
                # Get current question
                question = self.game.mbti_questions[self.game.current_mbti_index]
                
                # Draw question panel
                question_panel = pygame.Rect(200, 150, 600, 100)
                pygame.draw.rect(self.game.screen, WHITE, question_panel)
                pygame.draw.rect(self.game.screen, PRIMARY, question_panel, 2)
                
                # Draw question text
                question_text = question.get('question', 'No question found')
                self.game.draw_wrapped_text(question_text, self.game.font_medium, 
                                          pygame.Rect(220, 170, 560, 80), PRIMARY_DARK)
                
                # Draw option buttons for current question only
                options = question.get('options', [])
                if hasattr(self.game, 'mbti_option_buttons'):
                    for i, option in enumerate(options):
                        if i < len(self.game.mbti_option_buttons):
                            # Update button text and draw for this specific question
                            self.game.mbti_option_buttons[i].text = option
                            self.game.mbti_option_buttons[i].draw(self.game.screen)
            elif self.game.current_mbti_index >= len(self.game.mbti_questions):
                # All questions have been answered, show loading message before results
                loading_text = self.game.font_medium.render("Processing your answers...", True, PRIMARY)
                loading_rect = loading_text.get_rect(center=(self.game.width // 2, 300))
                self.game.screen.blit(loading_text, loading_rect)
        else:
            # Draw loading message
            loading_text = self.game.font_medium.render("Loading personality test questions...", True, DARK_GRAY)
            loading_rect = loading_text.get_rect(center=(self.game.width // 2, 300))
            self.game.screen.blit(loading_text, loading_rect)
    
    def draw_personality_result_screen(self):
        """Draw the personality test results screen."""
        # Draw title
        title_text = self.game.font_large.render("Your Personality Results", True, PRIMARY)
        title_rect = title_text.get_rect(center=(self.game.width // 2, 80))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw back button
        self.game.personality_back_button.draw(self.game.screen)
        
        # Check if results are available
        if hasattr(self.game, 'mbti_result') and self.game.mbti_result:
            result = self.game.mbti_result
            
            # Draw type
            type_code = result.get('type', 'UNKNOWN')
            type_text = self.game.font_title.render(type_code, True, PRIMARY)
            type_rect = type_text.get_rect(center=(self.game.width // 2, 140))
            self.game.screen.blit(type_text, type_rect)
            
            # Draw description
            desc_rect = pygame.Rect(150, 180, 700, 80)
            desc_text = result.get('description', 'No description available')
            self.game.draw_wrapped_text(desc_text, self.game.font_medium, desc_rect, DARK_GRAY)
            
            # Draw strengths and weaknesses
            strength_title = self.game.font_medium.render("Strengths:", True, GREEN)
            self.game.screen.blit(strength_title, (150, 270))
            
            strengths = result.get('strengths', [])
            for i, strength in enumerate(strengths[:5]):  # Limit to 5 strengths
                strength_text = self.game.font_small.render(f"• {strength}", True, DARK_GRAY)
                self.game.screen.blit(strength_text, (170, 300 + i * 25))
            
            weakness_title = self.game.font_medium.render("Growth Areas:", True, SECONDARY)
            self.game.screen.blit(weakness_title, (500, 270))
            
            weaknesses = result.get('weaknesses', [])
            for i, weakness in enumerate(weaknesses[:5]):  # Limit to 5 weaknesses
                weakness_text = self.game.font_small.render(f"• {weakness}", True, DARK_GRAY)
                self.game.screen.blit(weakness_text, (520, 300 + i * 25))
            
            # Draw career matches
            career_title = self.game.font_medium.render("Career Matches:", True, BLUE)
            self.game.screen.blit(career_title, (150, 430))
            
            careers = result.get('career_matches', [])
            for i, career in enumerate(careers[:5]):  # Limit to 5 careers
                career_text = self.game.font_small.render(f"• {career}", True, DARK_GRAY)
                self.game.screen.blit(career_text, (170, 460 + i * 25))
            
            # Draw download button if logged in
            if self.game.user and self.game.user != "Guest":
                self.game.download_personality_button.draw(self.game.screen)
        else:
            # Draw loading message
            loading_text = self.game.font_medium.render("Analyzing your personality...", True, PRIMARY)
            loading_rect = loading_text.get_rect(center=(self.game.width // 2, 300))
            self.game.screen.blit(loading_text, loading_rect)
    
    def draw_simulation_screen(self):
        """Draw the simulation scenarios screen."""
        # Draw title
        title_text = self.game.font_large.render("Decision Simulations", True, PRIMARY)
        title_rect = title_text.get_rect(center=(self.game.width // 2, 80))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw back button
        self.game.simulation_back_button.draw(self.game.screen)
        
        # Draw simulation scenarios
        if hasattr(self.game, 'simulation_scenarios') and self.game.simulation_scenarios:
            for scenario in self.game.simulation_scenarios:
                if "button" in scenario:
                    scenario["button"].draw(self.game.screen)
        else:
            # Draw loading message
            loading_text = self.game.font_medium.render("Loading simulations...", True, DARK_GRAY)
            loading_rect = loading_text.get_rect(center=(self.game.width // 2, 300))
            self.game.screen.blit(loading_text, loading_rect)
    
    def draw_simulation_result_screen(self):
        """Draw the simulation results screen."""
        # Draw title
        title_text = self.game.font_large.render("Simulation Results", True, PRIMARY)
        title_rect = title_text.get_rect(center=(self.game.width // 2, 80))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw back button
        self.game.simulation_back_button.draw(self.game.screen)
        
        # Check if current user is a guest
        if self.game.user == "Guest":
            # Draw message explaining this feature is for registered users only
            message = "Full simulation features are only available for registered users."
            explanation = "Please create an account to access advanced features."
            
            message_text = self.game.font_medium.render(message, True, YELLOW)
            explanation_text = self.game.font_medium.render(explanation, True, DARK_GRAY)
            
            message_rect = message_text.get_rect(center=(self.game.width // 2, 250))
            explanation_rect = explanation_text.get_rect(center=(self.game.width // 2, 300))
            
            self.game.screen.blit(message_text, message_rect)
            self.game.screen.blit(explanation_text, explanation_rect)
            
            # Add login button
            if hasattr(self.game, 'scenario_login_button'):
                login_button = Button(
                    self.game.width // 2, 380,
                    200, 50,
                    "Login / Register",
                    color=PRIMARY_LIGHT,
                    hover_color=PRIMARY
                )
                login_button.draw(self.game.screen)
                self.game.simulation_login_button = login_button
            
        # Check if simulation results are available
        elif hasattr(self.game, 'current_simulation') and self.game.current_simulation:
            # Draw the simulation scenario
            scenario = self.game.current_simulation
            
            # Draw scenario title
            scenario_title = self.game.font_medium.render(scenario.get("title", "Unnamed Scenario"), True, PRIMARY_DARK)
            title_rect = scenario_title.get_rect(center=(self.game.width // 2, 150))
            self.game.screen.blit(scenario_title, title_rect)
            
            # Draw scenario description
            description = scenario.get("description", "No description available.")
            desc_rect = pygame.Rect(150, 180, 700, 100)
            self.game.draw_wrapped_text(description, self.game.font_small, desc_rect, DARK_GRAY)
            
            # Draw simulation panel
            panel_rect = pygame.Rect(150, 250, 700, 300)
            pygame.draw.rect(self.game.screen, WHITE, panel_rect)
            pygame.draw.rect(self.game.screen, PRIMARY, panel_rect, 2)
            
            # Draw scenario content
            content_text = "This simulation would show different choices and potential outcomes."
            content_text2 = "In a full implementation, you would see decision paths and consequences."
            
            content1 = self.game.font_medium.render(content_text, True, DARK_GRAY)
            content2 = self.game.font_medium.render(content_text2, True, DARK_GRAY)
            
            content1_rect = content1.get_rect(center=(self.game.width // 2, 300))
            content2_rect = content2.get_rect(center=(self.game.width // 2, 340))
            
            self.game.screen.blit(content1, content1_rect)
            self.game.screen.blit(content2, content2_rect)
            
            # Draw choices
            choice1_button = Button(
                self.game.width // 2 - 180, 420,
                300, 50,
                "Choice A: Conservative Approach",
                color=PRIMARY_LIGHT,
                hover_color=PRIMARY
            )
            
            choice2_button = Button(
                self.game.width // 2 + 180, 420,
                300, 50,
                "Choice B: Bold Approach",
                color=SECONDARY,
                hover_color=(255, 120, 0)
            )
            
            choice1_button.draw(self.game.screen)
            choice2_button.draw(self.game.screen)
            
            # Store buttons for event handling
            self.game.simulation_choice_buttons = [choice1_button, choice2_button]
            
        else:
            # Draw loading message
            loading_text = self.game.font_medium.render("Loading simulation results...", True, DARK_GRAY)
            loading_rect = loading_text.get_rect(center=(self.game.width // 2, 300))
            self.game.screen.blit(loading_text, loading_rect)
    
    def draw_simulation_report_screen(self):
        """Draw the simulation report screen that shows detailed results."""
        # Draw title
        title_text = self.game.font_large.render("Simulation Report", True, PRIMARY)
        title_rect = title_text.get_rect(center=(self.game.width // 2, 60))
        self.game.screen.blit(title_text, title_rect)
        
        # Check if we have a simulation report
        if hasattr(self.game, 'simulation_report') and self.game.simulation_report:
            report = self.game.simulation_report
            
            # Draw scenario title and choice made
            scenario_title = self.game.font_medium.render(report.get("scenario_title", "Unnamed Scenario"), True, PRIMARY_DARK)
            choice_text = self.game.font_medium.render(f"Choice: {report.get('choice', 'Unknown')}", True, SECONDARY)
            
            title_rect = scenario_title.get_rect(center=(self.game.width // 2, 100))
            choice_rect = choice_text.get_rect(center=(self.game.width // 2, 130))
            
            self.game.screen.blit(scenario_title, title_rect)
            self.game.screen.blit(choice_text, choice_rect)
            
            # Draw date
            date_text = self.game.font_small.render(f"Date: {report.get('date', 'Unknown')}", True, DARK_GRAY)
            date_rect = date_text.get_rect(topright=(self.game.width - 50, 80))
            self.game.screen.blit(date_text, date_rect)
            
            # Draw report content
            self._draw_simulation_report_content(report)
            
            # Draw action buttons
            if not hasattr(self.game, 'simulation_report_back_button'):
                self.game.simulation_report_back_button = Button(
                    150, 520,
                    150, 50,
                    "Back",
                    color=GRAY,
                    hover_color=DARK_GRAY
                )
                
            if not hasattr(self.game, 'simulation_try_again_button'):
                self.game.simulation_try_again_button = Button(
                    self.game.width // 2, 520,
                    150, 50,
                    "Try Again",
                    color=PRIMARY_LIGHT,
                    hover_color=PRIMARY
                )
                
            if not hasattr(self.game, 'download_simulation_button'):
                self.game.download_simulation_button = Button(
                    self.game.width - 150, 520,
                    200, 50,
                    "Download Report",
                    color=SECONDARY,
                    hover_color=(255, 120, 0)
                )
            
            # Only show download button for registered users
            self.game.simulation_report_back_button.draw(self.game.screen)
            self.game.simulation_try_again_button.draw(self.game.screen)
            
            if self.game.user and self.game.user != "Guest":
                self.game.download_simulation_button.draw(self.game.screen)
        else:
            # Show error message if no report is available
            error_text = self.game.font_medium.render("No simulation report available", True, RED)
            error_rect = error_text.get_rect(center=(self.game.width // 2, 300))
            self.game.screen.blit(error_text, error_rect)
            
            # Add a button to go back
            if not hasattr(self.game, 'simulation_report_back_button'):
                self.game.simulation_report_back_button = Button(
                    self.game.width // 2, 400,
                    150, 50,
                    "Back",
                    color=GRAY,
                    hover_color=DARK_GRAY
                )
            self.game.simulation_report_back_button.draw(self.game.screen)
    
    def _draw_simulation_report_content(self, report):
        """Draw the detailed content of the simulation report."""
        # Create the main panel for the report
        panel_rect = pygame.Rect(50, 160, self.game.width - 100, 340)
        pygame.draw.rect(self.game.screen, WHITE, panel_rect)
        pygame.draw.rect(self.game.screen, PRIMARY, panel_rect, 2)
        
        # Draw the outcomes section
        if 'outcomes' in report:
            section_title = self.game.font_medium.render("Key Outcomes", True, PRIMARY_DARK)
            self.game.screen.blit(section_title, (70, 180))
            
            for i, outcome in enumerate(report['outcomes']):
                outcome_text = self.game.font_small.render(f"• {outcome}", True, DARK_GRAY)
                self.game.screen.blit(outcome_text, (90, 210 + i * 22))
        
        # Draw the recommendations section
        if 'recommendations' in report:
            section_title = self.game.font_medium.render("Recommendations", True, PRIMARY_DARK)
            self.game.screen.blit(section_title, (70, 300))
            
            for i, rec in enumerate(report['recommendations']):
                rec_text = self.game.font_small.render(f"• {rec}", True, DARK_GRAY)
                self.game.screen.blit(rec_text, (90, 330 + i * 22))
        
        # Draw risk assessment
        if 'risk_assessment' in report:
            risk = report['risk_assessment']
            section_title = self.game.font_medium.render("Risk Assessment", True, PRIMARY_DARK)
            self.game.screen.blit(section_title, (500, 180))
            
            # Draw risk levels
            fin_risk = self.game.font_small.render(f"Financial Risk: {risk.get('financial_risk', 'Unknown')}", True, DARK_GRAY)
            car_risk = self.game.font_small.render(f"Career Risk: {risk.get('career_risk', 'Unknown')}", True, DARK_GRAY)
            opp_cost = self.game.font_small.render(f"Opportunity Cost: {risk.get('opportunity_cost', 'Unknown')}", True, DARK_GRAY)
            
            self.game.screen.blit(fin_risk, (520, 210))
            self.game.screen.blit(car_risk, (520, 232))
            self.game.screen.blit(opp_cost, (520, 254))
            
            # Draw concerns
            concerns_title = self.game.font_small.render("Primary Concerns:", True, DARK_GRAY)
            self.game.screen.blit(concerns_title, (520, 276))
            
            for i, concern in enumerate(risk.get('primary_concerns', [])):
                concern_text = self.game.font_small.render(f"• {concern}", True, DARK_GRAY)
                self.game.screen.blit(concern_text, (540, 298 + i * 22))
        
        # Draw long-term impact summary
        if 'long_term_impact' in report:
            impact = report['long_term_impact']
            section_title = self.game.font_medium.render("Long-Term Impact", True, PRIMARY_DARK)
            self.game.screen.blit(section_title, (500, 380))
            
            # Draw key points
            career = self.game.font_small.render("Career Path: " + impact.get('career_trajectory', '')[:20] + "...", True, DARK_GRAY)
            skills = self.game.font_small.render("Skills: " + impact.get('skill_development', '')[:20] + "...", True, DARK_GRAY)
            balance = self.game.font_small.render("Work-Life: " + impact.get('work_life_balance', '')[:20] + "...", True, DARK_GRAY)
            
            self.game.screen.blit(career, (520, 410))
            self.game.screen.blit(skills, (520, 432))
            self.game.screen.blit(balance, (520, 454))
    
    def draw_loading_screen(self):
        """Draw the loading screen."""
        # Use background color based on dark mode
        bg_color = (30, 30, 40) if self.game.dark_mode else (245, 245, 255)
        text_color = WHITE if self.game.dark_mode else BLACK
        
        # Fill background
        self.game.screen.fill(bg_color)
        
        # Center of screen
        center_x = self.game.width // 2
        center_y = self.game.height // 2
        
        # Draw loading title
        title_text = self.game.font_large.render("LOADING", True, PRIMARY)
        title_rect = title_text.get_rect(center=(center_x, center_y - 100))
        self.game.screen.blit(title_text, title_rect)
        
        # Draw loading message
        message_text = self.game.font_medium.render(self.game.loading_message, True, text_color)
        message_rect = message_text.get_rect(center=(center_x, center_y - 40))
        self.game.screen.blit(message_text, message_rect)
        
        # Draw animated loading spinner
        spinner_radius = 20
        angle = (pygame.time.get_ticks() % 2000) / 2000 * 360  # Full rotation every 2 seconds
        
        # Draw dots in a circle with the current active dot highlighted
        num_dots = 8
        dot_radius = 6
        for i in range(num_dots):
            dot_angle = i * (360 / num_dots) + angle
            dot_x = center_x + int(spinner_radius * math.cos(math.radians(dot_angle)))
            dot_y = center_y + int(spinner_radius * math.sin(math.radians(dot_angle)))
            
            # Make the current dot in the animation sequence highlighted
            if i == self.game.loading_animation_frames:
                # Current dot is larger and brighter
                pygame.draw.circle(self.game.screen, PRIMARY, (dot_x, dot_y), dot_radius + 2)
            else:
                # Other dots are smaller and dimmer
                pygame.draw.circle(self.game.screen, DARK_GRAY, (dot_x, dot_y), dot_radius)
        
        # Draw progress bar
        bar_width = 400
        bar_height = 20
        progress = self.game.loading_progress
        
        # Draw progress bar background
        bar_bg_rect = pygame.Rect(center_x - bar_width // 2, center_y + 50, bar_width, bar_height)
        pygame.draw.rect(self.game.screen, DARK_GRAY, bar_bg_rect, border_radius=bar_height // 2)
        
        # Draw progress bar fill
        if progress > 0:
            fill_width = int(bar_width * progress / 100)
            bar_fill_rect = pygame.Rect(center_x - bar_width // 2, center_y + 50, fill_width, bar_height)
            
            # Use gradient for progress bar
            if self.game.loading_completed:
                # Green for completed
                bar_color = GREEN  # Using GREEN instead of SUCCESS
            else:
                # Blue for in progress
                bar_color = PRIMARY
                
            pygame.draw.rect(self.game.screen, bar_color, bar_fill_rect, border_radius=bar_height // 2)
        
        # Draw percentage text
        percentage_text = self.game.font_small.render(f"{progress}%", True, text_color)
        percentage_rect = percentage_text.get_rect(center=(center_x, center_y + 50 + bar_height // 2))
        self.game.screen.blit(percentage_text, percentage_rect)
        
        # Draw tip at bottom
        tip_text = "Please wait while we process your request..."
        tip_surface = self.game.font_small.render(tip_text, True, text_color)
        tip_rect = tip_surface.get_rect(center=(center_x, center_y + 150))
        self.game.screen.blit(tip_surface, tip_rect) 