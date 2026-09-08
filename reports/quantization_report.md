# Quantization Report

**Date:** 2026-09-06  
**Model:** Qwen3 1.7B  
**Comparison:** BF16 vs 4-bit NF4  
**Seed:** 42  
**Prompts:** 15 morphology tests

## Performance Comparison

| Metric | BF16 | 4-bit NF4 | Change |
|---|---|---|---|
| Peak VRAM | 3335 MB | 1341 MB | -60% |
| Tokens/sec | 7.7 | 9.2 | +19% |
| Load time | ~10s | ~13s | +30% |
| Total gen time | 388.5s | 324.3s | -17% |

## Quality Comparison

Both BF16 and 4-bit versions produce **similar quality** outputs:
- Both struggle with instruction following
- Both produce repetitive loops
- Both produce some correct morphological forms (VH_003, VH_011)
- 4-bit does NOT show significant quality degradation for this model size

## Key Finding

**4-bit quantization is highly beneficial for Qwen3 1.7B:**
- 60% VRAM reduction (3335 → 1341 MB)
- 19% faster generation
- No significant quality loss

This makes the 1.7B model viable for development/debugging on low-VRAM GPUs.

## Raw Data

- `results/raw/baseline-v1/qwen3-1.7b-bf16/seed_42.jsonl`
- `results/raw/quantization-v1/qwen3-1.7b-nf4/seed_42.jsonl`
