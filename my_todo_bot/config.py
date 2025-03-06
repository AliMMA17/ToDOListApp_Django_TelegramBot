# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")