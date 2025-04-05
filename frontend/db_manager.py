"""
Database Manager for the Decision Game.
This module handles MongoDB database connections and operations.
"""

import pymongo
import os
from datetime import datetime


class DBManager:
    """MongoDB database manager for the Decision Game."""
    
    def __init__(self, connection_string=None):
        """
        Initialize the database manager.
        
        Args:
            connection_string: Optional MongoDB connection string
        """
        # Get connection string from environment or parameter
        self.connection_string = connection_string or os.environ.get(
            "MONGODB_CONNECTION_STRING", 
            "mongodb+srv://dineshraut121998:NTAl4PbusozWrS2M@mydatabase.gpeeo.mongodb.net/"
        )
        
        # Initialize MongoDB client
        self.client = None
        self.db = None
        
        try:
            self.client = pymongo.MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.server_info()
            self.db = self.client.decision_game
            print("Successfully connected to MongoDB")
            # Create indexes
            self._initialize_db()
        except pymongo.errors.ServerSelectionTimeoutError:
            print("Warning: Could not connect to MongoDB - running in local mode")
            self.use_local_storage = True
            # Create an in-memory data structure for local development
            self.local_users = []
            self.local_scenarios = []
        except Exception as e:
            print(f"Warning: Database connection failed: {str(e)} - running in local mode")
            self.use_local_storage = True
            # Create an in-memory data structure for local development
            self.local_users = []
            self.local_scenarios = []
    
    def _initialize_db(self):
        """Initialize the database and create indexes."""
        if self.db is not None:
            print("Database connected successfully")
            self._create_indexes()
        else:
            print("Failed to connect to database")
    
    def _create_indexes(self):
        """Create database indexes for improved query performance."""
        # Create user collection indexes
        self._create_user_indexes()
        
        # Create scenario collection indexes
        self._create_scenario_indexes()
    
    def _create_user_indexes(self):
        """Create indexes for the users collection."""
        try:
            # Create index on username for fast user lookups during login
            self.db.users.create_index("username", unique=True)
            print("Created unique index on users.username")
        except Exception as e:
            print(f"Error creating username index: {e}")
            
        try:
            # Create index on email for fast lookups during registration
            self.db.users.create_index("email", unique=True)
            print("Created unique index on users.email")
        except Exception as e:
            print(f"Error creating email index: {e}")
            
        try:
            # Create index on token for fast token validation
            self.db.users.create_index("token")
            print("Created index on users.token")
        except Exception as e:
            print(f"Error creating token index: {e}")
    
    def _create_scenario_indexes(self):
        """Create indexes for the scenarios collection."""
        try:
            # Create index on user_id for quick user-related queries
            self.db.scenarios.create_index("user_id")
            print("Created index on scenarios.user_id")
        except Exception as e:
            print(f"Error creating user_id index: {e}")
            
        try:
            # Create index on analysis_date for efficient date-based queries
            self.db.scenarios.create_index("analysis_date")
            print("Created index on scenarios.analysis_date")
        except Exception as e:
            print(f"Error creating analysis_date index: {e}")
            
        try:
            # Create compound index for efficient filtering by user and date
            self.db.scenarios.create_index([
                ("user_id", pymongo.ASCENDING), 
                ("analysis_date", pymongo.DESCENDING)
            ])
            print("Created compound index on scenarios.user_id and scenarios.analysis_date")
        except Exception as e:
            print(f"Error creating compound index: {e}")
            
        try:
            # Create text index for scenario text searching
            self.db.scenarios.create_index([("scenario_text", "text")])
            print("Created text index on scenarios.scenario_text")
        except Exception as e:
            print(f"Error creating text index: {e}")
            
        try:
            # Create index on word_count for filtering by scenario length
            self.db.scenarios.create_index("word_count")
            print("Created index on scenarios.word_count")
        except Exception as e:
            print(f"Error creating word_count index: {e}")
    
    def get_user_by_username(self, username):
        """Get user document by username."""
        try:
            if hasattr(self, 'use_local_storage') and self.use_local_storage:
                for user in self.local_users:
                    if user.get("username") == username:
                        return user
                return None
                
            return self.db.users.find_one({"username": username})
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    def get_user_by_token(self, token):
        """Get user document by token."""
        try:
            if hasattr(self, 'use_local_storage') and self.use_local_storage:
                for user in self.local_users:
                    if user.get("token") == token:
                        return user
                return None
                
            return self.db.users.find_one({"token": token})
        except Exception as e:
            print(f"Error getting user by token: {e}")
            return None
    
    def create_user(self, user_data):
        """Create a new user document."""
        try:
            if hasattr(self, 'use_local_storage') and self.use_local_storage:
                # Check for duplicate username or email
                for user in self.local_users:
                    if user.get("username") == user_data.get("username"):
                        raise ValueError("Username already exists")
                    if user.get("email") == user_data.get("email"):
                        raise ValueError("Email already exists")
                
                # Generate a fake ObjectId
                import uuid
                user_id = str(uuid.uuid4())
                user_data["_id"] = user_id
                
                # Debug password storage
                print(f"Creating local user with username: {user_data.get('username')}")
                print(f"Password hash being stored: {user_data.get('password')[:15]}...")
                
                # Store the user data
                self.local_users.append(user_data)
                
                # Debug registered users
                print(f"Current local users: {len(self.local_users)}")
                for user in self.local_users:
                    print(f"- {user.get('username')}: {user.get('password')[:10]}...")
                
                return user_id
            
            return self.db.users.insert_one(user_data).inserted_id
        except pymongo.errors.DuplicateKeyError as e:
            error_str = str(e)
            if "username" in error_str:
                raise ValueError("Username already exists")
            elif "email" in error_str:
                raise ValueError("Email already exists")
            else:
                raise ValueError("User creation failed: duplicate key")
        except ValueError as ve:
            # Re-raise ValueError for username/email already exists
            raise ve
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
    
    def update_user(self, user_id, update_data):
        """Update a user document."""
        try:
            if hasattr(self, 'use_local_storage') and self.use_local_storage:
                for i, user in enumerate(self.local_users):
                    if str(user.get("_id")) == str(user_id):
                        for key, value in update_data.items():
                            self.local_users[i][key] = value
                        print(f"Updated local user: {self.local_users[i].get('username')} with data: {update_data.keys()}")
                        return True
                print(f"User ID {user_id} not found in local storage")
                return False
            
            # When using MongoDB
            try:
                # Import ObjectId only when needed
                from pymongo import ObjectId
                return self.db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": update_data}
                )
            except ImportError:
                # Fallback if ObjectId isn't available
                return self.db.users.update_one(
                    {"_id": user_id},
                    {"$set": update_data}
                )
        except Exception as e:
            print(f"Error updating user: {e}")
            return None
    
    def create_scenario(self, scenario_data):
        """Create a new scenario document."""
        try:
            return self.db.scenarios.insert_one(scenario_data).inserted_id
        except Exception as e:
            print(f"Error creating scenario: {e}")
            raise
    
    def get_scenarios_by_user(self, user_id, limit=10, skip=0, sort_by="analysis_date", descending=True):
        """Get scenarios for a specific user with sorting options."""
        try:
            sort_field = sort_by
            sort_direction = pymongo.DESCENDING if descending else pymongo.ASCENDING
            
            return list(self.db.scenarios.find(
                {"user_id": user_id}
            ).sort(
                sort_field, sort_direction
            ).skip(skip).limit(limit))
        except Exception as e:
            print(f"Error getting scenarios by user: {e}")
            return []
    
    def search_scenarios(self, user_id, keyword, limit=10):
        """Search scenarios with text search."""
        try:
            return list(self.db.scenarios.find({
                "$and": [
                    {"user_id": user_id},
                    {"$text": {"$search": keyword}}
                ]
            }).sort(
                [("score", {"$meta": "textScore"})]
            ).limit(limit))
        except Exception as e:
            print(f"Error searching scenarios: {e}")
            return []
    
    def increment_user_counter(self, user_id, field, amount=1):
        """Increment a counter field in a user document."""
        try:
            return self.db.users.update_one(
                {"_id": pymongo.ObjectId(user_id)},
                {"$inc": {field: amount}}
            )
        except Exception as e:
            print(f"Error incrementing user counter: {e}")
            return None 