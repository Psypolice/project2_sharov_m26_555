# src/primitive_db/decorators.py
import time

import prompt

def handle_db_errors(func):
    # Декоратор для централизованной обработки ошибок БД
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print(f"Ошибка: Файл данных не найден. {e}")
            return None
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
            return None
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return None
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            return None

    return wrapper


def confirm_action(action_name):
    # Фабрика декораторов для подтверждения опасных операций
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                answer = (
                    prompt.string(
                        f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
                    )
                    .strip()
                    .lower()
                )
            except (EOFError, KeyboardInterrupt):
                print("\nОперация отменена.")
                return None
            if answer != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    # Декоратор для замера времени выполнения функции
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f"Функция {func.__name__} выполнилась за {end - start:.3f} секунд.")
        return result

    return wrapper


def create_cacher():
    """Функция с замыканием для кэширования результатов.

    Возвращает кортеж: (cache_result, invalidate_cache)
    - cache_result(key, value_func) — возвращает кэшированный результат или вычисляет
    - invalidate_cache() — очищает кэш
    """
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            print(f"[Кэш] Результат для ключа {key} получен из кэша.")
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    def invalidate_cache():
        cache.clear()

    return cache_result, invalidate_cache
