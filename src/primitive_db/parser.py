# src/primitive_db/parser.py
from primitive_db.constants import VALID_TYPES


def split_values(values_str: str) -> list[str]:
    #Разбивает строку значений '(v1, v2, "v3")' на список, учитывая кавычки
    values_str = values_str.strip()
    if values_str.startswith("(") and values_str.endswith(")"):
        values_str = values_str[1:-1]

    result = []
    current = []
    in_quotes = False
    quote_char = None

    for ch in values_str:
        if ch in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = ch
            current.append(ch)
        elif ch == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current.append(ch)
        elif ch == "," and not in_quotes:
            result.append("".join(current).strip())
            current = []
        else:
            current.append(ch)

    if current:
        result.append("".join(current).strip())

    return [v for v in result if v]


def parse_condition(condition_str: str, schema: dict) -> tuple[bool, dict]:
    #Парсит условие вида 'age = 28' или 'age = 28, name = "Alex"
    result = {}
    conditions = condition_str.split(",")

    for cond in conditions:
        cond = cond.strip()
        if not cond:
            continue
        if "=" not in cond:
            return False, {}

        key, _, value = cond.partition("=")
        key = key.strip()
        value = value.strip()

        if not key or not value:
            return False, {}

        if key not in schema:
            return False, {}

        expected_type = schema[key]

        if expected_type == "int":
            try:
                result[key] = int(value)
            except ValueError:
                return False, {}
        elif expected_type == "str":
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            result[key] = value
        elif expected_type == "bool":
            low = value.lower()
            if low in ("true", "1"):
                result[key] = True
            elif low in ("false", "0"):
                result[key] = False
            else:
                return False, {}

    return True, result