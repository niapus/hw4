class MyDict:
    def __init__(self, size=8):
        self._buckets = [[] for _ in range(size)]
        self._len = 0

    def _get_bucket_index(self, key):
        return hash(key) % len(self._buckets)

    def __len__(self):
        return self._len

    def __contains__(self, key):
        index = self._get_bucket_index(key)
        for k, v in self._buckets[index]:
            if k == key:
                return True
        return False

    def __getitem__(self, key):
        index = self._get_bucket_index(key)
        for k, value in self._buckets[index]:
            if k == key:
                return value
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        if self._len >= (len(self._buckets) * 2) / 3:
            buckets = self._buckets
            new_size = len(self._buckets) * 2
            self._buckets = [[] for _ in range(new_size)]
            for bucket in buckets:
                for k, v in bucket:
                    index = hash(k) % new_size
                    self._buckets[index].append((k, v))
        index = self._get_bucket_index(key)
        bucket = self._buckets[index]
        for i in range(len(bucket)):
            k, v = bucket[i]
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._len += 1

    def __delitem__(self, key):
        index = self._get_bucket_index(key)
        bucket = self._buckets[index]
        for k, v in bucket:
            if k == key:
                bucket.remove((k, v))
                self._len -= 1
                return  
        raise KeyError(key)

    def stats(self):
        longest = max(len(bucket) for bucket in self._buckets) if self._buckets else 0
        return (len(self._buckets), self._len, longest)

    def __repr__(self):
        pairs = []
        for bucket in self._buckets:
            for k, v in bucket:
                pairs.append(f"{repr(k)}: {repr(v)}")
        return f"MyDict({{{', '.join(pairs)}}})"


if __name__ == '__main__':
    d = MyDict()
    for i in range(1000):
        d[f'key{i}'] = i
    assert len(d) == 1000
    assert d['key42'] == 42
    assert 'key7' in d and 'nope' not in d
    d['key42'] = -1
    assert d['key42'] == -1 and len(d) == 1000
    del d['key42']
    assert 'key42' not in d and len(d) == 999
    assert d.get('nope') is None and d.get('nope', 0) == 0
    for bad in (lambda: d['nope'], lambda: d.__delitem__('nope')):
        try:
            bad()
            assert False, 'ожидали KeyError'
        except KeyError:
            pass
    buckets, size, longest = d.stats()
    assert size == 999 and size <= buckets * 2 / 3
    print(d.stats())

    # дополнительные проверки
    d_extra = MyDict(size=8)
    for i in range(5):
        d_extra[i] = i
    
    buckets_len, _, _ = d_extra.stats()
    assert buckets_len == 8

    d_empty = MyDict()
    d_empty["empty"] = 1
    del d_empty["empty"]
    assert len(d_empty) == 0
    assert "empty" not in d_empty

    d_none = MyDict()
    d_none[None] = None
    assert None in d_none
    assert d_none[None] is None
    assert len(d_none) == 1

    d_same = MyDict()
    for k in range(100):
        d_same["same_key"] = 0
    assert len(d_same) == 1
    
    """ 
    Ответы на вопросы:
    1. Почему при увеличении таблицы пары нельзя просто скопировать в корзины с теми же номерами?
    Номер корзины зависит от размера таблицы len(self._buckets)
    
    2. Что показывает stats() для 1000 строковых ключей и что он покажет, если ключами будут объекты, у которых __hash__ всегда возвращает 42? Проверьте экспериментом, замерьте время вставки 1000 таких ключей.
    (2048, 1000, 4). Для 1000 ключей с одинаковым hash — (2048, 1000, 1000). Время выполнения 0.11 против 0.002 секунд
    """
