"""Tests for vowel harmony and plural suffix selection."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kazakh_morphology.morphology.analyzer import AnalysisResult, analyze_word
from kazakh_morphology.morphology.vowel_harmony import (
    HarmonyClass,
    classify_vowel,
    get_last_vowel,
    get_vowel_harmony_class,
    select_dative_suffix,
    select_plural_suffix,
)


def test_classify_vowel_back():
    assert classify_vowel("а") == HarmonyClass.BACK
    assert classify_vowel("о") == HarmonyClass.BACK
    assert classify_vowel("ұ") == HarmonyClass.BACK
    assert classify_vowel("ы") == HarmonyClass.BACK
    assert classify_vowel("э") == HarmonyClass.BACK


def test_classify_vowel_front():
    assert classify_vowel("е") == HarmonyClass.FRONT
    assert classify_vowel("и") == HarmonyClass.FRONT
    assert classify_vowel("і") == HarmonyClass.FRONT
    assert classify_vowel("ө") == HarmonyClass.FRONT
    assert classify_vowel("ү") == HarmonyClass.FRONT


def test_vowel_harmony_back_word():
    assert get_vowel_harmony_class("бала") == HarmonyClass.BACK
    assert get_vowel_harmony_class("қала") == HarmonyClass.BACK
    assert get_vowel_harmony_class("ауыл") == HarmonyClass.BACK


def test_vowel_harmony_front_word():
    assert get_vowel_harmony_class("көше") == HarmonyClass.FRONT
    assert get_vowel_harmony_class("үй") == HarmonyClass.FRONT
    assert get_vowel_harmony_class("көз") == HarmonyClass.FRONT


def test_get_last_vowel():
    assert get_last_vowel("бала") == "а"
    assert get_last_vowel("көше") == "е"
    assert get_last_vowel("дос") == "о"
    assert get_last_vowel("xyz") is None


def test_plural_suffix():
    assert select_plural_suffix("бала") == "лар"
    assert select_plural_suffix("көше") == "лер"
    assert select_plural_suffix("үй") == "лер"
    assert select_plural_suffix("дос") == "дар"
    assert select_plural_suffix("тас") == "дар"
    assert select_plural_suffix("қол") == "лар"


def test_dative_suffix():
    assert select_dative_suffix("бала") == "ға"
    assert select_dative_suffix("көше") == "ге"
    assert select_dative_suffix("дос") == "қа"
    assert select_dative_suffix("үй") == "ге"


def test_analyze_word_legal():
    assert analyze_word("бала").status == AnalysisResult.LEGAL
    assert analyze_word("көше").status == AnalysisResult.LEGAL
    assert analyze_word("дос").status == AnalysisResult.LEGAL
    assert analyze_word("үй").status == AnalysisResult.LEGAL


def test_analyze_word_empty():
    assert analyze_word("").status == AnalysisResult.UNKNOWN
    assert analyze_word("   ").status == AnalysisResult.UNKNOWN
