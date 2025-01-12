# Postman to Pytest Converter

Convert Postman collection JSON files into pytest test files.

## Features (Phase 1 - MVP)

- Basic conversion of Postman collections to pytest files
- Support for essential HTTP methods (GET, POST, PUT, DELETE)
- Basic authentication support (Bearer token)
- Basic proxy support (HTTP/HTTPS)
- Directory structure that mirrors API paths
- Tests organized by HTTP verb per endpoint

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd postman-to-pytest

# Install the package
pip install .
```

## Usage

Basic usage:

```bash
postman2pytest input.json --output ./tests
```

Options:
- `input.json`: Path to Postman collection JSON file
- `--output`: Directory where test files will be generated (default: ./tests)
- `--help`: Show help message and exit

## Project Structure

```
postman2pytest/
├── src/              # Source code
├── tests/            # Test files
├── collections/      # Sample Postman collections
└── auth/             # Authentication handling
```

## Dependencies

- Python 3.8+
- pytest
- requests[socks]
- requests-oauthlib
- pydantic
- click
- urllib3
- python-dotenv

## Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest
```

## License

MIT

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
