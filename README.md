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

This project includes a comprehensive test suite built with pytest. To run the tests:

1. Install test dependencies:
   ```bash
   pip install -r src/requirements.txt
   ```

2. Run all tests:
   ```bash
   pytest
   ```

3. Run tests with verbose output:
   ```bash
   pytest -v
   ```

4. Run tests with coverage (optional):
   ```bash
   pip install pytest-cov
   pytest --cov=src
   ```

The test suite includes:
- Unit tests for core Pokemon data fetching functionality
- Tests for image downloading and processing
- GUI interaction tests using virtual display (xvfb)
- Error handling and edge case tests
- Mock tests for external API dependencies

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