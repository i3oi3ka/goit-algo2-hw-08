import random
import time
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def invalidate(self, index):
        # видаляємо всі діапазони, які містять index
        keys_to_remove = [k for k in self.cache if k[0] <= index <= k[1]]
        for k in keys_to_remove:
            del self.cache[k]


def range_sum_no_cache(array, left, right):
    return sum(array[left : right + 1])


def update_no_cache(array, index, value):
    array[index] = value


cache = LRUCache(capacity=1000)


def range_sum_with_cache(array, left, right):
    key = (left, right)
    result = cache.get(key)
    if result == -1:
        result = sum(array[left : right + 1])
        cache.put(key, result)
    return result


def update_with_cache(array, index, value):
    array[index] = value
    cache.invalidate(index)


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
        else:
            _, i, val = query
            update_no_cache(array, i, val)


def process_queries_with_cache(array, queries):
    for query in queries:
        if query[0] == "Range":
            _, l, r = query
            range_sum_with_cache(array, l, r)
        else:
            _, i, val = query
            update_with_cache(array, i, val)


if __name__ == "__main__":
    n = 100_000
    q = 50_000
    array = [random.randint(1, 100) for _ in range(n)]
    queries = make_queries(n, q)

    arr_copy = array.copy()
    t1 = time.time()
    process_queries_no_cache(arr_copy, queries)
    t_no_cache = time.time() - t1

    arr_copy = array.copy()
    t2 = time.time()
    process_queries_with_cache(arr_copy, queries)
    t_with_cache = time.time() - t2

    print(f"Без кешу : {t_no_cache:.2f} c")
    print(
        f"LRU-кеш  : {t_with_cache:.2f} c  (прискорення ×{t_no_cache / t_with_cache:.2f})"
    )
