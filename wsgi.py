import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent / "chatbot 5"
sys.path.insert(0, str(PROJECT_DIR))

from backend.appy import app
