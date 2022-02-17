# CheckMeIn
a system for checking into and out of a building

# Setup
You'll need a python venv, set it up like this:
  1. ```python3 -m venv venv```
  2. ```source venv/bin/activate```
  3. ```pip install -r requirements.txt```
  4. ```mkdir testData```
  5. ```echo "l1n5Be5G9GHFXTSMi6tb0O6o5AKmTC68OjF2UmaU55A=" > testData/checkmein.key```
  6. ```mkdir sessions```
* see section: Temporary notes for trouble shooting below if you are on pi

## Running tests
To make sure you haven't broken anything where it will crash, run the tests using:
  ```python -m pytest tests```

If a test fails and you want to eliminate it temporarily, rename it to not end in "py". For example,
```mv tests/sampleTest.py tests/sampleTest.py.ignore```
DO NOT push these renamed files to the origin repository.

## Launching the server on your test platform
Once you are satisfied that you have the dependencies met, and the unit tests are passing, then to run the
server, you will execute:

```python3 checkmein.py development.conf```

You can connect to your server using a local browser at "http://localhost:8089"
Note: 
* When first starting, assuming you ran the tests, you may choose to
```mkdir data```
```cp testData test.db data/checkmein.db```
This gives you a database with a couple of members and an admin user whose name 
is 'admin' and password is 'password'. 

We may want to build a command line tool that takes something like some kind of sqlite "markdown" 
and populates the database to make playing with capabilities easier. (not hard to do that)

Along these lines , it is handy to
```sudo apt install sqlitebrowswer```
because one can view the database contents using this tool.

## Temporary notes for trouble shooting
* On recent releases of Raspberry Pi OS, it may be necessary to
```sudo apt install libatlas-base-dev```
to get numpy to work in python3.
