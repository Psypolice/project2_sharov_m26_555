# src/primitive_db/constants.py
import os

# Имена файлов и директорий
META_FILE = os.path.join(os.getcwd(), "db_meta.json")
DATA_DIR = os.path.join(os.getcwd(), "data")

# Допустимые типы данных
VALID_TYPES = {"int", "str", "bool"}