import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent / "chatbot 5"
sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(PROJECT_DIR / "backend"))

from appy import app
