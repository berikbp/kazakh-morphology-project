"""Tests for constrained decoding."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kazakh_morphology.decoding.logits_processor import MorphologyLogitsProcessor
from kazakh_morphology.morphology.analyzer import AnalysisResult, analyze_continuation


def test_analyze_continuation_legal():
    result = analyze_continuation("бала", "лар")
    assert result.status == AnalysisResult.LEGAL


def test_analyze_continuation_unknown():
    result = analyze_continuation("бала", "xyz")
    assert result.status in (AnalysisResult.LEGAL, AnalysisResult.UNKNOWN)


def test_morphology_processor_initialization():
    class MockTokenizer:
        def decode(self, token_id, skip_special_tokens=True):
            return "а"

    processor = MorphologyLogitsProcessor(MockTokenizer(), top_k=10)
    assert processor.stats["steps"] == 0
    assert processor.stats["candidates_rejected"] == 0


def test_morphology_processor_reset():
    class MockTokenizer:
        def decode(self, token_id, skip_special_tokens=True):
            return "а"

    processor = MorphologyLogitsProcessor(MockTokenizer(), top_k=10)
    processor.stats["steps"] = 5
    processor.reset()
    assert processor.stats["steps"] == 0
