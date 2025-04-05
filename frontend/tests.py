"""
Test module for the Decision Game.
This module contains unit tests for the various components.
"""

import unittest
import os
import sys
from unittest.mock import MagicMock, patch
from datetime import datetime

# Import application modules
from frontend.db_manager import DBManager
from frontend.user_service import UserService
from frontend.scenario_service import ScenarioService
from frontend.ai_service import AIService
from frontend.api_client import APIClient


class TestDBManager(unittest.TestCase):
    """Test cases for the database manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the MongoDB client
        self.mongo_client_mock = MagicMock()
        self.db_mock = MagicMock()
        self.mongo_client_mock.decision_game = self.db_mock
        
        # Create a patched DBManager
        with patch('pymongo.MongoClient', return_value=self.mongo_client_mock):
            self.db_manager = DBManager()
    
    def test_create_user(self):
        """Test creating a user."""
        # Prepare test data
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "fullname": "Test User",
            "password": "hashedpassword"
        }
        
        # Configure mock
        inserted_id = "61234567890abcdef1234567"
        self.db_mock.users.insert_one.return_value.inserted_id = inserted_id
        
        # Execute test
        result = self.db_manager.create_user(user_data)
        
        # Verify result
        self.assertEqual(result, inserted_id)
        self.db_mock.users.insert_one.assert_called_once_with(user_data)
    
    def test_get_user_by_username(self):
        """Test getting a user by username."""
        # Prepare test data
        username = "testuser"
        expected_user = {
            "_id": "61234567890abcdef1234567",
            "username": username,
            "email": "test@example.com"
        }
        
        # Configure mock
        self.db_mock.users.find_one.return_value = expected_user
        
        # Execute test
        result = self.db_manager.get_user_by_username(username)
        
        # Verify result
        self.assertEqual(result, expected_user)
        self.db_mock.users.find_one.assert_called_once_with({"username": username})
    
    def test_get_user_by_token(self):
        """Test getting a user by token."""
        # Prepare test data
        token = "test_token_12345"
        expected_user = {
            "_id": "61234567890abcdef1234567",
            "username": "testuser",
            "token": token
        }
        
        # Configure mock
        self.db_mock.users.find_one.return_value = expected_user
        
        # Execute test
        result = self.db_manager.get_user_by_token(token)
        
        # Verify result
        self.assertEqual(result, expected_user)
        self.db_mock.users.find_one.assert_called_once_with({"token": token})


class TestUserService(unittest.TestCase):
    """Test cases for the user service."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the database manager
        self.db_manager_mock = MagicMock()
        
        # Create UserService with mock db_manager
        self.user_service = UserService(self.db_manager_mock)
    
    def test_register_success(self):
        """Test successful user registration."""
        # Prepare test data
        username = "testuser"
        email = "test@example.com"
        fullname = "Test User"
        password = "testpassword"
        
        # Configure mock
        user_id = "61234567890abcdef1234567"
        self.db_manager_mock.create_user.return_value = user_id
        
        # Execute test
        result = self.user_service.register(username, email, fullname, password)
        
        # Verify result
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["user_id"], user_id)
        
        # Verify the password was hashed
        self.db_manager_mock.create_user.assert_called_once()
        call_args = self.db_manager_mock.create_user.call_args[0][0]
        self.assertNotEqual(call_args["password"], password)
    
    def test_register_duplicate_error(self):
        """Test registration with duplicate username/email."""
        # Prepare test data
        username = "testuser"
        email = "test@example.com"
        fullname = "Test User"
        password = "testpassword"
        
        # Configure mock to raise ValueError
        self.db_manager_mock.create_user.side_effect = ValueError("Username already exists")
        
        # Execute test
        result = self.user_service.register(username, email, fullname, password)
        
        # Verify result
        self.assertEqual(result["status_code"], 400)
        self.assertEqual(result["detail"], "Username already exists")
    
    def test_login_success(self):
        """Test successful login."""
        # Prepare test data
        username = "testuser"
        password = "testpassword"
        
        # Mock the user data
        user = {
            "_id": "61234567890abcdef1234567",
            "username": username,
            "password": self.user_service._hash_password(password)
        }
        
        # Configure mocks
        self.db_manager_mock.get_user_by_username.return_value = user
        
        # Execute test
        result = self.user_service.login(username, password)
        
        # Verify result
        self.assertIn("access_token", result)
        self.assertEqual(result["username"], username)
        self.assertEqual(result["user_id"], str(user["_id"]))
        
        # Verify token was saved
        self.db_manager_mock.update_user.assert_called_once()
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        # Prepare test data
        username = "testuser"
        password = "wrong_password"
        
        # Mock the user data
        user = {
            "_id": "61234567890abcdef1234567",
            "username": username,
            "password": self.user_service._hash_password("correct_password")
        }
        
        # Configure mocks
        self.db_manager_mock.get_user_by_username.return_value = user
        
        # Execute test
        result = self.user_service.login(username, password)
        
        # Verify result
        self.assertIn("error", result)
        
        # Verify token was NOT saved
        self.db_manager_mock.update_user.assert_not_called()


