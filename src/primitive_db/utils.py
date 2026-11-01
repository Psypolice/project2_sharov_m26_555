# src/primitive_db/utils.py
import json
import os

def load_metadata(filepath):
    #Загружаем данные из JSON
    try:
        with open(filepath, "r", encoding="utf-8") as db:
            return json.load(db)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"Ошибка: файл {filepath} повреждён.")
        return {}

def save_metadata(filepath, data):
    #Сохранем данные в JSON
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as db:
        json.dump(data, db, ensure_ascii=False, indent=2)

def load_table_data(table_name, data_dir="data"):
    #Загружаем данные таблицы из JSON
    filepath = os.path.join(data_dir, f"{table_name}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as table:
            return json.load(table)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Ошибка: файл {filepath} повреждён.")
        return []

def save_table_data(table_name, data, data_dir="data"):
    #Сохранеям данные таблицы в JSON
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, f"{table_name}.json")
    with open(filepath, "w", encoding="utf-8") as table:
        json.dump(data, table, ensure_ascii=False, indent=2)