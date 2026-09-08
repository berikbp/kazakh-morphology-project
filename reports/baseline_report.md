# Baseline Report

**Date:** 2026-09-06

## Models Tested

| Model | Precision | VRAM | tok/s |
|---|---|---|---|
| Qwen3 1.7B | BF16 | 3335 MB | 7.7 |
| Qwen3 8B | 4-bit NF4 | 5876 MB | 5.4 |

**Not tested** (gated repos, need HuggingFace login): Sherkala 8B, KazLLM 8B, SozKZ 1B

## Key Findings

### Qwen3 1.7B BF16
- Generates repetitive loops on most prompts
- Almost no correct morphological forms
- Too small for reliable Kazakh instruction following

### Qwen3 8B 4-bit
- **Better but still struggles** with instruction following
- Produced some correct forms:
  - VH_003: "қарға - қарғалар" (correct plural with -лар)
  - VH_011: "бару-барды, келу-келді, жазу-жазды, оқу-оқыды" (correct past tense)
  - VH_006: "кітапқа (датив), баланы (аккузатив)" (partially correct cases)
- Still produces meta-questions instead of performing tasks
- Still falls into repetitive loops

### Morphology Error Observations
1. Both models rephrase prompts instead of performing requested tasks
2. When forms are produced, they tend to be correct for simple cases
3. Complex suffix chains (plural + possessive + case) are not attempted
4. The models lack Kazakh-specific training for following morphology instructions

## Comparison

| Metric | Qwen3 1.7B | Qwen3 8B |
|---|---|---|
| Correct plural forms | 0 | 1 |
| Correct past tense | 0 | 4 |
| Correct case forms | 0 | 2 (partial) |
| Instruction following | Poor | Moderate |
| Repetition rate | High | High |

## Next Steps

1. Need HuggingFace token for Sherkala/KazLLM (Kazakh-specific models)
2. Test constrained decoding on Qwen3 8B to see if it reduces errors
3. Consider chat template formatting for better instruction following

## Raw Data

- `results/raw/baseline-v1/qwen3-1.7b-bf16/seed_42.jsonl`
- `results/raw/baseline-v1/qwen3-8b-q4km/seed_42.jsonl`
