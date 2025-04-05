"""
User Service module for the Decision Game.
This module handles user management, authentication, and user data.
"""

import random
from datetime import datetime
import hashlib
from bson import ObjectId


class UserService:
    """Service for user management and authentication."""
    
    def __init__(self, db_manager):
        """
        Initialize the user service.
        
        Args:
            db_manager: The database manager instance
        """
        self.db_manager = db_manager
    
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
        try:
            # Hash the password for security
            hashed_password = self._hash_password(password)
            
            # Create user data
            user_data = {
                "username": username,
                "email": email,
                "fullname": fullname,
                "password": hashed_password,  # In a real app, use proper password hashing
                "created_at": datetime.now(),
                "level": 1,
                "points": 0,
                "scenarios_completed": 0
            }
            
            # Create the user
            user_id = self.db_manager.create_user(user_data)
            
            return {
                "status_code": 200,
                "message": "User registered successfully",
                "user_id": str(user_id)
            }
            
        except ValueError as e:
            return {
                "status_code": 400,
                "detail": str(e)
            }
        except Exception as e:
            print(f"Registration error: {e}")
            return {
                "status_code": 500,
                "detail": f"Database error: {str(e)}"
            }
    
    def login(self, username, password):
        """
        Login a user.
        
        Args:
            username: The username
            password: The password
            
        Returns:
            A dictionary with the token if successful
        """
        try:
            # Special test case to display all users (for debugging)
            if username == "showall" and password == "showall":
                self._print_all_users()
                return {"error": "Debug mode: Displayed all users in console"}
                
            # Get the user
            user = self.db_manager.get_user_by_username(username)
            
            if not user:
                print(f"User {username} not found in database")
                return {"error": "Invalid username or password"}
            
            # Verify password
            hashed_password = self._hash_password(password)
            stored_password = user.get("password", "")
            
            print(f"Login attempt for {username}:")
            print(f"Input password hash: {hashed_password[:10]}...")
            print(f"Stored password hash: {stored_password[:10]}...")
            
            if stored_password != hashed_password:
                print(f"Password mismatch for {username}")
                return {"error": "Invalid username or password"}
            
            print(f"Password verified for {username}")
            
            # Generate token
            token = self._generate_token(username)
            
            # Update user with new token
            self.db_manager.update_user(user["_id"], {
                "token": token,
                "last_login": datetime.now()
            })
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "user_id": str(user["_id"]),
                "username": username
            }
            
        except Exception as e:
            print(f"Login error: {e}")
            return {"error": f"Login failed: {str(e)}"}
    
    def get_user_from_token(self, token):
        """
        Get user data from token.
        
        Args:
            token: The authentication token
            
        Returns:
            The user document or None
        """
        if not token:
            return None
            
        return self.db_manager.get_user_by_token(token)
    
    def get_user_id_from_token(self, token):
        """
        Get user ID from token.
        
        Args:
            token: The authentication token
            
        Returns:
            The user ID as string or None
        """
        user = self.get_user_from_token(token)
        if user:
            return str(user["_id"])
        return None
    
    def increment_scenarios_completed(self, user_id):
        """
        Increment the user's scenarios_completed count.
        
        Args:
            user_id: The user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.db_manager.increment_user_counter(user_id, "scenarios_completed")
            return True
        except Exception as e:
            print(f"Error incrementing scenarios completed: {e}")
            return False
    
    def _generate_token(self, username):
        """
        Generate a unique token for the user.
        
        Args:
            username: The username
            
        Returns:
            A unique token string
        """
        # In a real app, use a more secure token generation method
        return f"token_{username}_{random.randint(1000, 9999)}_{datetime.now().timestamp()}"
    
    def _hash_password(self, password):
        """
        Hash a password for secure storage.
        
        Args:
            password: The plaintext password
            
        Returns:
            The hashed password
        """
        # In a real app, use a proper password hashing algorithm like bcrypt
        # This is a simple hash for demonstration purposes only
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _print_all_users(self):
        """Print all users in the database for debugging."""
        print("\n==== REGISTERED USERS ====")
        if hasattr(self.db_manager, 'use_local_storage') and self.db_manager.use_local_storage:
            print("Using local storage, users:")
            if not self.db_manager.local_users:
                print("No users found in local storage")
            for i, user in enumerate(self.db_manager.local_users):
                print(f"{i+1}. Username: {user.get('username')}, Email: {user.get('email')}")
                print(f"   Password hash: {user.get('password')[:15]}...")
        else:
            # Display from MongoDB
            try:
                users = list(self.db_manager.db.users.find({}))
                if not users:
                    print("No users found in MongoDB")
                for i, user in enumerate(users):
                    print(f"{i+1}. Username: {user.get('username')}, Email: {user.get('email')}")
                    print(f"   Password hash: {user.get('password')[:15]}...")
            except Exception as e:
                print(f"Error retrieving users: {e}")
        print("==========================\n") 