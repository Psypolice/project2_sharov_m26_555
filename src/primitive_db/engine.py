# src/primitive_db/engine.py
import os
import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

DATA_FILE = os.path.join(os.getcwd(), "db_meta.json")


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def print_welcome() -> None:
    """Выводит приветственное сообщение."""
    print("\nПервая попытка запустить проект!")
    print()
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    print()

def run():
    print_welcome()

    metadata = load_metadata(DATA_FILE)
    while True:
        user_input = prompt.string("Введите команду: ").strip()
        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError as ex:
            print(f"Некорректное значение: {user_input}. Введите снова")
            continue

        if not args:
            continue

        command = args[0]
        metadata = load_metadata(DATA_FILE)

        if command == "exit":
            break

        if command == "help":
            print_help()
            continue

        if command == "list_tables":
            print(list_tables(metadata))
            continue

        if command == "create_table":
            if len(args) < 3:
                print(
                    "Некорректное значение. Требуется имя таблицы и хотя бы один"
                    "столбец. Попробуйте снова."
                )
                continue
            table_name = args[1]
            columns = args[2:]
            success, message = create_table(metadata, table_name, columns)
            if success:
                save_metadata(DATA_FILE, metadata)
            print(message)
            continue

        if command == "drop_table":
            if len(args) != 2:
                print(
                    "Некорректное значение. Требуется имя таблицы. "
                    "Попробуйте снова."
                )
                continue
            table_name = args[1]
            success, message = drop_table(metadata, table_name)
            if success:
                save_metadata(DATA_FILE, metadata)
            print(message)
            continue

        print(f"Функции {command} нет. Попробуйте снова.")