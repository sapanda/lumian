# Note:
Make sure you are in the synthesis folder

# Installing libs
pip install -r requirements.txt

# Running migrations
PYTHONPATH=. python migrations/create_transcript_table_schema.py

# Running tests
PYTHONPATH=. pytest tests

# Running the app
uvicorn app.server:app --host 0.0.0.0 --port $PORT

# While Developing
uvicorn app.server:app --reload --port $PORT