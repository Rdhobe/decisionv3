"""
API Client module for the Decision Game.
This module handles communication with the backend API, MongoDB storage, and OpenAI integration.
"""

import random
from datetime import datetime
import os

from frontend.db_manager import DBManager
from frontend.user_service import UserService
from frontend.scenario_service import ScenarioService
from frontend.ai_service import AIService
import pymongo

class APIClient:
    """API client for the Decision Game with service-based architecture."""
    
    def __init__(self):
        """Initialize the API client."""
        self.base_url = ""  # This would be a real URL in production
        self.token = None
        
        # Initialize services
        self.db_manager = DBManager()
        self.ai_service = AIService()
        self.user_service = UserService(self.db_manager)
        self.scenario_service = ScenarioService(self.db_manager, self.ai_service)
    
    def login(self, username, password):
        """
        Login to the system.
        
        Args:
            username: The username
            password: The password
            
        Returns:
            A dictionary with the token if successful
        """
        return self.user_service.login(username, password)
    
    def register(self, username, email, fullname, password):
        """
        Register a new user.
        
        Args:
            username: The username
            email: The email address
            fullname: The user's full name
            password: The password
            
        Returns:
            A dictionary with status information
        """
        return self.user_service.register(username, email, fullname, password)
    
    def set_token(self, token):
        """
        Set the authentication token.
        
        Args:
            token: The authentication token
        """
        self.token = token
    
    def clear_token(self):
        """Clear the authentication token."""
        self.token = None
    
    def analyze_scenario(self, scenario_text):
        """
        Analyze scenario using the scenario service.
        
        Args:
            scenario_text: The scenario text to analyze
            
        Returns:
            A dictionary with analysis results
        """
        # Get user_id from token if available
        user_id = None
        if self.token:
            user_id = self.user_service.get_user_id_from_token(self.token)
        
        # Analyze the scenario
        return self.scenario_service.analyze_scenario(scenario_text, user_id)
    
    def get_user_id_from_token(self, token):
        """
        Get user ID from token.
        
        Args:
            token: The authentication token
            
        Returns:
            The user ID as string or None
        """
        return self.user_service.get_user_id_from_token(token)
    
    def save_scenario_analysis(self, user_id, scenario_text, analysis_results):
        """
        Save scenario analysis results.
        
        Args:
            user_id: The user ID
            scenario_text: The scenario text
            analysis_results: The analysis results
            
        Returns:
            The ID of the saved scenario
        """
        return self.scenario_service.save_scenario_analysis(
            user_id, scenario_text, analysis_results)
    
    def get_user_scenarios(self, user_id, limit=10, skip=0):
        """
        Get user scenarios sorted by date.
        
        Args:
            user_id: The user ID
            limit: Maximum number of scenarios to return
            skip: Number of scenarios to skip
            
        Returns:
            A list of scenario documents
        """
        return self.scenario_service.get_user_scenarios(user_id, limit, skip)
    
    def get_scenarios_by_word_count(self, user_id, limit=20, descending=True):
        """
        Get user scenarios sorted by word count.
        
        Args:
            user_id: The user ID
            limit: Maximum number of scenarios to return
            descending: Whether to sort in descending order
            
        Returns:
            A list of scenario documents
        """
        return self.scenario_service.get_scenarios_by_word_count(user_id, limit, descending)
    
    def search_scenarios(self, user_id, keyword, limit=10):
        """
        Search for scenarios containing a keyword.
        
        Args:
            user_id: The user ID
            keyword: The keyword to search for
            limit: Maximum number of results to return
            
        Returns:
            A list of matching scenario documents
        """
        return self.scenario_service.search_scenarios(user_id, keyword, limit)
    
    def get_mbti_questions(self):
        """
        Get MBTI questions using the AI service.
        
        Returns:
            A list of MBTI questions
        """
        return self.ai_service.get_mbti_questions()
    
    def submit_mbti_answers(self, answers):
        """
        Submit MBTI answers and get analysis.
        
        Args:
            answers: A dictionary mapping question IDs to answers
            
        Returns:
            A dictionary with the MBTI result
        """
        return self.ai_service.analyze_mbti_answers(answers)
    
    def get_simulation_scenarios(self):
        """
        Get simulation scenarios using the AI service.
        
        Returns:
            A list of simulation scenarios
        """
        return self.ai_service.generate_simulation_scenarios()
    
    def download_personality_report(self, mbti_result, filename):
        """
        Generate and download a personality report.
        
        Args:
            mbti_result: The MBTI result dictionary
            filename: The filename to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Implementation would go here
            return True
        except Exception as e:
            print(f"Error downloading personality report: {e}")
            return False
    
    def download_conversation_report(self, conversation_summary, filename):
        """
        Generate and download a conversation report.
        
        Args:
            conversation_summary: The conversation summary
            filename: The filename to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Implementation would go here
            return True
        except Exception as e:
            print(f"Error downloading conversation report: {e}")
            return False
    
    def get_decision_history(self):
        """
        Get decision history from MongoDB or generate with GPT-4o-mini if no history exists.
        
        Returns:
            A list of past decisions
        """
        if not self.token:
            return []
        
        # Find user ID from token
        user = self.db_manager.find_one({"token": self.token})
        if not user:
            return []
        
        # Retrieve decision history from database
        decisions = list(self.db_manager.find({"user_id": user["_id"]}))
        
        # If no history exists, generate some with GPT-4o-mini
        if not decisions:
            try:
                response = self.ai_service.generate_decision_scenarios(3)
                
                # Store generated decisions in database
                for decision in response:
                    decision["user_id"] = user["_id"]
                    self.db_manager.insert_one(decision)
                
            except Exception as e:
                print(f"Error calling OpenAI API: {e}")
                # Fallback to mock data
                decisions = [
                    {
                        "id": 1,
                        "date": "2023-06-15",
                        "scenario": "Should I accept a job offer in another city?",
                        "clarity_level": "High"
                    },
                    {
                        "id": 2,
                        "date": "2023-06-20",
                        "scenario": "Should I invest in a new business opportunity?",
                        "clarity_level": "Moderate"
                    },
                    {
                        "id": 3,
                        "date": "2023-07-05",
                        "scenario": "Should I pursue a master's degree?",
                        "clarity_level": "Excellent"
                    }
                ]
                
                # Store fallback decisions
                for decision in decisions:
                    decision["user_id"] = user["_id"]
                    self.db_manager.insert_one(decision)
        
        # Format decision data for response
        return [{
            "id": str(decision.get("_id", "")),
            "date": decision.get("date", ""),
            "scenario": decision.get("scenario", ""),
            "clarity_level": decision.get("clarity_level", "")
        } for decision in decisions]
    
    def get_simulation_series(self):
        """Get available simulation series for the user's level from MongoDB"""
        if not self.token:
            print("Not logged in")
            return []
            
        # Find user ID and level from token
        user = self.db_manager.find_one({"token": self.token})
        if not user:
            print("Invalid token")
            return []
        
        user_level = user.get("level", 1)
        
        # Get series available for user's level
        series_list = list(self.db_manager.find({"min_level": {"$lte": user_level}}))
        
        return [{
            "id": str(series["_id"]),
            "title": series.get("title", ""),
            "description": series.get("description", ""),
            "difficulty": series.get("difficulty", "Beginner"),
            "scenarios_count": series.get("scenarios_count", 0)
        } for series in series_list]
    
    def start_simulation_series(self, series_id, requires_support=False):
        """Start a simulation series and get the first scenario"""
        if not self.token:
            print("Not logged in")
            return {"detail": "Not authenticated"}
            
        # Find user ID from token
        user = self.db_manager.find_one({"token": self.token})
        if not user:
            return {"detail": "Invalid token"}
        
        try:
            # Get series info
            series = self.db_manager.find_one({"_id": pymongo.ObjectId(series_id)})
            if not series:
                return {"detail": "Series not found"}
            
            # Get first scenario in series
            first_scenario = self.db_manager.find_one({
                "series_id": pymongo.ObjectId(series_id),
                "order": 1
            })
            
            if not first_scenario:
                # Generate first scenario with GPT if none exists
                try:
                    response = self.ai_service.generate_decision_scenario(series.get('title'))
                    
                    # Create scenario in database
                    scenario_id = self.db_manager.insert_one({
                        "series_id": pymongo.ObjectId(series_id),
                        "order": 1,
                        "text": response.get("text", ""),
                        "choices": response.get("choices", []),
                        "difficulty": response.get("difficulty", "Medium"),
                        "created_at": datetime.now()
                    }).inserted_id
                    
                    # Get the inserted scenario
                    first_scenario = self.db_manager.find_one({"_id": scenario_id})
                    
                except Exception as e:
                    print(f"Error calling OpenAI API: {e}")
                    return {"detail": "Error generating scenario"}
            
            # Create user progress entry
            progress_id = self.db_manager.insert_one({
                "user_id": user["_id"],
                "series_id": pymongo.ObjectId(series_id),
                "current_scenario": 1,
                "requires_support": requires_support,
                "started_at": datetime.now(),
                "completed": False
            }).inserted_id
            
            return {
                "progress_id": str(progress_id),
                "scenario": {
                    "id": str(first_scenario["_id"]),
                    "text": first_scenario.get("text", ""),
                    "choices": first_scenario.get("choices", []),
                    "order": first_scenario.get("order", 1)
                },
                "series_title": series.get("title", "")
            }
            
        except Exception as e:
            print(f"Error starting simulation: {e}")
            return {"detail": str(e)}
    
    def make_series_choice(self, series_id, scenario_id, choice_id):
        """Make a choice in a simulation series and get the next scenario or outcome"""
        if not self.token:
            print("Not logged in")
            return {"detail": "Not authenticated"}
            
        # Find user ID from token
        user = self.db_manager.find_one({"token": self.token})
        if not user:
            return {"detail": "Invalid token"}
        
        try:
            # Record the choice
            choice_record_id = self.db_manager.insert_one({
                "user_id": user["_id"],
                "series_id": pymongo.ObjectId(series_id),
                "scenario_id": pymongo.ObjectId(scenario_id),
                "choice_id": choice_id,
                "timestamp": datetime.now()
            }).inserted_id
            
            # Get current scenario info
            current_scenario = self.db_manager.find_one({
                "_id": pymongo.ObjectId(scenario_id)
            })
            
            if not current_scenario:
                return {"detail": "Scenario not found"}
            
            # Get user progress
            progress = self.db_manager.find_one({
                "user_id": user["_id"],
                "series_id": pymongo.ObjectId(series_id),
                "completed": False
            })
            
            if not progress:
                return {"detail": "No active progress found"}
            
            # Check if this is the last scenario
            series = self.db_manager.find_one({
                "_id": pymongo.ObjectId(series_id)
            })
            
            if current_scenario.get("order", 1) >= series.get("scenarios_count", 3):
                # This was the last scenario, generate outcome
                try:
                    # Get the selected choice text
                    selected_choice = None
                    for choice in current_scenario.get("choices", []):
                        if choice.get("id") == choice_id:
                            selected_choice = choice.get("text", "")
                            break
                    
                    response = self.ai_service.generate_decision_outcome(current_scenario.get('text'), selected_choice)
                    
                    # Mark series as completed
                    self.db_manager.update_one(
                        {"_id": progress["_id"]},
                        {"$set": {"completed": True, "completed_at": datetime.now()}}
                    )
                    
                    # Award points to user
                    self.db_manager.update_one(
                        {"_id": user["_id"]},
                        {"$inc": {
                            "points": 50,
                            "scenarios_completed": series.get("scenarios_count", 3)
                        }}
                    )
                    
                    return {
                        "is_final": True,
                        "outcome": response,
                        "series_completed": True
                    }
                    
                except Exception as e:
                    print(f"Error generating outcome: {e}")
                    return {"detail": "Error generating outcome"}
            
            # Get next scenario
            next_scenario_order = current_scenario.get("order", 1) + 1
            next_scenario = self.db_manager.find_one({
                "series_id": pymongo.ObjectId(series_id),
                "order": next_scenario_order
            })
            
            if not next_scenario:
                # Generate next scenario with GPT
                try:
                    # Get the selected choice text
                    selected_choice = None
                    for choice in current_scenario.get("choices", []):
                        if choice.get("id") == choice_id:
                            selected_choice = choice.get("text", "")
                            break
                    
                    response = self.ai_service.generate_decision_follow_up(current_scenario.get('text'), selected_choice)
                    
                    # Create scenario in database
                    scenario_id = self.db_manager.insert_one({
                        "series_id": pymongo.ObjectId(series_id),
                        "order": next_scenario_order,
                        "text": response.get("text", ""),
                        "choices": response.get("choices", []),
                        "difficulty": response.get("difficulty", "Medium"),
                        "created_at": datetime.now()
                    }).inserted_id
                    
                    # Get the inserted scenario
                    next_scenario = self.db_manager.find_one({"_id": scenario_id})
                    
                except Exception as e:
                    print(f"Error calling OpenAI API: {e}")
                    return {"detail": "Error generating next scenario"}
            
            # Update user progress
            self.db_manager.update_one(
                {"_id": progress["_id"]},
                {"$set": {"current_scenario": next_scenario_order}}
            )
            
            return {
                "is_final": False,
                "next_scenario": {
                    "id": str(next_scenario["_id"]),
                    "text": next_scenario.get("text", ""),
                    "choices": next_scenario.get("choices", []),
                    "order": next_scenario.get("order", next_scenario_order)
                }
            }
            
        except Exception as e:
            print(f"Error processing choice: {e}")
            return {"detail": str(e)}
    
    def get_series_progress(self):
        """Get the user's progress in all simulation series from MongoDB"""
        if not self.token:
            print("Not logged in")
            return []
            
        # Find user ID from token
        user = self.db_manager.find_one({"token": self.token})
        if not user:
            print("Invalid token")
            return []
        
        # Get progress records
        progress_records = list(self.db_manager.find({"user_id": user["_id"]}))
        
        results = []
        for progress in progress_records:
            # Get series info
            series = self.db_manager.find_one({
                "_id": progress.get("series_id")
            })
            
            if not series:
                continue
                
            results.append({
                "series_id": str(series["_id"]),
                "title": series.get("title", ""),
                "total_scenarios": series.get("scenarios_count", 0),
                "current_scenario": progress.get("current_scenario", 1),
                "completed": progress.get("completed", False),
                "started_at": progress.get("started_at", datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                "completed_at": progress.get("completed_at", "").strftime("%Y-%m-%d %H:%M:%S") if progress.get("completed_at") else None
            })
            
        return results
    
    def get_series_leaderboard(self, series_id):
        """Get the leaderboard for a specific simulation series from MongoDB"""
        if not self.token:
            print("Not logged in")
            return []
            
        # Find user ID from token
        user = self.db_manager.find_one({"token": self.token})
        if not user:
            print("Invalid token")
            return []
            
        # Get leaderboard records
        leaderboard_records = list(self.db_manager.find({"series_id": pymongo.ObjectId(series_id)}).sort("points", pymongo.DESCENDING))

        results = []
        for record in leaderboard_records:
            user = self.db_manager.find_one({"_id": record.get("user_id")})
            if not user:
                continue
                
            results.append({
                "username": user.get("username", ""),
                "points": record.get("points", 0),
                "scenarios_completed": record.get("scenarios_completed", 0)
            })
        
        return results
    