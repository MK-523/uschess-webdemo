#!/usr/bin/env python3
"""
matches a user query to the most similar articles, uses basic TF vectors

How to use:
    python3 recommender.py "i want endgame practice"
"""

import json
import math
import os
import sys
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(__file__)
ARTICLES_FILE = os.path.join(ROOT, "articles.json")

def tokenize(text):
    #tokenizer
    text = text.lower()
    tokens = re.findall(r"[a-z0-9]+", text)
    return tokens

def build_vocab(documents):
    vocab = {}
    idx = 0
    for doc in documents:
        for tok in set(doc):
            if tok not in vocab:
                vocab[tok] = idx
                idx += 1
    return vocab

def tf_vector(tokens, vocab):
    vec = [0] * len(vocab)
    counts = Counter(tokens)
    for t, c in counts.items():
        if t in vocab:
            vec[vocab[t]] = c
    return vec

def cosine(a, b):
    #cosine similarity between lists
    num = sum(x*y for x,y in zip(a,b))
    suma = math.sqrt(sum(x*x for x in a))
    sumb = math.sqrt(sum(y*y for y in b))
    if suma == 0 or sumb == 0:
        return 0.0
    return num / (suma * sumb)

def load_articles():
    with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def prepare_corpus(articles):
    docs = []
    for a in articles:
        text = (a.get("title","") + " " + a.get("summary","") + " " + a.get("content","")).strip()
        docs.append(tokenize(text))
    return docs

def recommend(query, top_k=3):
    articles = load_articles()
    corpus = prepare_corpus(articles)
    vocab = build_vocab(corpus + [tokenize(query)])
    vecs = [tf_vector(doc, vocab) for doc in corpus]
    qvec = tf_vector(tokenize(query), vocab)
    scores = []
    for idx, v in enumerate(vecs):
        sc = cosine(qvec, v)
        scores.append((sc, idx))
    scores.sort(reverse=True, key=lambda x: x[0])
    results = []
    for sc, idx in scores[:top_k]:
        art = articles[idx].copy()
        art["score"] = round(float(sc), 4)
        results.append(art)
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 recommender.py \"your query here\"")
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    results = recommend(query, top_k=5)
    print(f"Query: {query}\nTop matches:")
    for r in results:
        print(f"- [{r['score']}] {r['title']} ({r['category']}) -- {r['summary']}")

if __name__ == "__main__":
    main()
