# src/primitive_db/core.py
from typing import Any

TYPES = {"int", "str", "bool"}

def _parse_column(column_str):
    #Парсит строку 'name:str' в кортеж (name, str)
    if ":" not in column_str:
        return None
    parts = column_str.split(":", 1)
    if len(parts) != 2:
        return None
    name, col_type = parts[0].strip(), parts[1].strip()
    if not name or not col_type:
        return None
    if col_type not in TYPES:
        return None
    return name, col_type

def create_table(metadata, table_name, columns):
    #Создание таблицы
    if table_name in metadata:
        return False, f'Ошибка: Таблица "{table_name}" уже существует.'

    parsed = {}
    for col in columns:
        parsed_col = _parse_column(col)
        if parsed_col is None:
            return False, f"Некорректное значение: {col}. Попробуйте снова."
        name, col_type = parsed_col
        if name in parsed:
            return False, f"Ошибка: столбец '{name}' уже определён."
        parsed[name] = col_type

    #Всегда добавляем ID:int в начало
    parsed = {"ID": "int", **parsed}
    metadata[table_name] = parsed
    columns_str = ", ".join(f"{k}:{v}" for k, v in parsed.items())
    return True, f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}'


def drop_table(metadata, table_name):
    #Удаление таблицы
    if table_name not in metadata:
        return False, f'Ошибка: Таблица "{table_name}" не существует.'
    del metadata[table_name]
    return True, f'Таблица "{table_name}" успешно удалена.'


def list_tables(metadata):
    #Показ списка таблиц
    if not metadata:
        return "Таблицы не найдены."
    return "\n".join(f"- {name}" for name in metadata)

def _validate_value(value, expected_type):
    #Валидирует и преобразует значение согласно типу
    value = value.strip()

    if expected_type == "int":
        try:
            return True, int(value)
        except (ValueError, TypeError):
            return False, None
        
    if expected_type == "str":
        #Убираем кавычки, если они есть
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        return True, value
    
    if expected_type == "bool":
        low = value.lower()
        if low in ("true", "1"):
            return True, True
        if low in ("false", "0"):
            return True, False

    return False, None

def insert(metadata, table_name, table_data, values):
    #Добавляет запись в таблицу
    if table_name not in metadata:
        return False, f'Ошибка: Таблица "{table_name}" не существует.', []

    schema = metadata[table_name]
    #Исключаем ID для подсчёта ожидаемых значений
    schema_without_id = {k: v for k, v in schema.items() if k != "ID"}

    if len(values) != len(schema_without_id):
        return False, (
            f"Ошибка: Ожидалось {len(schema_without_id)} значений, "
            f"получено {len(values)}."
        ), {}, table_data
    #Генерация ID
    max_id = max((r.get("ID", 0) for r in table_data), default=0)
    record = {"ID": max_id + 1}

    #Валидируем и преобразуем значения
    for (col_name, col_type), value in zip(schema_without_id.items(), values):
        success, validated_value = _validate_value(value, col_type)
        if not success:
            return False, f"Некорректное значение: '{value}' для типа {col_type}.", {}, table_data
        record[col_name] = validated_value
    
    table_data.append(record)
    return True, f"Запись с ID={record['ID']} успешно добавлена в таблицу \"{table_name}\".", record, table_data

def select(table_data, where_clause=None):
    #Выбор записей из таблицы
    if where_clause is None:
        return table_data

    result = []
    for record in table_data:
        match = True
        for key, value in where_clause.items():
            if key not in record or record[key] != value:
                match = False
                break
        if match:
            result.append(record)
    return result

def update(table_data, set_clause, where_clause):
    #Обновление записей в таблице
    update_count = 0
    for record in table_data:
        match = True
        for key, value in where_clause.items():
            if key not in record or record[key] != value:
                match = False
                break
        if match:
            for key, value in set_clause.items():
                record[key] = value
            update_count += 1
    return update_count, table_data

def delete(table_data, where_clause):
    #Удаление записей из таблицы
    result = []
    deleted_count = 0
    for record in table_data:
        match = True
        for key, value in where_clause.items():
            if key not in record or record[key] != value:
                match = False
                break
        if match:
            deleted_count += 1
        else:
            result.append(record)
    return deleted_count, result