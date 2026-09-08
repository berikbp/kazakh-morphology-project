"""Tests for the morphology analyzer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kazakh_morphology.morphology.analyzer import (
    AnalysisResult,
    analyze_continuation,
    analyze_word,
    check_vowel_harmony,
)


def test_analyze_known_nouns():
    for word in ["бала", "үй", "көз", "дос", "ақша", "қала"]:
        result = analyze_word(word)
        assert result.status == AnalysisResult.LEGAL, f"{word} should be LEGAL, got {result}"


def test_analyze_loanwords():
    for word in ["кітап", "телефон", "компьютер"]:
        result = analyze_word(word)
        assert result.status == AnalysisResult.UNKNOWN, f"{word} should be UNKNOWN (loanword), got {result}"


def test_analyze_unknown_words():
    for word in ["xxxxx", "zzzzz", "йййй"]:
        result = analyze_word(word)
        assert result.status in (AnalysisResult.ILLEGAL, AnalysisResult.UNKNOWN), f"{word} should not be LEGAL"


def test_vowel_harmony_legal():
    assert check_vowel_harmony("бала").status == AnalysisResult.LEGAL
    assert check_vowel_harmony("көше").status == AnalysisResult.LEGAL
    assert check_vowel_harmony("үй").status == AnalysisResult.LEGAL


def test_analyze_continuation():
    result = analyze_continuation("бала", "лар")
    assert result.status == AnalysisResult.LEGAL

    result = analyze_continuation("көше", "лер")
    assert result.status == AnalysisResult.LEGAL
