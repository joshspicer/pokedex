# Testing Documentation

This document describes the testing setup for the Pokédex application.

## Test Structure

The tests are organized into several test classes:

- `TestPokedexCore`: Tests core functionality like API calls, image loading, and data processing
- `TestPokedexValidation`: Tests input validation and edge cases
- `TestPokedexNavigation`: Tests navigation logic (next/previous Pokemon)
- `TestPokedexImageHandling`: Tests image processing and manipulation

## Running Tests

### Method 1: Using the test runner script
```bash
python run_tests.py
```

### Method 2: Using unittest directly
```bash
python -m unittest tests.test_pokedex -v
```

### Method 3: Running individual test classes
```bash
python -m unittest tests.test_pokedex.TestPokedexCore -v
python -m unittest tests.test_pokedex.TestPokedexValidation -v
```

## Test Coverage

The tests cover the following functionality:

### Core Features
- ✅ Pokemon data retrieval from PokeAPI
- ✅ Pokemon image downloading
- ✅ Pokemon GIF processing and frame extraction
- ✅ Error handling for network failures
- ✅ Input validation for Pokemon numbers (1-1025)
- ✅ Pokemon name formatting for clipboard copying

### Navigation Logic
- ✅ Next/previous Pokemon navigation
- ✅ Boundary conditions (min/max Pokemon numbers)
- ✅ Invalid input handling

### Image Processing
- ✅ Image thumbnail resizing
- ✅ Different image format support (PNG, JPEG)
- ✅ Invalid image data handling

### Validation
- ✅ Pokemon number range validation
- ✅ URL formatting for Pokemon images
- ✅ Name formatting edge cases

## Test Dependencies

The tests use Python's built-in `unittest` framework and require:
- `unittest.mock` for mocking external dependencies
- `PIL` (Pillow) for image processing
- `requests` for HTTP requests (mocked in tests)

## Test Philosophy

The tests are designed to:
1. **Mock external dependencies**: All API calls and file operations are mocked
2. **Test core logic without GUI**: Focus on business logic rather than UI components
3. **Cover edge cases**: Test boundary conditions and error scenarios
4. **Maintain fast execution**: All tests should run quickly without network calls

## Adding New Tests

When adding new functionality to the Pokédex app, add corresponding tests:

1. Create test methods in the appropriate test class
2. Use descriptive test method names starting with `test_`
3. Mock external dependencies using `@patch` decorator
4. Include both success and failure scenarios
5. Test edge cases and boundary conditions

Example test structure:
```python
@patch('requests.get')
def test_new_feature_success(self, mock_get):
    """Test successful execution of new feature."""
    # Setup mock
    mock_get.return_value = Mock()
    
    # Execute test
    result = self.app.new_feature()
    
    # Assert results
    self.assertIsNotNone(result)
    mock_get.assert_called_once()
```