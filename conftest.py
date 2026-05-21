# conftest.py
# Author: Salma Hani | ID: 120210255
# Ensures pytest adds the project root to sys.path so all imports resolve.

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
