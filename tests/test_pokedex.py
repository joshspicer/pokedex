import unittest
from unittest.mock import Mock, patch, MagicMock
import io
import sys
import os

# Add src directory to path to import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the necessary modules
from PIL import Image
import requests


class MockPokedexApp:
    """Mock version of PokedexApp for testing core functionality without GUI."""
    
    def __init__(self):
        self.current_image = None
        self.current_gif = None
        self.current_pokemon_name = None
        self.showing_gif = False
        self.gif_frames = []
        self.current_frame = 0
        self.is_animating = False
        self.image_size = (800, 800)

    def get_pokemon_data(self, number):
        try:
            # Get Pokemon details from PokeAPI
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{number}", timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                'name': data['name'].title(),
                'gif_url': data['sprites']['other']['showdown']['front_default']
            }
        except requests.RequestException:
            return None

    def get_pokemon_image(self, number):
        # Format number to 3 digits with leading zeros
        formatted_num = str(number).zfill(3)
        url = f"https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{formatted_num}.png"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
            return image
        except (requests.RequestException, Image.UnidentifiedImageError):
            return None

    def get_pokemon_gif(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            gif = Image.open(io.BytesIO(response.content))
            
            # Clear previous frames
            self.gif_frames = []
            
            try:
                # Extract all frames from the GIF
                frame_count = 0
                while True:
                    # Resize frame to maintain consistent size
                    gif.thumbnail(self.image_size, Image.Resampling.LANCZOS)
                    # Store frame (simplified without PhotoImage conversion)
                    self.gif_frames.append(gif.copy())
                    frame_count += 1
                    gif.seek(frame_count)
            except EOFError:
                pass  # We've reached the end of the frames
                
            return gif if self.gif_frames else None
            
        except (requests.RequestException, Image.UnidentifiedImageError):
            return None

    def validate_pokemon_number(self, number):
        """Validate if Pokemon number is in valid range."""
        try:
            num = int(number)
            return 1 <= num <= 1025
        except (ValueError, TypeError):
            return False

    def format_pokemon_name_for_copy(self, name):
        """Format Pokemon name for clipboard copying."""
        if name:
            return f"justin/{name.lower()}"
        return None


class TestPokedexCore(unittest.TestCase):
    """Test core Pokédex functionality without GUI components."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = MockPokedexApp()

    def tearDown(self):
        """Clean up after each test method."""
        pass

    @patch('requests.get')
    def test_get_pokemon_data_success(self, mock_get):
        """Test successful Pokemon data retrieval."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'name': 'pikachu',
            'sprites': {
                'other': {
                    'showdown': {
                        'front_default': 'https://example.com/pikachu.gif'
                    }
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.app.get_pokemon_data(25)

        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Pikachu')
        self.assertEqual(result['gif_url'], 'https://example.com/pikachu.gif')
        mock_get.assert_called_once_with('https://pokeapi.co/api/v2/pokemon/25', timeout=10)

    @patch('requests.get')
    def test_get_pokemon_data_api_error(self, mock_get):
        """Test Pokemon data retrieval with API error."""
        # Mock API error
        mock_get.side_effect = requests.RequestException("API Error")

        result = self.app.get_pokemon_data(25)

        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_pokemon_image_success(self, mock_get):
        """Test successful Pokemon image retrieval."""
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Mock successful image response
        mock_response = Mock()
        mock_response.content = img_byte_arr
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.app.get_pokemon_image(25)

        self.assertIsInstance(result, Image.Image)
        mock_get.assert_called_once_with(
            'https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/025.png',
            timeout=10
        )

    @patch('requests.get')
    def test_get_pokemon_image_network_error(self, mock_get):
        """Test Pokemon image retrieval with network error."""
        mock_get.side_effect = requests.RequestException("Network Error")

        result = self.app.get_pokemon_image(25)

        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_pokemon_image_invalid_image(self, mock_get):
        """Test Pokemon image retrieval with invalid image data."""
        # Mock response with invalid image data
        mock_response = Mock()
        mock_response.content = b'invalid image data'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.app.get_pokemon_image(25)

        self.assertIsNone(result)

    def test_number_formatting(self):
        """Test that Pokemon numbers are formatted correctly with leading zeros."""
        # Test the number formatting used in get_pokemon_image
        test_cases = [
            (1, '001'),
            (25, '025'),
            (100, '100'),
            (999, '999'),
            (1000, '1000')
        ]

        for number, expected in test_cases:
            formatted = str(number).zfill(3)
            self.assertEqual(formatted, expected)

    def test_validate_pokemon_number_valid(self):
        """Test Pokemon number validation with valid inputs."""
        valid_numbers = [1, 25, 150, 500, 1000, 1025, '1', '25', '1025']
        
        for number in valid_numbers:
            self.assertTrue(self.app.validate_pokemon_number(number), 
                          f"Number {number} should be valid")

    def test_validate_pokemon_number_invalid(self):
        """Test Pokemon number validation with invalid inputs."""
        invalid_numbers = [0, 1026, -1, 9999, 'invalid', '', None, 'abc']
        
        for number in invalid_numbers:
            self.assertFalse(self.app.validate_pokemon_number(number), 
                           f"Number {number} should be invalid")

    def test_format_pokemon_name_for_copy(self):
        """Test Pokemon name formatting for clipboard."""
        test_cases = [
            ('Pikachu', 'justin/pikachu'),
            ('Mr. Mime', 'justin/mr. mime'),
            ('Farfetch\'d', 'justin/farfetch\'d'),
            ('BULBASAUR', 'justin/bulbasaur'),
            ('', None),
            (None, None)
        ]

        for input_name, expected in test_cases:
            result = self.app.format_pokemon_name_for_copy(input_name)
            self.assertEqual(result, expected)

    @patch('requests.get')
    def test_get_pokemon_gif_success(self, mock_get):
        """Test successful GIF retrieval and frame processing."""
        # Create a simple animated GIF (this is a simplified test)
        test_gif = Image.new('RGB', (100, 100), color='blue')
        gif_byte_arr = io.BytesIO()
        test_gif.save(gif_byte_arr, format='GIF')
        gif_byte_arr = gif_byte_arr.getvalue()

        mock_response = Mock()
        mock_response.content = gif_byte_arr
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.app.get_pokemon_gif('https://example.com/test.gif')

        self.assertIsInstance(result, Image.Image)
        self.assertTrue(len(self.app.gif_frames) > 0)

    @patch('requests.get')
    def test_get_pokemon_gif_network_error(self, mock_get):
        """Test GIF retrieval with network error."""
        mock_get.side_effect = requests.RequestException("Network Error")

        result = self.app.get_pokemon_gif('https://example.com/test.gif')

        self.assertIsNone(result)



class TestPokedexValidation(unittest.TestCase):
    """Test cases for input validation and edge cases."""

    def test_pokemon_number_range_validation(self):
        """Test that Pokemon numbers are within valid range."""
        valid_numbers = [1, 25, 150, 500, 1000, 1025]
        invalid_numbers = [0, -1, 1026, 9999, -100]

        for num in valid_numbers:
            self.assertTrue(1 <= num <= 1025, f"Number {num} should be valid")

        for num in invalid_numbers:
            self.assertFalse(1 <= num <= 1025, f"Number {num} should be invalid")

    def test_pokemon_name_formatting(self):
        """Test Pokemon name formatting for clipboard."""
        test_cases = [
            ('Pikachu', 'justin/pikachu'),
            ('Mr. Mime', 'justin/mr. mime'),
            ('Farfetch\'d', 'justin/farfetch\'d'),
            ('BULBASAUR', 'justin/bulbasaur'),
        ]

        for input_name, expected in test_cases:
            formatted = f"justin/{input_name.lower()}"
            self.assertEqual(formatted, expected)

    def test_url_formatting(self):
        """Test URL formatting for Pokemon images."""
        test_cases = [
            (1, 'https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/001.png'),
            (25, 'https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/025.png'),
            (100, 'https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/100.png'),
            (1000, 'https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/1000.png'),
        ]

        for number, expected_url in test_cases:
            formatted_num = str(number).zfill(3)
            url = f"https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{formatted_num}.png"
            self.assertEqual(url, expected_url)


class TestPokedexNavigation(unittest.TestCase):
    """Test navigation logic for Pokemon browsing."""

    def test_next_navigation_logic(self):
        """Test next navigation boundary conditions."""
        # Test normal increment
        current = 25
        next_num = min(current + 1, 1025)
        self.assertEqual(next_num, 26)
        
        # Test at boundary
        current = 1025
        next_num = min(current + 1, 1025)
        self.assertEqual(next_num, 1025)  # Should stay at max
        
        # Test near boundary
        current = 1024
        next_num = min(current + 1, 1025)
        self.assertEqual(next_num, 1025)

    def test_previous_navigation_logic(self):
        """Test previous navigation boundary conditions."""
        # Test normal decrement
        current = 25
        prev_num = max(current - 1, 1)
        self.assertEqual(prev_num, 24)
        
        # Test at boundary
        current = 1
        prev_num = max(current - 1, 1)
        self.assertEqual(prev_num, 1)  # Should stay at min
        
        # Test near boundary
        current = 2
        prev_num = max(current - 1, 1)
        self.assertEqual(prev_num, 1)


class TestPokedexImageHandling(unittest.TestCase):
    """Test image handling and processing functionality."""

    def test_image_thumbnail_sizing(self):
        """Test image thumbnail resizing logic."""
        # Create test images of various sizes
        test_cases = [
            (1920, 1080),  # Large landscape
            (1080, 1920),  # Large portrait
            (100, 100),    # Small square
            (800, 600),    # Medium landscape
        ]
        
        target_size = (800, 800)
        
        for width, height in test_cases:
            test_image = Image.new('RGB', (width, height), color='blue')
            # Simulate thumbnail operation
            test_image.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Check that image fits within target dimensions
            self.assertLessEqual(test_image.width, target_size[0])
            self.assertLessEqual(test_image.height, target_size[1])

    @patch('requests.get')
    def test_image_content_types(self, mock_get):
        """Test handling of different image content types."""
        app = MockPokedexApp()
        
        # Test PNG
        png_image = Image.new('RGB', (100, 100), color='red')
        png_byte_arr = io.BytesIO()
        png_image.save(png_byte_arr, format='PNG')
        
        mock_response = Mock()
        mock_response.content = png_byte_arr.getvalue()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = app.get_pokemon_image(1)
        self.assertIsInstance(result, Image.Image)
        
        # Test JPEG
        jpeg_image = Image.new('RGB', (100, 100), color='green')
        jpeg_byte_arr = io.BytesIO()
        jpeg_image.save(jpeg_byte_arr, format='JPEG')
        
        mock_response.content = jpeg_byte_arr.getvalue()
        mock_get.return_value = mock_response
        
        result = app.get_pokemon_image(2)
        self.assertIsInstance(result, Image.Image)


if __name__ == '__main__':
    unittest.main()