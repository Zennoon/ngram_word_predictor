import sys

from flask import Flask, jsonify, render_template, request

from models.ngram import NGramModel
from models.max_ngram import MaxNGramModel
from preprocessors import preprocess_corpus
from utils import get_corpus_words

app = Flask(__name__)


def create_app(max_n: int = 2):
    if max_n < 1 or max_n > 4:
        print("max_n must be between 1 and 4")
        exit()
    with open("./GPAC.txt", encoding="utf-8") as f:
        text = f.read()
    text = text[: int(len(text) / 100)]

    sanitized_corpus = preprocess_corpus(text)
    del text
    corpus_words = get_corpus_words(sanitized_corpus)
    del sanitized_corpus
    
    model = MaxNGramModel(words=corpus_words, max_n=max_n)

    @app.get("/")
    def home():
        return render_template("index.html", n=max_n)

    @app.post("/word_prob")
    def get_word_probability():
        try:
            data = request.get_json()
            word = data.get("word", "")
            history = data.get("history", "")
            history = "<s> " + history
            prefix = data.get("prefix", "")
            n = data.get("n", 4)
            result = model.get_word_probability(word, n, history, prefix)
            return jsonify({"status": "success", "data": {"probability": result}})
        except Exception as e:
            return jsonify({"status": "error", "message": e})

    @app.post("/most_prob_words")
    def get_k_most_prob_words():
        try:
            data = request.get_json()
            n = data.get("n")
            history = data.get("history", "")
            history = "<s> " + history
            prefix = data.get("prefix", "")
            k = data.get("k", 10)
            print(n, prefix)
            result = model.get_k_most_probable_words(n, history, prefix, k)
            for i in range(len(result)):
                if result[i][0] == "</s>":
                    delimiters = [
                        (delim, result[i][1]) for delim in ["፡፡", "!", "?"]
                    ]
                    result = result[:i] + delimiters + result[i + 1 :]
                    break
            print(result)
            return jsonify({"status": "success", "data": {"words": result}})
        except Exception as e:
            return jsonify({"status": "error", "message": e})

    app.run(host="0.0.0.0", debug=True)


if __name__ == "__main__":
    max_n = sys.argv[1] if len(sys.argv) >= 2 else 4
    try:
        max_n = int(max_n)
    except ValueError:
        max_n = 4
    create_app(max_n)
