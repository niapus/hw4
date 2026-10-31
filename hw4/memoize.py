import time


def memoize(func):
    cache = {}

    def get_cached_result(*args, **kwargs):
        cache_key = (args, tuple(sorted(kwargs.items())))
        try:
            if cache_key in cache:
                get_cached_result.hits += 1
                return cache[cache_key]
            
            result = func(*args, **kwargs)
            cache[cache_key] = result
            get_cached_result.misses += 1
            return result
        except TypeError:
            return func(*args, **kwargs)

    get_cached_result.hits = 0
    get_cached_result.misses = 0

    def cache_clear():
        cache.clear()
        get_cached_result.hits = 0
        get_cached_result.misses = 0

    get_cached_result.cache_clear = cache_clear

    get_cached_result.__name__ = func.__name__
    get_cached_result.__doc__ = func.__doc__
    
    return get_cached_result


if __name__ == '__main__':
    calls = []

    def slow_square(x, power=2):
        '''Возводит в степень.'''
        calls.append(x)
        return x ** power

    sq = memoize(slow_square)
    assert sq(3) == 9 and sq(3) == 9 and sq(3, power=3) == 27
    assert calls == [3, 3]
    assert (sq.hits, sq.misses) == (1, 2)
    assert sq.__name__ == 'slow_square' and sq.__doc__ == 'Возводит в степень.'
    total = memoize(sum)
    assert total([1, 2, 3]) == 6 and total([1, 2, 3]) == 6   # нехешируемый аргумент: вызов без кэша
    assert (total.hits, total.misses) == (0, 0)
    sq.cache_clear()
    assert (sq.hits, sq.misses) == (0, 0)
    sq(3)
    assert calls[-1] == 3

    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)
    
    fast_fib = memoize(fib)

    t0 = time.perf_counter()
    print("Вариант A. Результат:", fast_fib(30))
    tA = time.perf_counter() - t0
    print("Вариант A. misses:", fast_fib.misses, " time:", round(tA, 4), "s")


    fib = memoize(fib)

    t0 = time.perf_counter()
    print("Вариант B. Результат", fib(30))
    tB = time.perf_counter() - t0
    print("Вариант B. misses:", fib.misses, " time:", round(tB, 4), "s")

    """
    Вариант A. Результат: 832040
    Вариант A. misses: 1  time: 0.1388 s
    Вариант B. Результат 832040
    Вариант B. misses: 31  time: 0.0001 s

    fib находит в Global. В варианте A кеш создаётся в memoize, но fib рекурсивно вызывает свою исходную версию, для которой этого ещё не происходило.
    А в варианте B fib обновляется, поэтому уже посчитанные значения кешированы, что уменьшает нужное время в 1000 раз.
    """
    