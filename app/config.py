import os
from dotenv import load_dotenv
import cohere

# Load environment variables from .env file
load_dotenv()

# Cohere API configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY environment variable is not set")

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "vector_db")

co = cohere.Client(COHERE_API_KEY) 