"""
Voice Engine module for the Decision Game.
This module handles voice input functionality using speech recognition.
"""

import time
import speech_recognition as sr
import threading
import pygame
import os
import sys
import random
from frontend.ui_components import TextBox

class VoiceEngine:
    """Voice input engine for the Decision Game using speech recognition."""
    
    def __init__(self):
        """Initialize the voice engine."""
        print("Initializing speech recognition engine")
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        
        # Configure the recognizer for better recognition
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Flag to stop listening
        self.stop_flag = False
        
        # Store last error for diagnostics
        self.last_error = None
        
        # Set whether to use fallback mode
        self.use_fallback = False
        
        # Sample responses for fallback mode
        self.sample_responses = [
            "I'm trying to decide whether to change careers.",
            "I'm considering buying a new house but I'm not sure if it's the right time.",
            "I need to choose between going back to school or accepting a promotion at work.",
            "I'm thinking about moving to a different city for better opportunities.",
            "I'm not sure if I should invest my savings or pay off my student loans first."
        ]
        
        # Test microphone during initialization
        if not self.test_microphone():
            print("Real microphone not available, using fallback mode")
            self.use_fallback = True
        
    def test_microphone(self):
        """Test microphone availability and store error information."""
        try:
            # List available microphones for debugging
            mics = sr.Microphone.list_microphone_names()
            print(f"Available microphones: {mics}")
            
            # Try to initialize microphone with default device
            with sr.Microphone() as source:
                print(f"Successfully initialized microphone: {source}")
                return True
        except Exception as e:
            self.last_error = str(e)
            print(f"Microphone initialization error: {e}")
            return False
                
    def listen(self):
        """
        Listen for voice input and convert to text.
        
        Returns:
            A string representing the transcribed voice input
        """
        print("Starting voice recognition...")
        self.is_listening = True
        self.stop_flag = False
        result_text = ""
        
        # Use fallback mode if required
        if self.use_fallback:
            return self._fallback_listen()
        
        try:
            # Try using the default microphone
            with sr.Microphone() as source:
                # Adjust for ambient noise first
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                print("Processing speech...")
                result_text = self.recognizer.recognize_google(audio)
                print(f"Recognized: {result_text}")
                
        except sr.WaitTimeoutError:
            print("Timeout - no speech detected")
            result_text = ""
        except sr.UnknownValueError:
            print("Could not understand audio")
            result_text = ""
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            result_text = ""
        except Exception as e:
            print(f"Unexpected error during speech recognition: {e}")
            self.last_error = str(e)
            result_text = ""
        finally:
            self.is_listening = False
            
        return result_text
    
    def _fallback_listen(self):
        """Simulate listening in fallback mode."""
        print("Using fallback voice recognition (simulated)...")
        
        # Simulate processing time
        time.sleep(2)
        
        # Choose a random sample response
        response = random.choice(self.sample_responses)
        print(f"Simulated voice input: {response}")
        
        self.is_listening = False
        return response
            
    def stop_listening(self):
        """Stop listening for voice input."""
        if self.is_listening:
            print("Stopping voice input listening")
            self.stop_flag = True
            self.is_listening = False
    
    def get_error_details(self):
        """
        Get detailed error information about microphone issues.
        
        Returns:
            A string with diagnostic information
        """
        details = []
        
        # Add basic error information
        if self.last_error:
            details.append(f"Last error: {self.last_error}")
        
        # Check if PyAudio is properly installed
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            details.append(f"PyAudio found {num_devices} audio devices")
            
            # List available devices
            devices = []
            for i in range(num_devices):
                device_info = p.get_device_info_by_index(i)
                if device_info.get('maxInputChannels') > 0:
                    devices.append(f"Input device {i}: {device_info.get('name')}")
            
            if devices:
                details.append("Available input devices:")
                details.extend(devices)
            else:
                details.append("No input devices found")
                
            p.terminate()
        except Exception as e:
            details.append(f"PyAudio error: {e}")
        
        # Check if any microphones are recognized by the speech_recognition library
        try:
            mics = sr.Microphone.list_microphone_names()
            if mics:
                details.append(f"Speech Recognition found {len(mics)} microphones")
            else:
                details.append("Speech Recognition found no microphones")
        except Exception as e:
            details.append(f"Microphone listing error: {e}")
        
        return "\n".join(details)
    
    def is_available(self):
        """
        Check if voice input is available.
        
        Returns:
            True if speech recognition is available (either real or fallback)
        """
        if self.use_fallback:
            return True
            
        try:
            # Try to initialize a microphone
            with sr.Microphone() as source:
                return True
        except Exception as e:
            self.last_error = str(e)
            return False 