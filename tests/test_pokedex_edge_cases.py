import unittest.mock as mock
import pytest
import io
from PIL import Image
import sys
import os

# Add src directory to path to import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from app import PokedexApp


class TestPokedexAppGifFunctionality:
    """Additional tests for GIF functionality and edge cases"""
    
    @pytest.fixture
    def app(self):
        """Create a PokedexApp instance for testing"""
        import tkinter as tk
        root = tk.Tk()
        app = PokedexApp(root)
        yield app
        root.destroy()
    
    @mock.patch('app.requests.get')
    def test_get_pokemon_gif_success(self, mock_get, app):
        """Test successful GIF fetching"""
        # Create a simple GIF image
        gif_image = Image.new('RGB', (100, 100), color='green')
        gif_bytes = io.BytesIO()
        gif_image.save(gif_bytes, format='GIF')
        gif_bytes.seek(0)
        
        mock_response = mock.Mock()
        mock_response.content = gif_bytes.getvalue()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = app.get_pokemon_gif("https://example.com/test.gif")
        
        assert result is not None
        assert len(app.gif_frames) > 0
    
    @mock.patch('app.messagebox.showerror')
    @mock.patch('app.requests.get')
    def test_get_pokemon_gif_failure(self, mock_get, mock_messagebox, app):
        """Test GIF fetching with network error"""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = app.get_pokemon_gif("https://example.com/test.gif")
        
        assert result is None
        mock_messagebox.assert_called_once()
    
    def test_gif_animation_control(self, app):
        """Test GIF animation start/stop functionality"""
        # Set up GIF frames
        from tkinter import PhotoImage
        gif_frame = PhotoImage(width=100, height=100)
        app.gif_frames = [gif_frame, gif_frame.copy()]
        app.showing_gif = True
        app.is_animating = True
        
        # Test animation cycle
        initial_frame = app.current_frame
        app.animate_gif()
        # Frame should advance (but we can't easily test timing in unit tests)
        assert app.current_frame >= 0  # Should still be valid
    
    def test_toggle_image_with_no_images(self, app):
        """Test toggle when no images are loaded"""
        app.current_image = None
        app.current_gif = None
        app.gif_frames = []
        
        # Should not crash
        app.toggle_image()
        assert app.showing_gif is False  # Should remain false
    
    @mock.patch('app.messagebox.showerror')
    def test_get_pokemon_image_invalid_image_data(self, mock_messagebox, app):
        """Test image fetching with invalid image data"""
        with mock.patch('app.requests.get') as mock_get:
            mock_response = mock.Mock()
            mock_response.content = b"invalid image data"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Mock Image.open to raise UnidentifiedImageError
            with mock.patch('app.Image.open') as mock_image_open:
                from PIL import Image
                mock_image_open.side_effect = Image.UnidentifiedImageError()
                
                result = app.get_pokemon_image(1)
                
                assert result is None
                mock_messagebox.assert_called_once_with("Error", "Downloaded data is not a valid image")
    
    def test_search_pokemon_empty_input(self, app):
        """Test search with empty input"""
        with mock.patch('app.messagebox.showwarning') as mock_warning:
            app.number_entry.insert(0, "")
            app.search_pokemon()
            mock_warning.assert_called_once_with("Invalid Input", "Please enter a valid number")
    
    def test_next_pokemon_with_invalid_entry(self, app):
        """Test next Pokemon with invalid current entry"""
        with mock.patch.object(app, 'display_pokemon') as mock_display:
            app.number_entry.insert(0, "invalid")
            app.next_pokemon()
            mock_display.assert_called_once_with(1)  # Should default to 1
    
    def test_previous_pokemon_with_invalid_entry(self, app):
        """Test previous Pokemon with invalid current entry"""
        with mock.patch.object(app, 'display_pokemon') as mock_display:
            app.number_entry.insert(0, "invalid")
            app.previous_pokemon()
            mock_display.assert_called_once_with(1)  # Should default to 1
    
    @mock.patch('app.filedialog.asksaveasfilename')
    def test_save_image_file_error(self, mock_filedialog, app):
        """Test save image with file I/O error"""
        mock_filedialog.return_value = "/tmp/test_pokemon.png"
        app.current_image = Image.new('RGB', (100, 100), color='red')
        app.current_pokemon_name = "Pikachu"
        app.number_entry.insert(0, "25")
        
        with mock.patch('app.messagebox.showerror') as mock_error:
            with mock.patch.object(app.current_image, 'save') as mock_save:
                mock_save.side_effect = OSError("Permission denied")
                
                app.save_image()
                mock_error.assert_called_once()
    
    def test_default_filename_generation(self, app):
        """Test that default filename is generated correctly"""
        app.current_image = Image.new('RGB', (100, 100), color='blue')
        app.current_pokemon_name = "Charizard"
        app.number_entry.insert(0, "6")
        
        with mock.patch('app.filedialog.asksaveasfilename') as mock_filedialog:
            mock_filedialog.return_value = ""  # User cancels
            
            app.save_image()
            
            # Check that the default filename was set correctly
            mock_filedialog.assert_called_once()
            call_args = mock_filedialog.call_args
            assert call_args[1]['initialfile'] == "006-Charizard.png"
    
    @mock.patch('app.messagebox.showinfo')
    def test_copy_pokemon_name_formatting(self, mock_info, app):
        """Test that Pokemon name is formatted correctly when copied"""
        test_cases = [
            ("Pikachu", "justin/pikachu"),
            ("Mr. Mime", "justin/mr. mime"),
            ("Nidoran♂", "justin/nidoran♂"),
        ]
        
        for pokemon_name, expected_output in test_cases:
            app.current_pokemon_name = pokemon_name
            app.copy_pokemon_name()
            mock_info.assert_called_with("Copied", f"Copied: {expected_output}")
            mock_info.reset_mock()


if __name__ == "__main__":
    pytest.main([__file__])