from collections import defaultdict
import heapq


class NGramModel:
    def __init__(self, words: list[str], n: int = 2):
        if n < 1:
            raise ValueError(f"n must be greater than 0. {n} was given.")
        if n > 5:
            raise ValueError(
                "To conserve system resources, please use a maximum of n = 5"
            )
        print(f"Initializing NGramModel instance of order {n}...")
        self.n = n
        if n == 1:
            self.ngram_counts = defaultdict(int)
            self.__build_counts(words)
            self.word_count = sum(self.ngram_counts.values())
        else:
            self.ngram_counts = defaultdict(lambda: defaultdict(int))
            self.__build_counts(words)

        print("Finished initializing NGramModel instance...")
        del words

    def __build_counts(self, words: list[str]):
        if self.n == 1:
            for word in words:
                if word != "</s>":
                    self.ngram_counts[word] += 1
        else:
            for i in range(self.n - 1, len(words)):
                prev_sequence = tuple(words[i - self.n + 1 : i])
                if "</s>" in prev_sequence:
                    i += prev_sequence.index("</s>")
                    continue
                self.ngram_counts[prev_sequence][(words[i],)] += 1

    def get_word_probability(self, word: str, history: str = ""):
        if not word:
            print("Please provide a non-empty word.")
            return None
        if self.n == 1:
            return self.ngram_counts.get((word,), 0) / self.word_count
        history_words = tuple(history.split()[-self.n + 1 :])
        if len(history_words) < self.n - 1:
            print(
                f"For order n={self.n}, history must contain at least {self.n - 1} words long. {len(history_words)} words were given."
            )
            return 0.0
        count_history = sum(self.ngram_counts[history_words].values())
        if count_history == 0:
            return 0.0
        count_together = self.ngram_counts[history_words][(word,)]
        return count_together / count_history

    def get_k_most_probable_words(
        self, history: str = "", prefix: str = "", k: int = 10
    ):
        if k < 1:
            print("Please provide a valid k value")
            return []
        if self.n == 1:
            valid_sequences = (
                {
                    t: count
                    for t, count in self.ngram_counts.items()
                    if t[0].startswith(prefix)
                }
                if prefix
                else self.ngram_counts
            )
            top_tuples = heapq.nlargest(
                k, valid_sequences, key=lambda x: valid_sequences[x]
            )
            return [(t[0], self.ngram_counts[t] / self.word_count) for t in top_tuples]

        history_words = tuple(history.split()[-self.n + 1 :])
        if len(history_words) < self.n - 1:
            print(
                f"For order n={self.n}, history must contain at least {self.n - 1} words. {len(history_words)} words were given."
            )
            return []
        
        valid_sequences = (
            {
                t: count
                for t, count in self.ngram_counts[history_words].items()
                if t[0].startswith(prefix)
            }
            if prefix
            else self.ngram_counts[history_words]
        )
        count_history = sum(valid_sequences.values())
        if count_history == 0:
            return []
        top_tuples = heapq.nlargest(
            k, valid_sequences, key=lambda x: valid_sequences[x]
        )
        return [
            (t[0], self.ngram_counts[history_words][t] / count_history)
            for t in top_tuples
        ]
