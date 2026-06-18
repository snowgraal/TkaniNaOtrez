import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

from app import app as application