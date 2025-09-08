#!/usr/bin/env python3
"""
Unit tests for the Pokédx application functionality.

This test suite covers the core functionality of the PokedexApp class,
focusing on testable logic that can be isolated from GUI components.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from io import BytesIO
import requests
from PIL import Image

# Since tkinter isn't available in this environment, we'll mock it
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()

# Import the app after mocking tkinter
from app import PokedexApp


class TestPokedexCore(unittest.TestCase):
    """Test core functionality of PokedexApp."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the tkinter root and create a PokedexApp instance
        self.mock_root = Mock()
        self.mock_root.title = Mock()
        self.mock_root.clipboard_clear = Mock()
        self.mock_root.clipboard_append = Mock()
        self.mock_root.update = Mock()
        self.mock_root.after = Mock()
        
        with patch('app.ttk'), patch('app.tk'):
            self.app = PokedexApp(self.mock_root)
    
    @patch('app.requests.get')
    def test_get_pokemon_data_success(self, mock_get):
        """Test successful Pokemon data retrieval."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            'name': 'pikachu',
            'sprites': {
                'other': {
                    'showdown': {
                        'front_default': 'http://example.com/pikachu.gif'
                    }
                }
            }
        }
        mock_get.return_value = mock_response
        
        result = self.app.get_pokemon_data(25)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Pikachu')
        self.assertEqual(result['gif_url'], 'http://example.com/pikachu.gif')
        mock_get.assert_called_once_with("https://pokeapi.co/api/v2/pokemon/25", timeout=10)
    
    @patch('app.requests.get')
    def test_get_pokemon_data_api_failure(self, mock_get):
        """Test Pokemon data retrieval when API fails."""
        # Mock API failure
        mock_get.side_effect = requests.RequestException("API Error")
        
        with patch('app.messagebox.showerror') as mock_error:
            result = self.app.get_pokemon_data(25)
            
            self.assertIsNone(result)
            mock_error.assert_called_once()
    
    @patch('app.requests.get')
    def test_get_pokemon_image_success(self, mock_get):
        """Test successful Pokemon image download."""
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='red')
        image_bytes = BytesIO()
        test_image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.content = image_bytes.getvalue()
        mock_get.return_value = mock_response
        
        result = self.app.get_pokemon_image(1)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Image.Image)
        mock_get.assert_called_once_with(
            "https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/001.png", 
            timeout=10
        )
    
    @patch('app.requests.get')
    def test_get_pokemon_image_failure(self, mock_get):
        """Test Pokemon image download when request fails."""
        mock_get.side_effect = requests.RequestException("Network Error")
        
        with patch('app.messagebox.showerror') as mock_error:
            result = self.app.get_pokemon_image(1)
            
            self.assertIsNone(result)
            mock_error.assert_called_once()


class TestPokedexValidation(unittest.TestCase):
    """Test input validation and data formatting."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_root = Mock()
        with patch('app.ttk'), patch('app.tk'):
            self.app = PokedexApp(self.mock_root)
    
    def test_pokemon_number_validation_valid(self):
        """Test validation of valid Pokemon numbers."""
        self.app.number_entry = Mock()
        self.app.number_entry.get.return_value = "25"
        
        with patch.object(self.app, 'display_pokemon') as mock_display:
            self.app.search_pokemon()
            mock_display.assert_called_once_with(25)
    
    def test_pokemon_number_validation_invalid_range(self):
        """Test validation of Pokemon numbers outside valid range."""
        self.app.number_entry = Mock()
        self.app.number_entry.get.return_value = "2000"
        
        with patch('app.messagebox.showwarning') as mock_warning:
            self.app.search_pokemon()
            mock_warning.assert_called_once_with("Invalid Input", "Number must be between 1 and 1025")
    
    def test_pokemon_number_validation_non_numeric(self):
        """Test validation of non-numeric input."""
        self.app.number_entry = Mock()
        self.app.number_entry.get.return_value = "abc"
        
        with patch('app.messagebox.showwarning') as mock_warning:
            self.app.search_pokemon()
            mock_warning.assert_called_once_with("Invalid Input", "Please enter a valid number")
    
    def test_copy_pokemon_name_formatting(self):
        """Test Pokemon name formatting for clipboard."""
        self.app.current_pokemon_name = "Pikachu"
        
        with patch('app.messagebox.showinfo') as mock_info:
            self.app.copy_pokemon_name()
            
            self.mock_root.clipboard_clear.assert_called_once()
            self.mock_root.clipboard_append.assert_called_once_with("justin/pikachu")
            mock_info.assert_called_once_with("Copied", "Copied: justin/pikachu")


