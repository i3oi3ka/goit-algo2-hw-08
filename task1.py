import random
import time
from functools import lru_cache  # Імпортуємо готовий декоратор
from typing import Tuple

# --- Клас LRUCache та функції range/update_with_cache видалені ---
# ...

# --- 2. Функції для генерації запитів (без змін) ---


def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    """Генерує список "гарячих" та випадкових запитів."""
    # Створюємо пул "гарячих" діапазонів
    hot = [
        (random.randint(0, n // 2), random.randint(n // 2, n - 1))
        for _ in range(hot_pool)
    ]

    queries = []
    for _ in range(q):
        if random.random() < p_update:  # ~3% запитів — Update
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:  # ~97% — Range
            if random.random() < p_hot:  # 95% — «гарячі» діапазони
                left, right = random.choice(hot)
            else:  # 5% — випадкові діапазони
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


# --- 3. Функції БЕЗ кешування (без змін) ---


def range_sum_no_cache(array, left, right):
    """Обчислює суму 'в лоб', проходячи по діапазону."""
    return sum(array[left : right + 1])


def update_no_cache(array, index, value):
    """Просто оновлює значення в масиві."""
    array[index] = value


# --- 4. Логіка З кешуванням (з використанням @lru_cache) ---


class CachedArrayHandler:
    """
    Інкапсулює масив та методи роботи з ним,
    використовуючи @lru_cache для методу get_sum.
    """

    def __init__(self, array_data, cache_capacity: int):
        self.array = array_data

        # Ми не можемо просто прикрасити get_sum декоратором @lru_cache,
        # оскільки cache_capacity - це змінна.
        # Тому ми "прикрашаємо" метод вручну під час ініціалізації.
        self.get_sum = lru_cache(maxsize=cache_capacity)(self._get_sum_internal)

    def _get_sum_internal(self, left: int, right: int) -> int:
        """
        Внутрішній метод, який реально обчислює суму.
        Саме він буде кешований.
        """
        # print(f"Cache MISS for ({left}, {right})") # Для дебагу
        return sum(self.array[left : right + 1])

    def update(self, index: int, value: int) -> None:
        """
        Оновлює значення в масиві та повністю очищує кеш.
        """
        # 1. Оновити сам масив
        self.array[index] = value

        # 2. Інвалідація кешу
        # functools.lru_cache не дозволяє видаляти окремі
        # "протухлі" ключі. Ми змушені очистити ВЕСЬ кеш.
        self.get_sum.cache_clear()


# --- 5. Головний блок тестування ---


def main():
    # Налаштування симуляції
    N = 100_000  # Розмір масиву
    Q = 50_000  # Кількість запитів
    K = 1000  # Ємність кешу

    # --- Підготовка ---
    print(f"Генерація {N} елементів базового масиву...")
    base_array = [random.randint(1, 100) for _ in range(N)]

    print(f"Генерація {Q} запитів (3% Update, 95% 'гарячих' Range)...")
    queries = make_queries(N, Q)
    print("Підготовка завершена.\n")

    # --- Тест 1: БЕЗ кешу ---
    print("--- Тестування БЕЗ кешу ---")
    array_no_cache = list(base_array)
    start_time_no_cache = time.time()

    results_no_cache = []
    for query_type, *args in queries:
        if query_type == "Range":
            res = range_sum_no_cache(array_no_cache, args[0], args[1])
            results_no_cache.append(res)
        elif query_type == "Update":
            update_no_cache(array_no_cache, args[0], args[1])

    end_time_no_cache = time.time()
    time_taken_no_cache = end_time_no_cache - start_time_no_cache

    print(f"✅ Час виконання без кешу: {time_taken_no_cache:.4f} секунд")

    # --- Тест 2: З @lru_cache ---
    print(f"\n--- Тестування З @lru_cache (K={K}) ---")

    # Створюємо копію масиву та наш об'єкт-обгортку
    array_with_cache = list(base_array)
    handler = CachedArrayHandler(array_with_cache, cache_capacity=K)

    start_time_with_cache = time.time()

    results_with_cache = []
    for query_type, *args in queries:
        if query_type == "Range":
            # Викликаємо кешований метод
            res = handler.get_sum(args[0], args[1])
            results_with_cache.append(res)
        elif query_type == "Update":
            # Викликаємо метод, який оновить масив і очистить кеш
            handler.update(args[0], args[1])

    end_time_with_cache = time.time()
    time_taken_with_cache = end_time_with_cache - start_time_with_cache

    print(f"✅ Час виконання з @lru_cache: {time_taken_with_cache:.4f} секунд")

    # --- Підсумок ---
    print("\n--- РЕЗУЛЬТАТИ ---")
    print(f"Результати збігаються: {results_no_cache == results_with_cache}")

    if time_taken_with_cache > 0:
        speedup = time_taken_no_cache / time_taken_with_cache
        print(f"🚀 Прискорення за рахунок @lru_cache: {speedup:.2f}x")
    else:
        print("Виконання було надто швидким для вимірювання прискорення.")

    # Демонстрація статистики кешу
    print(f"Статистика кешу: {handler.get_sum.cache_info()}")


if __name__ == "__main__":
    main()
