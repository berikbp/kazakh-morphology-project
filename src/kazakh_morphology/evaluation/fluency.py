"""Fluency evaluation utilities for Kazakh text generation."""

from __future__ import annotations


def count_repetitions(text: str, ngram_size: int = 3) -> float:
    words = text.split()
    if len(words) < ngram_size:
        return 0.0

    ngrams = []
    for i in range(len(words) - ngram_size + 1):
        ngram = tuple(words[i : i + ngram_size])
        ngrams.append(ngram)

    if not ngrams:
        return 0.0

    unique_ngrams = set(ngrams)
    return 1.0 - (len(unique_ngrams) / len(ngrams))


def measure_lexical_diversity(text: str) -> float:
    words = text.split()
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def detect_code_switching(text: str) -> dict:
    kazakh_chars = set("әғқңүұіөһӘҒҚҢҮҰІӨҺ")
    latin_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    kk_count = sum(1 for c in text if c in kazakh_chars)
    lat_count = sum(1 for c in text if c in latin_chars)
    total = kk_count + lat_count

    if total == 0:
        return {"kazakh_ratio": 0.0, "latin_ratio": 0.0, "code_switches": 0}

    switches = 0
    prev_type = None
    for c in text:
        if c in kazakh_chars:
            curr_type = "kk"
        elif c in latin_chars:
            curr_type = "lat"
        else:
            continue
        if prev_type is not None and curr_type != prev_type:
            switches += 1
        prev_type = curr_type

    return {
        "kazakh_ratio": kk_count / total,
        "latin_ratio": lat_count / total,
        "code_switches": switches,
    }


def evaluate_fluency(text: str) -> dict:
    return {
        "repetition_rate": round(count_repetitions(text), 3),
        "lexical_diversity": round(measure_lexical_diversity(text), 3),
        "code_switching": detect_code_switching(text),
        "char_count": len(text),
        "word_count": len(text.split()),
    }
