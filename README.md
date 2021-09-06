# CheckMeIn
a system for checking into and out of a building

# Setup
You'll need a python venv, set it up like this:
  1. ```python3 -m venv venv```
  2. ```source venv/bin/activate```
  3. ```pip install -r requirements.txt```

You'll also need a ```sessions``` directory to store session data

## Running tests
To make sure you haven't broken anything where it will crash, run the tests using:
  python -m pytest tests
