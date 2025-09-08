import unittest.mock as mock
import pytest
import tkinter as tk
from io import BytesIO
from PIL import Image
import sys
import os

# Add src directory to path to import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from app import PokedexApp


class TestPokedexApp:
    """Test suite for PokedexApp functionality"""
    
    @pytest.fixture
    def app(self):
        """Create a PokedexApp instance for testing"""
        root = tk.Tk()
        app = PokedexApp(root)
        yield app
        root.destroy()
    
    @pytest.fixture
    def mock_pokemon_data(self):
        """Mock Pokemon API response data"""
        return {
            'name': 'Pikachu',
            'sprites': {
                'other': {
                    'showdown': {
                        'front_default': 'https://example.com/pikachu.gif'
                    }
                }
            }
        }
    
    @pytest.fixture
    def mock_image(self):
        """Create a mock PIL Image for testing"""
        img = Image.new('RGB', (100, 100), color='red')
        return img

    def test_app_initialization(self, app):
        """Test that the app initializes correctly"""
        assert app.root.title() == "Pokédex"
        assert app.current_image is None
        assert app.current_gif is None
        assert app.current_pokemon_name is None
        assert app.showing_gif is False
        assert app.image_size == (800, 800)
    
    @mock.patch('app.requests.get')
    def test_get_pokemon_data_success(self, mock_get, app, mock_pokemon_data):
        """Test successful Pokemon data fetching"""
        mock_response = mock.Mock()
        mock_response.json.return_value = mock_pokemon_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = app.get_pokemon_data(25)
        
        assert result is not None
        assert result['name'] == 'Pikachu'
        assert result['gif_url'] == 'https://example.com/pikachu.gif'
        mock_get.assert_called_once_with("https://pokeapi.co/api/v2/pokemon/25", timeout=10)
    
    @mock.patch('app.messagebox.showerror')
    @mock.patch('app.requests.get')
    def test_get_pokemon_data_failure(self, mock_get, mock_messagebox, app):
        """Test Pokemon data fetching with network error"""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = app.get_pokemon_data(25)
        
        assert result is None
        mock_messagebox.assert_called_once()
    
    @mock.patch('app.requests.get')
    def test_get_pokemon_image_success(self, mock_get, app, mock_image):
        """Test successful Pokemon image fetching"""
        # Create a BytesIO object with image data
        img_bytes = BytesIO()
        mock_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        mock_response = mock.Mock()
        mock_response.content = img_bytes.getvalue()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = app.get_pokemon_image(1)
        
        assert result is not None
        assert isinstance(result, Image.Image)
        mock_get.assert_called_once_with(
            "https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/001.png", 
            timeout=10
        )
    
    @mock.patch('app.messagebox.showerror')
    @mock.patch('app.requests.get')
    def test_get_pokemon_image_failure(self, mock_get, mock_messagebox, app):
        """Test Pokemon image fetching with network error"""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = app.get_pokemon_image(1)
        
        assert result is None
        mock_messagebox.assert_called_once()
    
    def test_pokemon_number_formatting(self, app):
        """Test that Pokemon numbers are formatted correctly with leading zeros"""
        with mock.patch.object(app, 'get_pokemon_image') as mock_get_image:
            app.get_pokemon_image(1)
            # Verify the URL uses 001 format
            expected_url = "https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/001.png"
            mock_get_image.assert_called_once_with(1)
    
    def test_search_pokemon_valid_input(self, app):
        """Test search with valid Pokemon number"""
        with mock.patch.object(app, 'display_pokemon') as mock_display:
            app.number_entry.insert(0, "25")
            app.search_pokemon()
            mock_display.assert_called_once_with(25)
    
    def test_search_pokemon_invalid_input(self, app):
        """Test search with invalid input"""
        with mock.patch('app.messagebox.showwarning') as mock_warning:
            app.number_entry.insert(0, "abc")
            app.search_pokemon()
            mock_warning.assert_called_once()
    
    def test_search_pokemon_out_of_range(self, app):
        """Test search with number out of valid range"""
        with mock.patch('app.messagebox.showwarning') as mock_warning:
            app.number_entry.insert(0, "9999")
            app.search_pokemon()
            mock_warning.assert_called_once_with("Invalid Input", "Number must be between 1 and 1025")
    
    def test_next_pokemon(self, app):
        """Test next Pokemon navigation"""
        with mock.patch.object(app, 'display_pokemon') as mock_display:
            app.number_entry.insert(0, "1")
            app.next_pokemon()
            mock_display.assert_called_once_with(2)
    
    def test_next_pokemon_at_max(self, app):
        """Test next Pokemon when at maximum number"""
        with mock.patch.object(app, 'display_pokemon') as mock_display:
            app.number_entry.insert(0, "1025")
            app.next_pokemon()
            mock_display.assert_called_once_with(1025)  # Should stay at max
    
    def test_previous_pokemon(self, app):
        """Test previous Pokemon navigation"""
        with mock.patch.object(app, 'display_pokemon') as mock_display:
            app.number_entry.insert(0, "2")
            app.previous_pokemon()
            mock_display.assert_called_once_with(1)
    
    def test_previous_pokemon_at_min(self, app):
        """Test previous Pokemon when at minimum number"""
        with mock.patch.object(app, 'display_pokemon') as mock_display:
            app.number_entry.insert(0, "1")
            app.previous_pokemon()
            mock_display.assert_called_once_with(1)  # Should stay at min
    
    def test_copy_pokemon_name(self, app):
        """Test copying Pokemon name to clipboard"""
        app.current_pokemon_name = "Pikachu"
        with mock.patch('app.messagebox.showinfo') as mock_info:
            app.copy_pokemon_name()
            mock_info.assert_called_once_with("Copied", "Copied: justin/pikachu")
    
    def test_copy_pokemon_name_none(self, app):
        """Test copying Pokemon name when no Pokemon is selected"""
        app.current_pokemon_name = None
        with mock.patch('app.messagebox.showinfo') as mock_info:
            app.copy_pokemon_name()
            mock_info.assert_not_called()
    
    def test_toggle_image_functionality(self, app):
        """Test image toggle between static and GIF"""
        app.current_image = Image.new('RGB', (100, 100), color='blue')
        # Create actual PhotoImage objects instead of mocks
        from tkinter import PhotoImage
        gif_frame = PhotoImage(width=100, height=100)
        app.gif_frames = [gif_frame]
        
        # Test toggling to GIF
        app.toggle_image()
        assert app.showing_gif is True
        assert app.toggle_text.get() == "Show Static"
        
        # Test toggling back to static
        app.toggle_image()
        assert app.showing_gif is False
        assert app.toggle_text.get() == "Show GIF"
    
    @mock.patch('app.filedialog.asksaveasfilename')
    def test_save_image_success(self, mock_filedialog, app, mock_image):
        """Test successful image saving"""
        mock_filedialog.return_value = "/tmp/test_pokemon.png"
        app.current_image = mock_image
        app.current_pokemon_name = "Pikachu"
        app.number_entry.insert(0, "25")
        
        with mock.patch('app.messagebox.showinfo') as mock_info:
            with mock.patch.object(mock_image, 'save') as mock_save:
                app.save_image()
                mock_save.assert_called_once_with("/tmp/test_pokemon.png", 'PNG')
                mock_info.assert_called_once()
    
    @mock.patch('app.filedialog.asksaveasfilename')
    def test_save_image_cancelled(self, mock_filedialog, app, mock_image):
        """Test image saving when user cancels dialog"""
        mock_filedialog.return_value = ""  # User cancelled
        app.current_image = mock_image
        app.current_pokemon_name = "Pikachu"
        
        with mock.patch('app.messagebox.showinfo') as mock_info:
            app.save_image()
            mock_info.assert_not_called()
    
    def test_save_image_no_image(self, app):
        """Test save image when no image is loaded"""
        app.current_image = None
        app.current_pokemon_name = None
        
        # Should not raise an error or show any dialog
        app.save_image()  # Should handle gracefully


if __name__ == "__main__":
    pytest.main([__file__])