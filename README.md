# Simple PyTest Demo

A basic calculator module with pytest examples for automation testing, including Selenium WebDriver integration.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run only calculator tests (non-Selenium)
```bash
pytest -m "not selenium"
```

### Run only Selenium tests
```bash
pytest -m selenium
```

### Run tests with specific browser
```bash
pytest -m selenium --browser=chrome
pytest -m selenium --browser=firefox
```

### Run tests in headless mode
```bash
pytest -m selenium --headless
```

## Available Functions

- `add(a, b)`: Add two numbers
- `subtract(a, b)`: Subtract b from a
- `multiply(a, b)`: Multiply two numbers

## Project Structure

- `calculator.py`: Contains the calculator functions
- `tests/test_calculator.py`: Unit tests for calculator functions
- `tests/test_selenium_example.py`: Selenium WebDriver example tests
- `tests/conftest.py`: Pytest fixtures and configuration
- `pytest.ini`: Pytest configuration

This repository is designed for testing automation systems and CI/CD pipelines.