class TestScenarioService(unittest.TestCase):
    """Test cases for the scenario service."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the dependencies
        self.db_manager_mock = MagicMock()
        self.ai_service_mock = MagicMock()
        
        # Create ScenarioService with mocks
        self.scenario_service = ScenarioService(self.db_manager_mock, self.ai_service_mock)
    
    def test_analyze_scenario(self):
        """Test analyzing a scenario."""
        # Prepare test data
        scenario_text = "Should I accept a job offer in another city?"
        user_id = "61234567890abcdef1234567"
        
        # Mock AI service response
        ai_response = {
            "questions": ["Question 1", "Question 2"],
            "perspectives": ["Perspective 1", "Perspective 2"],
            "action_plan": ["Action 1", "Action 2"]
        }
        self.ai_service_mock.analyze_scenario.return_value = ai_response
        
        # Configure db_manager mock
        scenario_id = "71234567890abcdef1234567"
        self.db_manager_mock.create_scenario.return_value = scenario_id
        
        # Execute test
        result = self.scenario_service.analyze_scenario(scenario_text, user_id)
        
        # Verify result
        self.assertEqual(result["questions"], ai_response["questions"])
        self.assertEqual(result["perspectives"], ai_response["perspectives"])
        self.assertEqual(result["action_plan"], ai_response["action_plan"])
        self.assertIn("analysis_date", result)
        self.assertIn("word_count", result)
        
        # Verify scenario was saved
        self.db_manager_mock.create_scenario.assert_called_once()
        self.db_manager_mock.increment_user_counter.assert_called_once_with(user_id, "scenarios_completed")
    
    def test_get_user_scenarios(self):
        """Test retrieving user scenarios."""
        # Prepare test data
        user_id = "61234567890abcdef1234567"
        expected_scenarios = [
            {"_id": "71234567890abcdef1234567", "scenario_text": "Scenario 1"},
            {"_id": "81234567890abcdef1234567", "scenario_text": "Scenario 2"}
        ]
        
        # Configure mock
        self.db_manager_mock.get_scenarios_by_user.return_value = expected_scenarios
        
        # Execute test
        result = self.scenario_service.get_user_scenarios(user_id)
        
        # Verify result
        self.assertEqual(result, expected_scenarios)
        self.db_manager_mock.get_scenarios_by_user.assert_called_once_with(
            user_id, limit=10, skip=0, sort_by="analysis_date", descending=True
        )


class TestAIService(unittest.TestCase):
    """Test cases for the AI service."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a patched AIService
        with patch('openai.OpenAI') as mock_openai:
            self.openai_mock = mock_openai.return_value
            self.ai_service = AIService()
    
    def test_analyze_scenario(self):
        """Test analyzing a scenario with OpenAI."""
        # Prepare test data
        scenario_text = "Should I accept a job offer in another city?"
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"questions": ["Q1", "Q2"], "perspectives": ["P1", "P2"], "action_plan": ["A1", "A2"]}'
        self.openai_mock.chat.completions.create.return_value = mock_response
        
        # Execute test
        result = self.ai_service.analyze_scenario(scenario_text)
        
        # Verify result
        self.assertEqual(result["questions"], ["Q1", "Q2"])
        self.assertEqual(result["perspectives"], ["P1", "P2"])
        self.assertEqual(result["action_plan"], ["A1", "A2"])
        
        # Verify OpenAI was called correctly
        self.openai_mock.chat.completions.create.assert_called_once()
        call_args = self.openai_mock.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4o-mini")
        self.assertEqual(len(call_args["messages"]), 2)
        self.assertIn(scenario_text, call_args["messages"][1]["content"])
    
    def test_get_mbti_questions(self):
        """Test getting MBTI questions."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"questions": [{"id": 1, "question": "Test question", "options": ["A", "B", "C"]}]}'
        self.openai_mock.chat.completions.create.return_value = mock_response
        
        # Execute test
        result = self.ai_service.get_mbti_questions()
        
        # Verify result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["question"], "Test question")
        
        # Verify OpenAI was called correctly
        self.openai_mock.chat.completions.create.assert_called_once()


if __name__ == "__main__":
    unittest.main() 