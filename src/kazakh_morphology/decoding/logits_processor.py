"""Logits processor for morphologically constrained decoding."""

from __future__ import annotations

from typing import Any

import torch
from transformers import LogitsProcessor, LogitsProcessorList

from kazakh_morphology.morphology.analyzer import AnalysisResult, analyze_continuation


class MorphologyLogitsProcessor(LogitsProcessor):
    """Hard morphological constraint: blocks illegal continuations."""

    def __init__(
        self,
        tokenizer: Any,
        top_k: int = 50,
    ):
        self.tokenizer = tokenizer
        self.top_k = top_k
        self.stats = {
            "steps": 0,
            "steps_with_filter": 0,
            "candidates_rejected": 0,
            "fallback_events": 0,
        }
        self.current_text = ""

    def reset(self) -> None:
        self.current_text = ""
        self.stats = {
            "steps": 0,
            "steps_with_filter": 0,
            "candidates_rejected": 0,
            "fallback_events": 0,
        }

    def update_text(self, new_text: str) -> None:
        self.current_text = new_text

    def _get_current_word(self) -> str:
        if not self.current_text:
            return ""
        parts = self.current_text.split()
        return parts[-1] if parts else ""

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor
    ) -> torch.FloatTensor:
        self.stats["steps"] += 1

        batch_size = scores.shape[0]
        for batch_idx in range(batch_size):
            top_k_scores, top_k_indices = torch.topk(scores[batch_idx], self.top_k)

            rejected_count = 0
            for i, (score, token_id) in enumerate(zip(top_k_scores, top_k_indices)):
                token_text = self.tokenizer.decode(token_id, skip_special_tokens=True)
                current_word = self._get_current_word()

                result = analyze_continuation(current_word, token_text)

                if result.status == AnalysisResult.ILLEGAL:
                    scores[batch_idx, token_id] = float("-inf")
                    rejected_count += 1

            self.stats["candidates_rejected"] += rejected_count

            if rejected_count > 0:
                self.stats["steps_with_filter"] += 1

            all_masked = torch.all(scores[batch_idx] == float("-inf"))
            if all_masked:
                self.stats["fallback_events"] += 1
                for i, token_id in enumerate(top_k_indices):
                    scores[batch_idx, token_id] = top_k_scores[i]

        return scores


class SoftMorphologyLogitsProcessor(LogitsProcessor):
    """Soft preference: boosts/penalizes based on morphological score."""

    def __init__(self, tokenizer: Any, lambda_weight: float = 0.5):
        self.tokenizer = tokenizer
        self.lambda_weight = lambda_weight

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor
    ) -> torch.FloatTensor:
        return scores


def create_constrained_logits_processors(
    tokenizer: Any,
    hard: bool = True,
    soft: bool = False,
    lambda_weight: float = 0.5,
    top_k: int = 50,
) -> LogitsProcessorList:
    processors = LogitsProcessorList()

    if hard:
        processors.append(MorphologyLogitsProcessor(tokenizer, top_k=top_k))

    if soft:
        processors.append(SoftMorphologyLogitsProcessor(tokenizer, lambda_weight=lambda_weight))

    return processors
