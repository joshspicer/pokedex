# Pokedex App

A simple Pokédex application built with Python and Tkinter that allows users to search for Pokémon by their number and view their images.

## Features

- Search for Pokémon by number (1-1025).
- Navigate through Pokémon images using Previous and Next buttons.
- Copy Pokémon images to your local machine.

## Requirements

- Python 3.x
- `requests`
- `Pillow`

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd pokedex-app
   ```

2. Install the required packages:

   ```bash
   pip install -r src/requirements.txt
   ```

## Running the Application

To run the application, execute the following command:

```bash
python src/app.py
```

## Testing

The application includes a comprehensive unit test suite that covers core functionality:

### Running Tests

```bash
# Run all tests using the test runner
python run_tests.py

# Or run tests directly with unittest
python -m unittest test_pokedex -v

# Run specific test classes
python -m unittest test_pokedex.TestPokedexCore -v
```

### Test Coverage

The test suite includes:
- **Core API functionality**: Pokemon data retrieval from PokeAPI
- **Input validation**: Pokemon number validation and error handling
- **Navigation logic**: Previous/next navigation with boundary conditions
- **Image processing**: Image downloading and format handling
- **Name formatting**: Pokemon name copying functionality
- **Error handling**: Network failures and invalid data scenarios

All tests use mocking for external dependencies (API calls, file operations) to ensure reliable and fast test execution.

## Packaging

To package the application as a standalone executable, you can use tools like `PyInstaller`. 

1. Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

2. Create the executable:

   ```bash
   pyinstaller --onefile src/app.py
   ```

The executable will be created in the `dist` folder.

## License

This project is licensed under the MIT License.