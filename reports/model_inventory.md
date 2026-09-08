# Model Inventory

**Date:** 2026-09-06

## Primary Models

### Model A — Sherkala 8B Chat

- **Repository:** inceptionai/Llama-3.1-Sherkala-8B-Chat
- **Base architecture:** Llama 3.1
- **Parameter count:** 8B
- **Primary languages:** Kazakh, English
- **Kazakh-specific:** Yes
- **Tokenizer:** Llama 3.1 tokenizer
- **Native dtype:** bfloat16
- **Chosen inference dtype:** bfloat16
- **Quantization:** 4-bit NF4 (bitsandbytes)
- **Backend:** transformers
- **Approx model weight memory:** ~4.5 GB (4-bit)
- **GPU-only possible?** Yes (with 4-bit quantization)
- **CPU offload required?** No (4-bit fits in 8 GB VRAM)
- **License/access restrictions:** Access gated on HuggingFace
- **Successfully loaded?** Pending
- **Peak VRAM:** Pending
- **Tokens/second:** Pending
- **Notes:** Main Kazakh-focused model. Must test in 4-bit for 8 GB VRAM.

### Model B — ISSAI KazLLM 8B

- **Repository:** issai/LLama-3.1-KazLLM-1.0-8B
- **GGUF repository:** issai/LLama-3.1-KazLLM-1.0-8B-GGUF4
- **Base architecture:** Llama 3.1
- **Parameter count:** 8B
- **Primary languages:** Kazakh, English
- **Kazakh-specific:** Yes
- **Tokenizer:** Llama 3.1 tokenizer
- **Native dtype:** bfloat16
- **Chosen inference dtype:** bfloat16
- **Quantization:** 4-bit (bitsandbytes NF4 or GGUF Q4_K_M)
- **Backend:** transformers (bitsandbytes)
- **Approx model weight memory:** ~4.5 GB (4-bit)
- **GPU-only possible?** Yes (with 4-bit quantization)
- **CPU offload required?** No
- **License/access restrictions:** None apparent
- **Successfully loaded?** Pending
- **Peak VRAM:** Pending
- **Tokens/second:** Pending
- **Notes:** Kazakh-specific competitor to Sherkala. Compare architectures.

### Model C — Qwen3 8B

- **Repository:** Qwen/Qwen3-8B
- **GGUF repository:** Qwen/Qwen3-8B-GGUF
- **Base architecture:** Qwen3
- **Parameter count:** 8B
- **Primary languages:** Multilingual
- **Kazakh-specific:** No
- **Tokenizer:** Qwen3 tokenizer
- **Native dtype:** bfloat16
- **Chosen inference dtype:** bfloat16
- **Quantization:** 4-bit NF4 (bitsandbytes)
- **Backend:** transformers
- **Approx model weight memory:** ~4.5 GB (4-bit)
- **GPU-only possible?** Yes (with 4-bit quantization)
- **CPU offload required?** No
- **License/access restrictions:** Apache 2.0
- **Successfully loaded?** Yes
- **Peak VRAM:** 5876 MB
- **Tokens/second:** 5.4
- **Notes:** Strong multilingual baseline. Produces some correct Kazakh forms. Still struggles with instruction following.

### Model D — Qwen3 1.7B

- **Repository:** Qwen/Qwen3-1.7B
- **Base architecture:** Qwen3
- **Parameter count:** 1.7B
- **Primary languages:** Multilingual
- **Kazakh-specific:** No
- **Tokenizer:** Qwen3 tokenizer
- **Native dtype:** bfloat16
- **Chosen inference dtype:** bfloat16
- **Quantization:** None (BF16)
- **Backend:** transformers
- **Approx model weight memory:** ~3.4 GB (BF16)
- **GPU-only possible?** Yes
- **CPU offload required?** No
- **License/access restrictions:** Apache 2.0
- **Successfully loaded?** Yes
- **Peak VRAM:** 3335 MB
- **Tokens/second:** 7.7
- **Notes:** Too small for reliable Kazakh instruction following. Produces repetitive loops.

### Model E — SozKZ 1B Kazakh

- **Repository:** stukenov/sozkz-core-llama-1b-kk-instruct-v2
- **Base architecture:** Llama
- **Parameter count:** 1B
- **Primary languages:** Kazakh
- **Kazakh-specific:** Yes
- **Tokenizer:** Llama tokenizer
- **Native dtype:** bfloat16
- **Chosen inference dtype:** bfloat16
- **Quantization:** None (BF16)
- **Backend:** transformers
- **Approx model weight memory:** ~2 GB (BF16)
- **GPU-only possible?** Yes
- **CPU offload required?** No
- **License/access restrictions:** None apparent
- **Successfully loaded?** Pending
- **Peak VRAM:** Pending
- **Tokens/second:** Pending
- **Notes:** Small Kazakh-specific baseline. Compare against larger Kazakh models.

## Optional Models (Add Later)

| Model | Parameters | Kazakh-specific | Notes |
|---|---|---|---|
| Gemma 3 1B IT | 1B | No | Small multilingual baseline |
| Gemma 3 4B IT | 4B | No | Medium multilingual |
| Llama 3.2 3B Instruct | 3B | No | Generic baseline |
| Qwen2.5 3B Instruct | 3B | No | Unquantized medium baseline |
| TilQazyna Kazakh Llama 8B | 8B | Yes | Additional Kazakh model |

## Precision Comparison Rules

When comparing models, always record:

```
Model — precision — quantization
Example: Sherkala-8B — NF4 4-bit
         Qwen3-8B — Q4_K_M
         Qwen3-1.7B — BF16
```

Never compare without specifying precision.
