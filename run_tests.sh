#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests with coverage
pytest --cov=blockchain tests/ --cov-report=term-missing

# Deactivate virtual environment if it was activated
if [ -d "venv" ]; then
    deactivate
fi 