class TestPokedexNavigation(unittest.TestCase):
    """Test navigation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_root = Mock()
        with patch('app.ttk'), patch('app.tk'):
            self.app = PokedexApp(self.mock_root)
        
        self.app.number_entry = Mock()
    
    def test_next_pokemon_normal(self):
        """Test normal next Pokemon navigation."""
        self.app.number_entry.get.return_value = "25"
        
        with patch.object(self.app, 'display_pokemon') as mock_display:
            self.app.next_pokemon()
            mock_display.assert_called_once_with(26)
    
    def test_next_pokemon_at_max(self):
        """Test next Pokemon navigation at maximum number."""
        self.app.number_entry.get.return_value = "1025"
        
        with patch.object(self.app, 'display_pokemon') as mock_display:
            self.app.next_pokemon()
            mock_display.assert_called_once_with(1025)  # Should stay at max
    
    def test_previous_pokemon_normal(self):
        """Test normal previous Pokemon navigation."""
        self.app.number_entry.get.return_value = "25"
        
        with patch.object(self.app, 'display_pokemon') as mock_display:
            self.app.previous_pokemon()
            mock_display.assert_called_once_with(24)
    
    def test_previous_pokemon_at_min(self):
        """Test previous Pokemon navigation at minimum number."""
        self.app.number_entry.get.return_value = "1"
        
        with patch.object(self.app, 'display_pokemon') as mock_display:
            self.app.previous_pokemon()
            mock_display.assert_called_once_with(1)  # Should stay at min
    
    def test_navigation_with_invalid_entry(self):
        """Test navigation when entry contains invalid data."""
        self.app.number_entry.get.return_value = "invalid"
        
        with patch.object(self.app, 'display_pokemon') as mock_display:
            self.app.next_pokemon()
            mock_display.assert_called_once_with(1)  # Should default to 1


class TestPokedexImageHandling(unittest.TestCase):
    """Test image processing and handling functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_root = Mock()
        with patch('app.ttk'), patch('app.tk'):
            self.app = PokedexApp(self.mock_root)
    
    def test_toggle_image_functionality(self):
        """Test image toggle between static and GIF."""
        # Set up initial state
        self.app.current_image = Mock()
        self.app.current_gif = Mock()
        self.app.gif_frames = [Mock(), Mock()]
        self.app.showing_gif = False
        self.app.image_label = Mock()
        
        # Mock the StringVar properly
        self.app.toggle_text = Mock()
        self.app.toggle_text.set = Mock()
        
        # Test toggle to GIF
        self.app.toggle_image()
        self.assertTrue(self.app.showing_gif)
        self.app.toggle_text.set.assert_called_with("Show Static")
    
    @patch('app.filedialog.asksaveasfilename')
    def test_save_image_success(self, mock_dialog):
        """Test successful image saving."""
        # Setup
        self.app.current_image = Mock()
        self.app.current_pokemon_name = "Pikachu"
        self.app.number_entry = Mock()
        self.app.number_entry.get.return_value = "25"
        
        mock_dialog.return_value = "/tmp/test.png"
        
        with patch('app.messagebox.showinfo') as mock_info:
            self.app.save_image()
            
            self.app.current_image.save.assert_called_once_with("/tmp/test.png", 'PNG')
            mock_info.assert_called_once_with("Success", "Image saved to /tmp/test.png!")
    
    @patch('app.filedialog.asksaveasfilename')
    def test_save_image_cancelled(self, mock_dialog):
        """Test image saving when user cancels dialog."""
        self.app.current_image = Mock()
        self.app.current_pokemon_name = "Pikachu"
        
        mock_dialog.return_value = ""  # User cancelled
        
        self.app.save_image()
        
        # Should not attempt to save
        self.app.current_image.save.assert_not_called()


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)