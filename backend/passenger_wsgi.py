# backend/passenger_wsgi.py
import sys
import os

# Add your project to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import your Flask app
from app import app as application

# Optional: Set environment variables
if __name__ == "__main__":
    application.run()