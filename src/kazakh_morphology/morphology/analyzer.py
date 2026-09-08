"""Kazakh morphology analyzer — checks legality of word forms."""

from enum import Enum
from typing import Any, NamedTuple

from kazakh_morphology.morphology.vowel_harmony import (
    BACK_VOWELS,
    FRONT_VOWELS,
    get_vowel_harmony_class,
    select_ablative_suffix,
    select_accusative_suffix,
    select_dative_suffix,
    select_genitive_suffix,
    select_instrumental_suffix,
    select_locative_suffix,
    select_plural_suffix,
)


class AnalysisResult(Enum):
    LEGAL = "legal"
    ILLEGAL = "illegal"
    UNKNOWN = "unknown"


class MorphAnalysis(NamedTuple):
    status: AnalysisResult
    reason: str = ""
    details: dict[str, Any] = {}  # noqa: RUF012


KNOWN_NOUNS = {
    "бала", "үй", "көз", "дос", "ақша", "кітап", "қала", "көше",
    "ауыл", "қыз", "тас", "қол", "аяқ", "құлақ", "ана", "әке",
    "мектеп", "су", "нан", "ет", "сүт", "жер", "күн", "түн",
    "ӛз", "ӛлең",
}

KNOWN_LOANWORDS = {
    "кітап", "телефон", "компьютер", "университет", "кабинет",
    "машина", "автомобиль", "аэроорт", "стадион", "музей",
    "театр", "кино", "радио", "телевизор", "интернет",
    "банк", "қонақүй", "аурухана", "дәретхана",
}

KNOWN_VERBS = {
    "бару", "келу", "жазу", "оқу", "айту", "жеу", "көру", "білу",
    "тұру", "отыру", "жуу", "сию", "сүю",
}

PLURAL_SUFFIXES = {"лар", "лер", "дар", "дер", "тар", "тер"}
CASE_SUFFIXES = {
    "ның", "нің", "дың", "дің", "тың", "тің",
    "ға", "ге", "қа", "ке",
    "ны", "ні", "ды", "ді", "ты", "ті",
    "да", "де", "та", "те",
    "дан", "ден", "тан", "тен",
    "мен", "пен",
}

POSSESSIVE_SUFFIXES = {
    "ым", "ім", "дың", "дің", "тың", "тің",
    "ы", "і", "сы", "сі",
    "мыз", "міз", "сыз", "сіз",
}


def check_vowel_harmony(word: str) -> MorphAnalysis:
    h_class = get_vowel_harmony_class(word)
    if h_class.value == "mixed":
        return MorphAnalysis(
            status=AnalysisResult.ILLEGAL,
            reason="vowel_harmony_violation",
            details={"harmony_class": h_class.value},
        )
    return MorphAnalysis(status=AnalysisResult.LEGAL, details={"harmony_class": h_class.value})


def check_plural_formation(word: str, suffix: str) -> MorphAnalysis:
    if suffix not in PLURAL_SUFFIXES:
        return MorphAnalysis(status=AnalysisResult.UNKNOWN, reason="not_recognized_plural")

    expected = select_plural_suffix(word)
    if suffix != expected:
        return MorphAnalysis(
            status=AnalysisResult.ILLEGAL,
            reason="wrong_plural_allomorph",
            details={"expected": expected, "found": suffix},
        )
    return MorphAnalysis(status=AnalysisResult.LEGAL)


def check_case_suffix(word: str, case_type: str) -> MorphAnalysis:
    suffix_map = {
        "genitive": select_genitive_suffix,
        "dative": select_dative_suffix,
        "accusative": select_accusative_suffix,
        "locative": select_locative_suffix,
        "ablative": select_ablative_suffix,
        "instrumental": select_instrumental_suffix,
    }

    if case_type not in suffix_map:
        return MorphAnalysis(status=AnalysisResult.UNKNOWN, reason="unknown_case_type")

    expected = suffix_map[case_type](word)
    return MorphAnalysis(
        status=AnalysisResult.LEGAL,
        details={"expected_suffix": expected, "case_type": case_type},
    )


def analyze_word(word: str) -> MorphAnalysis:
    word = word.strip()
    if not word:
        return MorphAnalysis(status=AnalysisResult.UNKNOWN, reason="empty_word")

    if word.lower() in KNOWN_LOANWORDS:
        return MorphAnalysis(status=AnalysisResult.UNKNOWN, reason="loanword")

    all_chars = set(word.lower())
    if not all_chars.intersection(BACK_VOWELS | FRONT_VOWELS):
        return MorphAnalysis(status=AnalysisResult.UNKNOWN, reason="no_vowels_found")

    h_result = check_vowel_harmony(word)
    if h_result.status == AnalysisResult.ILLEGAL:
        return h_result

    return MorphAnalysis(status=AnalysisResult.LEGAL, details={"harmony_class": h_result.details.get("harmony_class")})


def analyze_continuation(partial_word: str, next_token_text: str) -> MorphAnalysis:
    candidate = partial_word + next_token_text
    return analyze_word(candidate)
