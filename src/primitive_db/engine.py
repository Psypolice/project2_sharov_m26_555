# src/primitive_db/engine.py
import os
import shlex

from prettytable import PrettyTable
from primitive_db.core import (
    create_table, drop_table, list_tables,
    insert, select, update, delete
)
from primitive_db.utils import (
    load_metadata, save_metadata, 
    load_table_data, save_table_data
)

import prompt

META_FILE = os.path.join(os.getcwd(), "db_meta.json")
FILE_DIR = os.path.join(os.getcwd(), "data")

def _split_values(values_str: str) -> list[str]:
    #Разбиваем строку значений '(v1, v2, "v3")' на список, учитывая кавычки.
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

def _parse_condition(condition_str, schema):
    #Парсит условие вида 'age = 28' или 'age = 28, name = Alex'.
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

        #Определяем тип по схеме таблицы
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

def _print_table(rows: list, columns: list) -> None:
    #Выводит таблицу в красивом формате
    table = PrettyTable()
    table.field_names = columns
    for row in rows:
        table.add_row([row.get(c, "") for c in columns])
    print(table)


def print_help():
    print("\n***Операции с данными***")
    print("Функции:")
    print("  create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу")
    print("  list_tables - показать список всех таблиц")
    print("  drop_table <имя_таблицы> - удалить таблицу")
    print("  info <имя_таблицы> - информация о таблице")
    print("  insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - добавить запись")
    print("  select from <имя_таблицы> [where <условие>] - выбрать записи")
    print("  update <имя_таблицы> set <присваивания> where <условие> - обновить записи")
    print("  delete from <имя_таблицы> where <условие> - удалить записи")
    print("  exit - выход из программы")
    print("  help - справочная информация\n")

def print_welcome():
    """Выводит приветственное сообщение."""
    print("\nПервая попытка запустить проект!")
    print()
    print("***")
    print("  exit - выйти из программы")
    print("  help - справочная информация")
    print()

def run():
    #Главный цикл программы
    print_welcome()

    while True:
        user_input = prompt.string("Введите команду: ").strip()
        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]
        metadata = load_metadata(META_FILE)

        if command == "exit":
            print("Выход из программы. До свидания!")
            break

        if command == "help":
            print_help()
            continue

        if command == "list_tables":
            print(list_tables(metadata))
            continue

        if command == "info":
            if len(args) != 2:
                print("Синтаксис: info <имя_таблицы>")
                continue
            table_name = args[1]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            schema = metadata[table_name]
            cols = ", ".join(f"{k}:{v}" for k, v in schema.items())
            data = load_table_data(table_name, FILE_DIR)
            print(f"Таблица: {table_name}")
            print(f"Столбцы: {cols}")
            print(f"Количество записей: {len(data)}")
            continue

        if command == "create_table":
            if len(args) < 3:
                print("Некорректное значение: create_table требует имя таблицы и хотя бы"
                      " один столбец.")
                continue
            table_name = args[1]
            columns = args[2:]
            success, message = create_table(metadata, table_name, columns)
            if success:
                save_metadata(META_FILE, metadata)
            print(message)
            continue

        if command == "drop_table":
            if len(args) != 2:
                print("Некорректное значение: drop_table требует имя таблицы.")
                continue
            table_name = args[1]
            success, message = drop_table(metadata, table_name)
            if success:
                save_metadata(META_FILE, metadata)
                #Удаляем файл данных
                data_file = os.path.join(FILE_DIR, f"{table_name}.json")
                if os.path.exists(data_file):
                    os.remove(data_file)
            print(message)
            continue

        if command == "insert":
            if len(args) < 5 or args[1].lower() != "into" or args[3].lower() != "values":
                print('Синтаксис: insert into <имя_таблицы> values (<значение1>, <значение2>, ...)')
                continue
            table_name = args[2]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            values_str = " ".join(args[4:])
            values = _split_values(values_str)

            table_data = load_table_data(table_name, FILE_DIR)
            success, message, record, table_data = insert(metadata, table_name, table_data, values)

            if success:
                save_table_data(table_name, table_data, FILE_DIR)
            print(message)
            continue

        if command == "select":
            if len(args) < 3 or args[1].lower() != "from":
                print('Синтаксис: select from <имя_таблицы> [where <условие>]')
                continue
            table_name = args[2]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            where_clause = None
            if len(args) >= 5 and args[3].lower() == "where":
                where_str = " ".join(args[4:])
                schema = metadata[table_name]
                success, where_clause = _parse_condition(where_str, schema)
                if not success:
                    print(f"Некорректное условие: {where_str}")
                    continue

            table_data = load_table_data(table_name, FILE_DIR)
            result = select(table_data, where_clause)
            columns = list(metadata[table_name].keys())
            _print_table(result, columns)
            continue

        if command == "update":
            #update <table> set <set_clause> where <where_clause>
            if len(args) < 6:
                print('Синтаксис: update <имя_таблицы> set <присваивания> where <условие>')
                continue
            table_name = args[1]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            if args[2].lower() != "set":
                print("Ожидается ключевое слово 'set'.")
                continue

            try:
                where_idx = len(args) - 1 - args[::-1].index("where")
            except ValueError:
                print("Ожидается ключевое слово 'where'.")
                continue

            if where_idx < 4:
                print("Некорректный синтаксис update.")
                continue

            set_str = " ".join(args[3:where_idx])
            where_str = " ".join(args[where_idx + 1:])

            schema = metadata[table_name]
            success_set, set_clause = _parse_condition(set_str, schema)
            success_where, where_clause = _parse_condition(where_str, schema)

            if not success_set or not success_where:
                print("Некорректное значение в set или where.")
                continue

            table_data = load_table_data(table_name, FILE_DIR)
            updated_count, table_data = update(table_data, set_clause, where_clause)
            save_table_data(table_name, table_data, FILE_DIR)
            print(f"Обновлено записей: {updated_count}.")
            continue

        if command == "delete":
            #delete <table> where <where_clause>
            if len(args) < 5 or args[1].lower() != "from" or args[3].lower() != "where":
                print('Синтаксис: delete from <имя_таблицы> where <условие>')
                continue
            table_name = args[2]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            where_str = " ".join(args[4:])
            schema = metadata[table_name]
            success, where_clause = _parse_condition(where_str, schema)
            if not success:
                print(f"Некорректное условие: {where_str}")
                continue

            table_data = load_table_data(table_name, FILE_DIR)
            deleted_count, table_data = delete(table_data, where_clause)
            save_table_data(table_name, table_data, FILE_DIR)
            print(f"Удалено записей: {deleted_count}.")
            continue

        print(f"Функции {command} нет. Попробуйте снова.")