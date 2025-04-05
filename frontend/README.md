# Decision Game Frontend

This directory contains the frontend code for the Decision Game application, a tool to help users make better decisions.

## Code Structure

The code has been restructured into a modular architecture for better maintainability:

### Main Files
- `main.py` - Entry point for the application
- `main_game.py` - Main game class that orchestrates all other modules
- `__init__.py` - Package initialization file

### Modules
- `ui.py` - Base UI components (Button, TextBox, Label, Panel, ScrollArea)
- `ui_components.py` - Manages creation and initialization of all game UI elements
- `screens.py` - Contains all screen drawing functions
- `event_handlers.py` - Event handling and processing
- `game_logic.py` - Core business logic and gameplay functions
- `api_client.py` - API communication for user data and analysis
- `voice.py` - Voice input functionality

## How It Works

1. The `main.py` file serves as the entry point, importing and initializing the `DecisionGame` class.
2. The `DecisionGame` class (in `main_game.py`) orchestrates the game, managing:
   - Game state (login, register, scenario, etc.)
   - Main game loop (events, updates, drawing)
   - Global settings (dark mode, user data)
   - Utility functions (text wrapping, drawing)

3. Modules are organized by functionality:
   - `UIComponents` initializes all UI elements
   - `GameScreens` handles drawing each screen
   - `GameEventHandler` processes user input
   - `GameLogic` contains gameplay functions

## How to Run

Run the game by executing:
```
python -m decision.frontend.main
```

## Class Relationships

- `DecisionGame` owns instances of:
  - `UIComponents` - Creates and initializes all UI elements
  - `GameScreens` - Draws screens based on current state
  - `GameEventHandler` - Processes user input events
  - `GameLogic` - Contains game functionality
  - `APIClient` - Handles API communication
  - `VoiceEngine` - Manages voice input

- Each of these classes receives a reference to the main game instance to access game state and other components.

## Adding New Features

When adding new features:

1. **UI Components**: Add to `ui_components.py` in the appropriate initialization method
2. **Screen Drawing**: Add to `screens.py` in the appropriate drawing method
3. **Event Handling**: Add to `event_handlers.py` in the appropriate handler method
4. **Game Logic**: Add to `game_logic.py` with appropriate methods
5. **States**: Add new states to the `DecisionGame` class if needed 