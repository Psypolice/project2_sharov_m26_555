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
    for col in columns:
        parsed_col = _parse_column(col)
        if parsed_col is None:
            return False, f'Некорректное занчение {col}. Попробуйте снова'
        name, col_type = parsed_col
        parsed[name] = col_type

    parsed = {"ID": "int", **parsed}

    metadata[table_name] = parsed

    columns_str = ", ".join(f"{k}:{v}" for k, v in parsed.items())
    return True, f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}'