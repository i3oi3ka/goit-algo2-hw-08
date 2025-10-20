import random
import time
from functools import lru_cache


def range_sum_no_cache(array, left, right):
    return sum(array[left : right + 1])


def update_no_cache(array, index, value):
    array[index] = value


@lru_cache(maxsize=1000)
def cached_sum(array_tuple, left, right):
    return sum(array_tuple[left : right + 1])


def range_sum_with_cache(array, left, right):
    return cached_sum(tuple(array), left, right)


def update_with_cache(array, index, value):
    array[index] = value
    cached_sum.cache_clear()


def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [
        (random.randint(0, n // 2), random.randint(n // 2, n - 1))
        for _ in range(hot_pool)
    ]
    queries = []
    for _ in range(q):
        if random.random() < p_update:
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


def process_queries_no_cache(array, queries):
    for query in queries:
        if query[0] == "Range":
            _, l, r = query
            range_sum_no_cache(array, l, r)
        elif query[0] == "Update":
            _, i, val = query
            update_no_cache(array, i, val)


def process_queries_with_cache(array, queries):
    for query in queries:
        if query[0] == "Range":
            _, l, r = query
            range_sum_with_cache(array, l, r)
        elif query[0] == "Update":
            _, i, val = query
            update_with_cache(array, i, val)


if __name__ == "__main__":
    n = 100_000
    q = 50_000

    array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    # without cache
    arr_copy = array.copy()
    t1 = time.time()
    process_queries_no_cache(arr_copy, queries)
    t_no_cache = time.time() - t1

    # with cache
    arr_copy = array.copy()
    t2 = time.time()
    process_queries_with_cache(arr_copy, queries)
    t_with_cache = time.time() - t2

    # result
    speedup = t_no_cache / t_with_cache if t_with_cache > 0 else float("inf")

    print(f"Без кешу : {t_no_cache:.2f} c")
    print(f"LRU-кеш  : {t_with_cache:.2f} c  (прискорення ×{speedup:.2f})")
