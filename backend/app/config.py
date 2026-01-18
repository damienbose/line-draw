"""
Configuration for the backend application.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"

# Ensure directories exist
UPLOADS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Simulation defaults
DEFAULT_BLUR_SIGMA = 4.0
DEFAULT_ITERATIONS = 1_500_000
DEFAULT_START_X = 0.5
DEFAULT_START_Y = 0.5
