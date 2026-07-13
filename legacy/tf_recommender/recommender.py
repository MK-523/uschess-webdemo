#!/usr/bin/env python3
"""Historical term-frequency recommendation baseline from the first demo."""

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path


ARTICLES_FILE = Path(__file__).with_name("articles.json")


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def build_vocab(documents):
    vocab = {}
    for document in documents:
        for token in set(document):
            if token not in vocab:
                vocab[token] = len(vocab)
    return vocab


def tf_vector(tokens, vocab):
    vector = [0] * len(vocab)
    for token, count in Counter(tokens).items():
        if token in vocab:
            vector[vocab[token]] = count
    return vector


def cosine(left, right):
    numerator = sum(a * b for a, b in zip(left, right))
    left_size = math.sqrt(sum(value * value for value in left))
    right_size = math.sqrt(sum(value * value for value in right))
    if left_size == 0 or right_size == 0:
        return 0.0
    return numerator / (left_size * right_size)


def recommend(query, top_k=3):
    articles = json.loads(ARTICLES_FILE.read_text(encoding="utf-8"))
    documents = [
        tokenize(
            f"{article.get('title', '')} {article.get('summary', '')} "
            f"{article.get('content', '')}"
        )
        for article in articles
    ]
    vocabulary = build_vocab([*documents, tokenize(query)])
    query_vector = tf_vector(tokenize(query), vocabulary)
    scored = [
        (cosine(query_vector, tf_vector(document, vocabulary)), index)
        for index, document in enumerate(documents)
    ]
    scored.sort(reverse=True)
    results = []
    for score, index in scored[:top_k]:
        result = articles[index].copy()
        result["score"] = round(score, 4)
        results.append(result)
    return results


def main():
    if len(sys.argv) < 2:
        raise SystemExit('Usage: recommender.py "your query"')
    query = " ".join(sys.argv[1:])
    for result in recommend(query, top_k=5):
        print(f"[{result['score']}] {result['title']} — {result['summary']}")


if __name__ == "__main__":
    main()

