from collections import Counter
import re


class SearchIndex:
    """
    - self._index: список документов для каждого слова.
    - self._forward_index: список слов для каждого документа. Позволяет при remove() и повторном add() не перебирать весь инвертированный индекс.
    - self._word_counts (Counter): счётчик.
    """
    def __init__(self):
        self._index = {}
        self._forward_index = {}
        self._word_counts = Counter()

    def add(self, doc_id: int, text: str):
        if doc_id in self._forward_index:
            self.remove(doc_id)

        words = re.findall(r"\w+", text.lower())
        if not words:
            return

        self._forward_index[doc_id] = words
        self._word_counts.update(words)

        for word in set(words):
            if word not in self._index:
                self._index[word] = set()
            self._index[word].add(doc_id)

    def search_all(self, *words):
        if not words:
            return set()
        lower_words = [w.lower() for w in words]
        if any(w not in self._index for w in lower_words):
            return set()

        result = self._index[lower_words[0]].copy()
        for word in lower_words[1:]:
            result = result & self._index[word]
        return result

    def search_any(self, *words):
        result = set()
        for word in words:
            w_lower = word.lower()
            if w_lower in self._index:
                result.update(self._index[w_lower])
        return result

    def remove(self, doc_id: int):
        if doc_id not in self._forward_index:
            return

        words = self._forward_index[doc_id]
        del self._forward_index[doc_id]

        for word in words:
            self._word_counts[word] -= 1
            if self._word_counts[word] == 0:
                del self._word_counts[word]

        for word in set(words):
            if word in self._index:
                self._index[word].remove(doc_id)
                if len(self._index[word]) == 0:
                    del self._index[word]

    def top_words(self, n: int):
        return self._word_counts.most_common(n)


if __name__ == '__main__':
    idx = SearchIndex()
    idx.add(1, 'Python is a programming language.')
    idx.add(2, 'A dict is a hash table; a set is a hash table too!')
    idx.add(3, 'Python dict and set are fast.')
    assert idx.search_all('python') == {1, 3}
    assert idx.search_all('dict', 'set') == {2, 3}
    assert idx.search_all('python', 'hash') == set()
    assert idx.search_any('language', 'fast') == {1, 3}
    assert idx.search_all('PYTHON') == {1, 3}
    assert idx.search_all('nothing') == set()
    assert idx.top_words(2) == [('a', 5), ('is', 3)]
    idx.remove(1)
    assert idx.search_all('python') == {3}
    assert idx.search_any('language', 'programming') == set()
    idx.add(3, 'Totally new text')
    assert idx.search_all('python') == set()
    assert idx.search_all('new') == {3}
