"""
Scenario Service module for the Decision Game.
This module handles scenario-related operations.
"""

import datetime
from bson import ObjectId

class ScenarioService:
    """Service for scenario-related functionality."""
    
    def __init__(self, db_manager, ai_service):
        """
        Initialize the scenario service.
        
        Args:
            db_manager: The database manager instance
            ai_service: The AI service instance
        """
        self.db_manager = db_manager
        self.ai_service = ai_service
    
    def analyze_scenario(self, scenario_text, user_id=None):
        """
        Analyze a scenario using the AI service and save it if a user is provided.
        
        Args:
            scenario_text: The scenario text to analyze
            user_id: Optional user ID to associate with the scenario
            
        Returns:
            Analysis results from the AI service
        """
        # Calculate word count for indexing by length
        word_count = len(scenario_text.split())
        
        # Get analysis from AI service
        analysis_results = self.ai_service.analyze_scenario(scenario_text)
        
        # Save the scenario if user_id is provided
        if user_id:
            try:
                # Save to database
                self.save_scenario_analysis(user_id, scenario_text, analysis_results, word_count)
            except Exception as e:
                print(f"Error saving scenario: {e}")
                # Continue anyway since we have the analysis
        
        return analysis_results
    
    def save_scenario_analysis(self, user_id, scenario_text, analysis_results, word_count=None):
        """
        Save scenario analysis to the database.
        
        Args:
            user_id: The user ID
            scenario_text: The scenario text
            analysis_results: The analysis results
            word_count: Optional word count (calculated if not provided)
            
        Returns:
            The scenario ID
        """
        if word_count is None:
            word_count = len(scenario_text.split())
            
        # Create scenario document
        scenario = {
            "user_id": user_id,
            "scenario_text": scenario_text,
            "analysis": analysis_results,
            "word_count": word_count,
            "analysis_date": datetime.datetime.now()
        }
        
        try:
            if hasattr(self.db_manager, 'use_local_storage') and self.db_manager.use_local_storage:
                # Generate ID for local storage
                import uuid
                scenario_id = str(uuid.uuid4())
                scenario["_id"] = scenario_id
                
                # Store in local storage
                self.db_manager.local_scenarios.append(scenario)
                return scenario_id
                
            # Store in MongoDB
            result = self.db_manager.db.scenarios.insert_one(scenario)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error saving scenario: {e}")
            return None
    
    def get_user_scenarios(self, user_id, limit=10, skip=0):
        """
        Get scenarios for a user, ordered by date.
        
        Args:
            user_id: The user ID
            limit: Maximum number of results
            skip: Number of results to skip
            
        Returns:
            List of scenario documents
        """
        try:
            if hasattr(self.db_manager, 'use_local_storage') and self.db_manager.use_local_storage:
                # Filter and sort local scenarios
                user_scenarios = [s for s in self.db_manager.local_scenarios 
                                 if s.get("user_id") == user_id]
                
                # Sort by date
                sorted_scenarios = sorted(
                    user_scenarios, 
                    key=lambda x: x.get("analysis_date", datetime.datetime.min),
                    reverse=True
                )
                
                # Apply pagination
                return sorted_scenarios[skip:skip+limit]
            
            # Convert string ID to ObjectId if needed
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Use compound index for efficient querying
            return list(self.db_manager.db.scenarios.find(
                {"user_id": user_id}
            ).sort(
                "analysis_date", -1
            ).skip(skip).limit(limit))
            
        except Exception as e:
            print(f"Error getting user scenarios: {e}")
            return []
    
    def get_scenarios_by_word_count(self, user_id, limit=20, descending=True):
        """
        Get scenarios for a user, ordered by word count.
        
        Args:
            user_id: The user ID
            limit: Maximum number of results
            descending: Whether to sort in descending order
            
        Returns:
            List of scenario documents
        """
        try:
            if hasattr(self.db_manager, 'use_local_storage') and self.db_manager.use_local_storage:
                # Filter local scenarios
                user_scenarios = [s for s in self.db_manager.local_scenarios 
                                 if s.get("user_id") == user_id]
                
                # Sort by word count
                sort_direction = -1 if descending else 1
                sorted_scenarios = sorted(
                    user_scenarios, 
                    key=lambda x: x.get("word_count", 0) * sort_direction
                )
                
                # Apply limit
                return sorted_scenarios[:limit]
            
            # Convert string ID to ObjectId if needed
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
                
            # Use the word_count index for efficient sorting
            sort_direction = -1 if descending else 1
            return list(self.db_manager.db.scenarios.find(
                {"user_id": user_id}
            ).sort(
                "word_count", sort_direction
            ).limit(limit))
            
        except Exception as e:
            print(f"Error getting scenarios by word count: {e}")
            return []
    
    def search_scenarios(self, user_id, keyword, limit=10):
        """
        Search for scenarios containing a keyword.
        
        Args:
            user_id: The user ID
            keyword: The keyword to search for
            limit: Maximum number of results
            
        Returns:
            List of matching scenario documents
        """
        try:
            if hasattr(self.db_manager, 'use_local_storage') and self.db_manager.use_local_storage:
                # Simple text search in local storage
                keyword = keyword.lower()
                matching_scenarios = [
                    s for s in self.db_manager.local_scenarios 
                    if s.get("user_id") == user_id and 
                    keyword in s.get("scenario_text", "").lower()
                ]
                
                # Apply limit
                return matching_scenarios[:limit]
            
            # Convert string ID to ObjectId if needed
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
                
            # Use text index for efficient searching
            return list(self.db_manager.db.scenarios.find(
                {
                    "$and": [
                        {"user_id": user_id},
                        {"$text": {"$search": keyword}}
                    ]
                },
                {"score": {"$meta": "textScore"}}
            ).sort(
                [("score", {"$meta": "textScore"})]
            ).limit(limit))
            
        except Exception as e:
            print(f"Error searching scenarios: {e}")
            return [] 