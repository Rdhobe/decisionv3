"""
AI Service module for the Decision Game.
This module handles interactions with the Groq API.
"""

import json
import os
from groq import Groq  # Importing the Groq client

class AIService:
    """Service for AI-based functionality using Groq."""
    
    def __init__(self, api_key=None):
        """
        Initialize the AI service.
        
        Args:
            api_key: Optional Groq API key; will use environment variable if not provided.
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY") or "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"
        if not self.api_key:
            raise ValueError("Groq API key must be provided via parameter or environment variable.")
        self.client = Groq(api_key=self.api_key)  # Initialize the Groq client
        if not self.client:
            raise ValueError("Groq client not initialized.")
        self.default_model = "deepseek-r1-distill-llama-70b"
    
    def _call_groq_api(self, messages, fallback_func):
        """
        Helper method to call the Groq API for completions.
        
        Args:
            messages: List of message dictionaries for the API.
            fallback_func: Function to call for fallback data if the API call fails.
            
        Returns:
            The API response as a string, or fallback data if an error occurs.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=0.8,
                max_completion_tokens=4096,
                top_p=0.95,
                stream=False,
                stop=None,
            )
            
            response_content = completion.choices[0].message.content
            if not response_content or not response_content.strip():
                raise ValueError("Received empty response from Groq API.")
            
            # If the response starts with <think>, try to extract the actual content
            if response_content.startswith("<think>"):
                print("Response contains thinking process, extracting actual content...")
                
                # Check if there's a closing </think> tag
                if "</think>" in response_content:
                    # Extract content after the thinking process
                    parts = response_content.split("</think>", 1)
                    if len(parts) > 1 and parts[1].strip():
                        print("Successfully extracted content after thinking process")
                        return parts[1].strip()  # Return content after </think>
                
                # If we can't extract content after </think>, look for JSON in the thinking
                import re
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    potential_json = json_match.group(0)
                    try:
                        # See if this is valid JSON
                        import json
                        parsed = json.loads(potential_json)
                        print("Successfully extracted JSON from thinking process")
                        return parsed  # Return the parsed JSON directly
                    except json.JSONDecodeError:
                        print("Found JSON-like content in thinking, but it's not valid JSON")
                        pass
                
                print("Couldn't extract useful content from thinking, using fallback data")
                return fallback_func()
                
            return response_content
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return fallback_func()

    def analyze_scenario(self, scenario_text):
        """
        Analyze a decision scenario using Groq.
        
        Args:
            scenario_text: The scenario text to analyze.
            
        Returns:
            A dictionary with analysis results.
        """
        messages = [
            {"role": "system", "content": "You are an expert decision-making assistant. Analyze the following scenario and provide key questions, perspectives, and action plan steps. DO NOT include any thinking or explanation in your response. Respond ONLY with JSON."},
            {"role": "user", "content": f"Analyze this decision scenario and provide: 1) Five important questions to consider, 2) Four different perspectives to think about, 3) Four action plan steps.\n\nScenario: {scenario_text}\n\nRESPOND IN VALID JSON FORMAT with these keys: questions (array), perspectives (array), and action_plan (array)."}
        ]
        
        # First check if we got a direct fallback
        response = self._call_groq_api(messages, self._get_fallback_scenario_analysis)
        if isinstance(response, dict):
            return response
            
        try:
            # Attempt to clean the response before parsing
            cleaned_response = response.strip()
            
            # Check for thinking prefix
            if cleaned_response.startswith("<think>"):
                print("Received thinking prefix, trying to extract useful content")
                # This should now be handled by _call_groq_api
                
            # Look for a JSON object in the response
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                
            try:
                result = json.loads(cleaned_response)
                return result
            except json.JSONDecodeError:
                # Try to find JSON-like content in the response
                import re
                json_pattern = r'\{.*\}'
                match = re.search(json_pattern, cleaned_response, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    try:
                        return json.loads(json_str)
                    except:
                        pass
                
                # If all else fails, return fallback
                return self._get_fallback_scenario_analysis()
        except Exception as e:
            print(f"Error analyzing scenario: {e}")
            print(f"Raw response: {response[:100]}...")  # Print first 100 chars of response
            return self._get_fallback_scenario_analysis()

    def get_mbti_questions(self):
        """
        Get MBTI personality test questions using Groq.
        
        Returns:
            A list of MBTI questions.
        """
        messages = [
            {"role": "system", "content": "You are an expert MBTI personality assessment assistant. DO NOT include any thinking or explanation in your response. Respond ONLY with JSON."},
            {"role": "user", "content": "Generate 5 MBTI personality test questions with options from 'Strongly Agree' to 'Strongly Disagree'. Return as JSON with each question having: question text, id, and options array. RESPOND IN VALID JSON FORMAT with a 'questions' array."}
        ]
        
        response = self._call_groq_api(messages, self._get_fallback_mbti_questions)
        # If response is already a list (as expected) return it
        if isinstance(response, list):
            return response
        # If response is a dict with questions, return that
        if isinstance(response, dict) and "questions" in response:
            return response["questions"]
            
        # Otherwise, try to parse the response:
        try:
            # Attempt to clean the response before parsing
            cleaned_response = response.strip()
            
            # Check for thinking prefix
            if cleaned_response.startswith("<think>"):
                print("Received thinking prefix, using fallback data")
                return self._get_fallback_mbti_questions()
                
            # Look for a JSON object in the response
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                
            try:
                parsed = json.loads(cleaned_response)
                # If parsed is a dict with a "questions" key, return that
                if isinstance(parsed, dict) and "questions" in parsed:
                    return parsed["questions"]
                # If parsed is a list, return it directly
                if isinstance(parsed, list):
                    return parsed
                # Otherwise, return the fallback
                return self._get_fallback_mbti_questions()
            except json.JSONDecodeError:
                # Try to find JSON-like content in the response
                import re
                json_pattern = r'\{.*\}'
                match = re.search(json_pattern, cleaned_response, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    try:
                        parsed = json.loads(json_str)
                        if isinstance(parsed, dict) and "questions" in parsed:
                            return parsed["questions"]
                        if isinstance(parsed, list):
                            return parsed
                    except:
                        pass
                
                # If all else fails, return fallback
                return self._get_fallback_mbti_questions()
        except Exception as e:
            print(f"Error getting MBTI questions: {e}")
            print(f"Raw response: {response[:100]}...")  # Print first 100 chars of response
            return self._get_fallback_mbti_questions()

    def analyze_mbti_answers(self, answers):
        """
        Analyze MBTI test answers using Groq.
        
        Args:
            answers: A dictionary mapping question IDs to answers.
            
        Returns:
            A dictionary with MBTI results.
        """
        formatted_answers = [f"Question {q_id}: {answer}" for q_id, answer in answers.items()]
        answers_text = "\n".join(formatted_answers)
        
        messages = [
            {"role": "system", "content": "You are an expert MBTI personality assessment analyst. DO NOT include any thinking or explanation in your response. Respond ONLY with JSON."},
            {"role": "user", "content": f"Analyze these MBTI test answers and provide: 1) The four-letter personality type, 2) A description of the type, 3) Key strengths, 4) Potential weaknesses, 5) Career suggestions.\n\nAnswers:\n{answers_text}\n\nRESPOND IN VALID JSON FORMAT with these keys: type (string), description (string), strengths (array), weaknesses (array), and career_suggestions (array)."}
        ]
        
        response = self._call_groq_api(messages, self._get_fallback_mbti_results)
        if isinstance(response, dict):
            return response
        try:
            # Attempt to clean the response before parsing
            cleaned_response = response.strip()
            
            # Check for thinking prefix
            if cleaned_response.startswith("<think>"):
                print("Received thinking prefix, using fallback data")
                return self._get_fallback_mbti_results()
                
            # Look for a JSON object in the response
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                
            try:
                result = json.loads(cleaned_response)
                return result
            except json.JSONDecodeError:
                # Try to find JSON-like content in the response
                import re
                json_pattern = r'\{.*\}'
                match = re.search(json_pattern, cleaned_response, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    try:
                        return json.loads(json_str)
                    except:
                        pass
                
                # If all else fails, return fallback
                return self._get_fallback_mbti_results()
        except Exception as e:
            print(f"Error analyzing MBTI answers: {e}")
            print(f"Raw response: {response[:100]}...")  # Print first 100 chars of response
            return self._get_fallback_mbti_results()

    def generate_simulation_scenarios(self):
        """
        Generate decision simulation scenarios using Groq.
        
        Returns:
            A list of simulation scenarios.
        """
        messages = [
            {"role": "system", "content": "You are an expert decision scenario creator. DO NOT include any thinking or explanation in your response. Respond ONLY with JSON."},
            {"role": "user", "content": "Generate 3 decision scenarios for simulation with: 1) Title, 2) Description, 3) Options (at least 3 per scenario). RESPOND IN VALID JSON FORMAT with a 'scenarios' array containing objects with title, description, and options (array) properties."}
        ]
        
        response = self._call_groq_api(messages, self._get_fallback_simulation_scenarios)
        if isinstance(response, dict):
            # If the fallback returns a dict with "scenarios", extract the list
            if "scenarios" in response:
                return response["scenarios"]
            return []
        try:
            # Attempt to clean the response before parsing
            cleaned_response = response.strip()
            
            # Check for thinking prefix
            if cleaned_response.startswith("<think>"):
                print("Received thinking prefix, using fallback data")
                return self._get_fallback_simulation_scenarios()
                
            # Look for a JSON object in the response
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                
            try:
                parsed = json.loads(cleaned_response)
                if isinstance(parsed, dict) and "scenarios" in parsed:
                    return parsed["scenarios"]
                if isinstance(parsed, list):
                    return parsed
                return []
            except json.JSONDecodeError:
                # Try to find JSON-like content in the response
                import re
                json_pattern = r'\{.*\}'
                match = re.search(json_pattern, cleaned_response, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    try:
                        parsed = json.loads(json_str)
                        if isinstance(parsed, dict) and "scenarios" in parsed:
                            return parsed["scenarios"]
                        if isinstance(parsed, list):
                            return parsed
                    except:
                        pass
                
                # If all else fails, return fallback
                return self._get_fallback_simulation_scenarios()
        except Exception as e:
            print(f"Error generating simulation scenarios: {e}")
            print(f"Raw response: {response[:100]}...")  # Print first 100 chars of response
            return self._get_fallback_simulation_scenarios()
    
    def _get_fallback_scenario_analysis(self):
        """Get fallback scenario analysis data."""
        return {
            "questions": [
                "What are your main priorities in this situation?",
                "What alternatives have you considered?",
                "What are the potential risks of each option?",
                "How might this decision affect others around you?",
                "What information do you still need to make this decision?"
            ],
            "perspectives": [
                "Consider how this decision aligns with your long-term goals.",
                "Think about how this decision might look in hindsight a year from now.",
                "Examine this situation from the perspective of someone you admire.",
                "Consider the ethical implications of each possible choice."
            ],
            "action_plan": [
                "List all available options and their pros/cons.",
                "Gather any missing information you identified earlier.",
                "Consult with someone you trust about this decision.",
                "Set a deadline for making the final decision."
            ]
        }
    
    def _get_fallback_mbti_questions(self):
        """Get fallback MBTI questions.
        
        Returns a list of question dictionaries.
        """
        return [
            {
                "question": "You find it easy to introduce yourself to other people.",
                "id": 1,
                "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
            },
            {
                "question": "You often get so lost in thoughts that you ignore or forget your surroundings.",
                "id": 2,
                "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
            },
            {
                "question": "You try to respond to emails as soon as possible and cannot stand a messy inbox.",
                "id": 3,
                "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
            },
            {
                "question": "You find it easy to stay relaxed under pressure.",
                "id": 4,
                "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
            },
            {
                "question": "You do not usually initiate conversations.",
                "id": 5,
                "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
            }
        ]
    
    def _get_fallback_mbti_results(self):
        """Get fallback MBTI results."""
        return {
            "type": "INFJ",
            "description": "INFJs are creative nurturers with a strong sense of personal integrity and a drive to help others realize their potential.",
            "strengths": [
                "Creative and artistic",
                "Insightful about others",
                "Committed to their values",
                "Deep and complex thinkers"
            ],
            "weaknesses": [
                "Sensitive to criticism",
                "Can burn out easily",
                "Perfectionistic tendencies",
                "Difficulty with practical matters"
            ],
            "career_suggestions": [
                "Counselor or therapist",
                "Writer or editor",
                "Healthcare professional",
                "Teacher or professor"
            ]
        }
    
    def _get_fallback_simulation_scenarios(self):
        """Get fallback simulation scenarios.
        
        Returns a list of scenario dictionaries.
        """
        return [
            {
                "title": "Career Crossroads",
                "description": "You've received two job offers: one at a prestigious company with higher pay but longer hours, and one at a startup with lower initial pay but more flexibility and potential for growth.",
                "options": [
                    "Accept the prestigious company offer",
                    "Accept the startup offer",
                    "Negotiate with both companies for better terms",
                    "Decline both and continue searching"
                ]
            },
            {
                "title": "Relocation Dilemma",
                "description": "You have an opportunity to relocate to another city for better career prospects, but it would mean leaving friends and family behind.",
                "options": [
                    "Relocate immediately",
                    "Decline the opportunity",
                    "Try to negotiate a remote work arrangement",
                    "Delay the decision and visit the new city first"
                ]
            },
            {
                "title": "Education Investment",
                "description": "You're considering investing in further education, which would require significant time and money but could enhance your long-term career prospects.",
                "options": [
                    "Enroll full-time",
                    "Enroll part-time while continuing to work",
                    "Self-study instead of formal education",
                    "Postpone education and focus on gaining experience"
                ]
            }
        ]
