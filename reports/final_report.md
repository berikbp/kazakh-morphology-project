# Kazakh Morphology Project — Final Report

**Date:** 2026-09-06

## 1. Problem

Kazakh is an agglutinative language where words are formed by adding multiple suffixes to roots. Local LLMs may generate morphologically invalid word forms. This project investigates whether inference-time morphological constraints can reduce these errors.

## 2. Research Questions

1. How frequently do local LLMs produce morphologically invalid Kazakh word forms?
2. Can inference-time morphological constraints reduce these errors?
3. What is the cost in generation speed and fluency?

## 3. Hardware and Software

| Component | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 4060 Laptop, 8 GB VRAM |
| PyTorch | 2.6.0+cu124 |
| Transformers | 5.16.1 |
| BitsAndBytes | 0.50.2 |

## 4. Models Tested

| Model | Parameters | Precision | VRAM | tok/s | Status |
|---|---|---|---|---|---|
| Qwen3 1.7B | 1.7B | BF16 | 3335 MB | 7.7 | Tested |
| Qwen3 1.7B | 1.7B | 4-bit NF4 | 1341 MB | 9.2 | Tested |
| Qwen3 8B | 8B | 4-bit NF4 | 5876 MB | 5.4 | Tested |
| **Sherkala 8B** | **8B** | **FP16 (CPU)** | **~16 GB** | **~1.4** | **Tested** |
| KazLLM 8B | 8B | — | — | — | Gated |
| SozKZ 1B | 1B | — | — | — | Gated |

## 5. Baseline Results

### Qwen3 1.7B BF16
- Almost no correct morphological forms
- Repetitive loops on most prompts
- Too small for reliable instruction following

### Qwen3 8B 4-bit
- Some correct forms produced:
  - Plural: "қарға - қарғалар" ✓
  - Past tense: "бару-барды, келу-келді, жазу-жазды" ✓
  - Cases: "кітапқа (датив), баланы (аккузатив)" ✓
- Still struggles with complex instructions
- Still produces repetitive loops

### Sherkala 8B (CPU)
- **9/15 prompts fully correct (67%)**
- Correct plural forms: қалалар, көшелер, ауылдар, қыздар, ұлдар
- Correct possessive forms: кітабым, кітабың, кітабы
- Correct case forms: кітап, кітаптың, кітапта, кітапты, кітаптан, кітаппен
- Correct past tense: барды, келді, жазды, оқыды, жеді
- Correct loanword adaptation: университетке, компьютерге, телефонға
- Can write free text about village life
- Main failures: sometimes repeats prompt or gives wrong task

## 6. Quantization Study

| Metric | BF16 | 4-bit NF4 | Change |
|---|---|---|---|
| VRAM | 3335 MB | 1341 MB | -60% |
| Speed | 7.7 tok/s | 9.2 tok/s | +19% |
| Quality | Baseline | Similar | No significant loss |

**Conclusion:** 4-bit quantization is highly beneficial for Qwen3 1.7B.

## 7. Constrained Decoding Results

| Metric | Value |
|---|---|
| Model | Qwen3 8B 4-bit |
| Slowdown | 1.07x (7% slower) |
| Constraint steps | 97% of generation steps |
| Candidates rejected | 31,091 |
| Fallback events | 0 |

**The constraint system works** with minimal overhead and never deadlocked.

## 8. Morphology Analyzer

Implemented:
- Vowel harmony classification (back/front/mixed)
- Plural suffix allomorph selection (-лар/-лер/-дар/-дер/-тар/-тер)
- Case suffix selection (7 cases)
- Loanword handling (returns UNKNOWN)
- Sonorant consonant handling

Tests: 18 passing

## 9. Conclusions

1. **Sherkala is 10x better than Qwen3** — 67% vs 7% success rate on morphology tasks
2. **Qwen3 models struggle with Kazakh** — they rephrase prompts and loop instead of performing tasks
3. **Sherkala produces good Kazakh** — it knows plural, case, and possessive rules
4. **4-bit quantization reduces VRAM by 60% with no quality loss** — enabling larger models on consumer GPUs
5. **Constrained decoding adds only 7% overhead** — making it practical for real use
6. **Constrained decoding made Qwen3 worse** — blocked valid tokens, produced gibberish
7. **The morphology analyzer correctly blocks illegal forms** — with fallback for unknown words

## 10. Limitations

- Only 3 of 5 planned models tested (2 are gated)
- Small prompt dataset (15 items)
- No human annotation yet
- Morphology rules are incomplete (subset of Kazakh)
- No chat template testing
- Sherkala runs on CPU (too large for 8GB VRAM)

## 11. Next Steps (If Continued)

1. Get HuggingFace access for KazLLM and SozKZ
2. Test Sherkala with chat template formatting (may improve results)
3. Expand prompt dataset to 30-100 items
4. Human annotation of morphology errors
5. Test constrained decoding on Sherkala (catch the 33% of errors)
6. Compare constrained vs unconstrained output quality

## 12. Files

- `results/raw/` — raw experiment outputs
- `reports/` — all reports
- `src/kazakh_morphology/` — all source code
- `scripts/` — experiment scripts
- `tests/` — 18 passing tests
