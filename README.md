# Blockchain Lab

An educational blockchain implementation project built with Python.

## Quick Start

### Create and Activate Virtual Environment

#### Windows
```powershell
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

#### Linux/macOS
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the tests
```
pytest -q
```

## Project Structure

- `core/`: Core blockchain components (blocks, transactions, chain)
- `node/`: Node implementations (full node, light wallet)
- `crypto/`: Cryptographic utilities (merkle trees, bloom filters, keys)
- `sim/`: Simulation data and utilities
- `cli/`: Command-line interface
- `tests/`: Test suite

## Features

- Block creation and validation
- Transaction handling
- Mining with proof of work
- Cryptographic utilities (keys, signatures)
- Light wallet functionality
- Memory pool for unconfirmed transactions

## License

This project is for educational purposes.
