# src/primitive_db/core.py
def _parse_column(column_str):
    if ":" not in column_str:
        return None
    parts = column_str.split(":", 1)
    if len(parts) != 2:
        return None
    name, col_type = parts
    if not name or not col_type:
        return None
    if col_type not in {"int", "str", "bool"}:
        return None
    return name, col_type

def create_table(metadata, table_name, columns):
    if table_name in metadata:
        return False, f'Ошибка: Таблица "{table_name}" уже существует.'

    parsed = {}
    has_id = False
    for col in columns:
        parsed_col = _parse_column(col)
        if parsed_col is None:
            return False, f'Некорректное занчение {col}. Попробуйте снова'
        name, col_type = parsed_col
        if name == "ID":
            has_id = True
        parsed[name] = col_type

    if not has_id:
        parsed = {"ID": "int", **parsed}

    metadata[table_name] = parsed

    columns_str = ", ".join(f"{k}:{v}" for k, v in parsed.items())
    return True, f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}'


def drop_table(metadata, table_name):
    if table_name not in metadata:
        return False, f'Ошибка: Таблица "{table_name}" не существует.'
    del metadata[table_name]
    return True, f'Таблица "{table_name}" успешно удалена.'


def list_tables(metadata: dict) -> str:
    if not metadata:
        return "Таблицы не найдены."
    return "\n".join(f"- {name}" for name in metadata)