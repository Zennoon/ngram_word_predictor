from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import defaultdict, deque
import heapq
from math import log2


class MaxNGramModela:
    def __init__(self, words: list[str], max_n: int = 4):
        if max_n < 1 or max_n > 4:
            raise ValueError(f"max_n must be a value between 1 and 4: {max_n} was given.")
        print(f"Initializing MaxNGramModel instance of max order {max_n}...")
        self.max_n = max_n
        self.ngram_counts = { i: defaultdict(int) for i in range(1, self.max_n + 1) }
        self.__build_counts(words)
        self.unigrams_total = sum(self.ngram_counts[1].values())
        del words
        print("Finished initializing MaxNGramModel instance. Model is ready to use.")

    def __build_counts(self, words: list[str]):
        window = deque(maxlen=self.max_n)
        for i in range(len(words)):
            word = words[i]
            if word == "</s>":
                window.clear()
                continue
            window.append(word)
            for j in range(1, len(window) + 1):
                ngram_tuple = tuple(list(window)[-j:])
                self.ngram_counts[j][ngram_tuple] += 1

    def get_k_most_frequent_sequences(self, n: int, k: int = 10):
        if n > self.max_n:
            print(f"n cannot be greater than {self.max_n}. Using n={self.max_n} instead.")
            n = self.max_n
        top_tuples = heapq.nlargest(k, self.ngram_counts[n], key=lambda x: self.ngram_counts[n][x])
        return [(" ".join(t), self.ngram_counts[n][t]) for t in top_tuples]

    def get_word_probability(self, word: str, n: int = 2, history: str = "", prefix=""):
        if not word:
            print("Please provide a non-empty word.")
            return None
        if n > self.max_n:
            print(f"n cannot be greater than {self.max_n}. Using n={self.max_n} instead.")
            n = self.max_n

        history_words = tuple(history.split()[-n + 1:])
        if len(history_words) < n - 1:
            print(f"For order n={n}, history must contain at least {n-1} words. {len(history_words)} words given, using n={len(history_words) + 1} instead.")
        n = len(history_words) + 1
        
        while n > 1:
            history_words = history_words[-n+1:]
            if self.ngram_counts[n-1].get(history_words, 0) == 0:
                print(f"'{" ".join(history_words)}' not found in the corpus. Trying with less words.")
                n -= 1
            else:
                break

        if n == 1:
            history_words = tuple()
        if prefix:
            valid_sequences = { t: count for t, count in self.ngram_counts[n].items() if t[:-1] == history_words and t[-1].startswith(prefix) }
            count_history = sum(valid_sequences.values())
            count_together = valid_sequences.get(history_words + (word,), 0)
        else:
            count_history = self.ngram_counts[n-1].get(history_words, 0) if n > 1 else self.unigrams_total
            count_together = self.ngram_counts[n].get(history_words + (word,), 0)
        if count_history == 0:
            return 0.0
        return count_together / count_history

    def get_k_most_probable_words(self, n: int = 1, history: str = "", prefix: str = "", k: int = 10):
        if n > self.max_n:
            print(f"n cannot be greater than {self.max_n}. Using n={self.max_n} instead.")
            n = self.max_n
        history_words = tuple(history.split()[-n+1:])
        if len(history_words) < n - 1:
            print(f"For order n={n}, history must contain at least {n - 1} words. {len(history_words)} words given, using n={len(history_words) + 1} instead.")
            n = len(history_words) + 1
        
        while n > 1:
            history_words = history_words[-n+1:]
            if self.ngram_counts[n-1].get(history_words, 0) == 0:
                print(f"'{" ".join(history_words)}' not found in the corpus. Trying with less words.")
                n -= 1
            else:
                break
        if n == 1:
            history_words = tuple()
        valid_sequences = { t: count for t, count in self.ngram_counts[n].items() if t[:-1] == history_words and t[-1].startswith(prefix) }
        count_history = sum(valid_sequences.values())
        if count_history == 0:
            return []
        top_tuples = heapq.nlargest(k, valid_sequences, key=lambda x: valid_sequences[x])
        return [(t[-1], valid_sequences[t] / count_history) for t in top_tuples]        

    def draw_wordcloud(self, n: int = 1, title: str = ""):
        if n > self.max_n:
            print(f"n cannot be greater than {self.max_n}. Using n={self.max_n} instead.")
            n = self.max_n
        freq_dict = { " ".join(t): count for t, count in self.ngram_counts[n].items() }

        wc = WordCloud(
            width=800,
            height=400,
            background_color="white",
            font_path="/kaggle/input/datasets/yunuskedir/hiburmono-font/HiburMono-Regular.ttf"
        ).generate_from_frequencies(freq_dict)

        plt.figure(figsize=(12, 6))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(title if title else f"Word Cloud for NGram of order {n}")
        plt.show()

    def calculate_perplexity(self, n: int, test_data: list[str]):
        log_prob_sum = 0
        count = 0
        for i in range(n - 1, len(test_data)):
            sequence = test_data[i-n+1:i+1]
            if "</s>" in sequence:
                i += sequence.index("</s>")
                continue
            if n == 1 or self.ngram_counts[n-1][tuple(sequence[:-1])]:
                history = " ".join(sequence[:-1])
                prob = self.get_word_probability(sequence[-1], n, history)
                if prob > 0:
                    log_prob_sum += log2(prob)
                count += 1
        return 2 ** (-1 * (log_prob_sum / count))

    def calculate_accuracy(self, n: int, test_data: list[str]):
        count = 0
        correct_count = 0
        for i in range(n-1, len(test_data)):
            sequence = test_data[i-n+1:i+1]
            if "</s>" in sequence:
                i += sequence.index("</s>")
                continue
            context = " ".join(sequence[:-1])
            correct_word = sequence[-1]
            top_10_predictions = self.get_k_most_probable_words(n, history=context)
            top_10_words = list(map(lambda t: t[0], top_10_predictions))
            if correct_word in top_10_words:
                correct_count += (10 - top_10_words.index(correct_word)) / 10
            count += 1
        return (correct_count/(count if count else 1)) * 100
