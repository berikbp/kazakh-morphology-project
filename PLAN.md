# Kazakh Morphology Project — Detailed Execution Plan

> **Project focus:** Morphologically constrained decoding for Kazakh as an agglutinative language.  
> **Research principle:** **Measure first, then improve.**  
> **Primary machine:** NVIDIA GeForce RTX 4060 Laptop GPU, 8 GB VRAM.  
> **Environment/package manager:** `uv`  
> **Main language:** Python  
> **Primary inference stack:** PyTorch + Hugging Face Transformers + Accelerate + bitsandbytes  
> **Optional GGUF stack:** `llama.cpp` for selected quantized models

---

## 0. What I am trying to accomplish

The project investigates whether local language models generate **morphologically invalid Kazakh word forms**, and whether those errors can later be reduced during decoding by applying explicit morphological constraints.

The work should be done in this order:

1. Build a reproducible local environment.
2. Select and successfully run a small but meaningful set of local LLMs.
3. Build a Kazakh morphology-focused prompt/test set.
4. Establish an **unconstrained baseline**.
5. Measure and classify morphological errors.
6. Study quantized vs non-quantized inference.
7. Choose the most useful model(s) for the constrained-decoding prototype.
8. Implement the morphology-aware decoding pipeline.
9. Compare constrained vs unconstrained generation.
10. Analyze results and prepare the report/artifacts.

The project should **not** begin by implementing a complex morphology filter. First I need evidence that the baseline models actually make measurable morphology errors and I need a reproducible evaluation procedure.

---

# Master Phase Overview

| Phase | Name | Main Output |
|---|---|---|
| 0 | Repository + `uv` environment | Reproducible project skeleton |
| 1 | Hardware and environment verification | Machine/environment report |
| 2 | Model inventory and model selection | `models.md` |
| 3 | Unified model runner | One interface for inference |
| 4 | Kazakh morphology test suite | Versioned prompt dataset |
| 5 | Baseline generation | Raw outputs from all models |
| 6 | Morphology annotation and baseline evaluation | Error rates + taxonomy |
| 7 | Quantization study | Quantized vs non-quantized comparison |
| 8 | Model selection for main research | Primary model(s) selected |
| 9 | Morphological analyzer prototype | Legal/illegal/unknown checker |
| 10 | Constrained decoding prototype | Hard/soft decoding controls |
| 11 | Controlled experiments | Baseline vs constrained results |
| 12 | Analysis, reproducibility, report | Final research package |

---

# Phase 0 — Create the repository and `uv` project

## Goal

Create a clean project structure that I will use for the entire research project.

## Tasks

- [ ] Create the project directory.
- [ ] Initialize Git.
- [ ] Initialize a Python project with `uv`.
- [ ] Use one supported Python version across all experiments.
- [ ] Add dependencies through `uv`, not ad-hoc `pip install`.
- [ ] Commit `pyproject.toml` and `uv.lock`.
- [ ] Never commit downloaded model weights, Hugging Face cache, `.venv`, or large raw artifacts accidentally.

## Initial commands

```bash
mkdir kazakh-morphology
cd kazakh-morphology

git init

uv init --python 3.12
```

`uv` should manage the project environment and lockfile. Normal commands should be run through:

```bash
uv run python ...
```

rather than manually activating a virtual environment every time.

## Initial dependencies

Start with the inference/evaluation stack:

```bash
uv add torch transformers accelerate bitsandbytes safetensors sentencepiece
uv add huggingface-hub
uv add numpy pandas psutil pynvml tqdm pydantic rich
```

Development tools:

```bash
uv add --dev pytest ruff
```

Possible later dependencies should be added only when required by the morphology implementation.

Examples:

```bash
uv add regex
uv add datasets
```

Do **not** add large numbers of libraries before they are needed.

## Verify the lockfile

```bash
uv sync
uv tree
```

Commit:

```bash
git add pyproject.toml uv.lock .python-version .gitignore README.md
git commit -m "Initialize research project with uv"
```

## Suggested repository structure

```text
kazakh-morphology/
├── README.md
├── PLAN.md
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
│
├── configs/
│   ├── models.yaml
│   ├── generation.yaml
│   └── experiments/
│
├── data/
│   ├── prompts/
│   │   ├── morphology_v1.jsonl
│   │   └── morphology_v1.md
│   ├── annotations/
│   └── lexical_resources/
│
├── src/
│   └── kazakh_morphology/
│       ├── __init__.py
│       ├── inference/
│       │   ├── base.py
│       │   ├── transformers_runner.py
│       │   ├── quantization.py
│       │   └── generation.py
│       ├── morphology/
│       │   ├── analyzer.py
│       │   ├── vowel_harmony.py
│       │   ├── suffixes.py
│       │   └── fst/
│       ├── decoding/
│       │   ├── hard_constraint.py
│       │   ├── soft_constraint.py
│       │   └── logits_processor.py
│       ├── evaluation/
│       │   ├── morphology_eval.py
│       │   ├── fluency.py
│       │   └── performance.py
│       └── utils/
│
├── scripts/
│   ├── check_environment.py
│   ├── inspect_model.py
│   ├── run_single.py
│   ├── run_baseline.py
│   ├── run_experiment.py
│   └── summarize_results.py
│
├── results/
│   ├── raw/
│   ├── processed/
│   ├── metrics/
│   └── figures/
│
├── reports/
│   ├── environment.md
│   ├── model_inventory.md
│   ├── baseline_report.md
│   ├── quantization_report.md
│   └── final_report.md
│
└── tests/
    ├── test_vowel_harmony.py
    ├── test_analyzer.py
    └── test_decoding.py
```

## Definition of done

Phase 0 is complete when another person can clone the repository and run:

```bash
uv sync
uv run python -c "import torch, transformers; print('ok')"
```

without manually installing random dependencies.

---

# Phase 1 — Verify hardware and software environment

## Goal

Record exactly what machine and runtime are being used so results are reproducible.

## Known GPU

Current machine:

```text
NVIDIA GeForce RTX 4060 Laptop GPU
VRAM: 8188 MiB
Idle VRAM usage: approximately 651 MiB
Practical available VRAM: approximately 7.4 GiB
```

The desktop/Xwayland already consumes some VRAM. That is normal and should be treated as the machine's baseline.

## Tasks

- [ ] Record GPU model.
- [ ] Record total VRAM.
- [ ] Record NVIDIA driver.
- [ ] Record CUDA compatibility reported by `nvidia-smi`.
- [ ] Record total system RAM.
- [ ] Record CPU.
- [ ] Record OS/kernel.
- [ ] Record Python version.
- [ ] Record PyTorch version.
- [ ] Verify `torch.cuda.is_available()`.
- [ ] Record the actual GPU name PyTorch sees.
- [ ] Test BF16 support.
- [ ] Save everything in `reports/environment.md`.

## Commands

```bash
nvidia-smi
free -h
lscpu
uname -a
uv run python --version
```

Create:

```text
scripts/check_environment.py
```

It should print at least:

```python
import platform
import torch

print("Python:", platform.python_version())
print("PyTorch:", torch.__version__)
print("Torch CUDA runtime:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("VRAM:", torch.cuda.get_device_properties(0).total_memory)
    print("BF16 supported:", torch.cuda.is_bf16_supported())
```

Run:

```bash
uv run python scripts/check_environment.py
```

## Definition of done

I have a committed `reports/environment.md` containing enough information to reproduce and explain the hardware limits of all later experiments.

---

# Phase 2 — Build the local-model inventory

## Goal

Identify local models worth testing and classify them by:

- Kazakh-specific vs general multilingual;
- quantized vs non-quantized;
- parameter count;
- expected VRAM requirements;
- inference backend.

## Core model set

Start with **five primary models**.

### Model A — Sherkala 8B Chat

Repository:

```text
inceptionai/Llama-3.1-Sherkala-8B-Chat
```

Role:

- required Kazakh-focused model;
- main large Kazakh model;
- 8B parameters;
- too large for 8 GB VRAM in BF16 GPU-only;
- run using 4-bit bitsandbytes initially;
- optionally test BF16 with CPU offload later.

### Model B — ISSAI KazLLM 8B

Repository:

```text
issai/LLama-3.1-KazLLM-1.0-8B
```

GGUF repository:

```text
issai/LLama-3.1-KazLLM-1.0-8B-GGUF4
```

Role:

- Kazakh-specific 8B competitor;
- use Q4_K_M or another reproducibly documented quantization;
- compare against Sherkala.

### Model C — Qwen3 8B

Repository:

```text
Qwen/Qwen3-8B
```

GGUF repository:

```text
Qwen/Qwen3-8B-GGUF
```

Role:

- strong general multilingual 8B baseline;
- 4-bit quantized configuration should fit the 8 GB GPU;
- useful control against Kazakh-specialized 8B models.

### Model D — Qwen3 1.7B

Repository:

```text
Qwen/Qwen3-1.7B
```

Role:

- small multilingual model;
- run unquantized BF16;
- should comfortably fit the GPU;
- useful for controlled quantization experiments because the same model can also be quantized.

### Model E — SozKZ 1B Kazakh

Repository:

```text
stukenov/sozkz-core-llama-1b-kk-instruct-v2
```

Role:

- small Kazakh-specific baseline;
- run BF16;
- compare language specialization against parameter count.

## Optional models

Only add these after the five primary models are working:

- Gemma 3 1B IT — small multilingual BF16 baseline;
- Gemma 3 4B IT — medium multilingual model;
- Llama 3.2 3B Instruct — generic baseline;
- Qwen2.5 3B Instruct — another unquantized medium baseline;
- TilQazyna Kazakh Llama 8B — additional Kazakh model.

## Create `reports/model_inventory.md`

For each model record:

```text
Model:
Repository:
Base architecture:
Parameter count:
Primary languages:
Kazakh-specific?:
Tokenizer:
Native dtype:
Chosen inference dtype:
Quantization:
Backend:
Approx model weight memory:
GPU-only possible?:
CPU offload required?:
License/access restrictions:
Successfully loaded?:
Peak VRAM:
Tokens/second:
Notes:
```

## Important rule

Do not compare models without recording their exact precision.

For example:

```text
Sherkala-8B — NF4 4-bit
Qwen3-8B — Q4_K_M
Qwen3-1.7B — BF16
```

must not be described merely as:

```text
Sherkala vs Qwen
```

because model size and numerical representation are both changing.

## Definition of done

All five models are listed with repositories, intended precision, intended backend, and reason for inclusion.

---

# Phase 3 — Build one reproducible inference runner

## Goal

Avoid having a completely different script for each model.

Build one runner that accepts model configuration and outputs standardized JSON/JSONL results.

## Initial interface

Example:

```bash
uv run python scripts/run_single.py \
  --model qwen3-1.7b-bf16 \
  --prompt "Қазақ тілінде үш сөйлем жаз." \
  --seed 42
```

Eventually:

```bash
uv run python scripts/run_baseline.py \
  --model qwen3-1.7b-bf16 \
  --prompt-file data/prompts/morphology_v1.jsonl \
  --seed 42
```

## Every generation record must contain

```json
{
  "experiment_id": "...",
  "model_id": "...",
  "model_revision": "...",
  "backend": "transformers",
  "precision": "bf16",
  "quantization": null,
  "prompt_id": "VH_001",
  "prompt": "...",
  "seed": 42,
  "temperature": 0.0,
  "top_p": 1.0,
  "max_new_tokens": 200,
  "output": "...",
  "prompt_tokens": 0,
  "generated_tokens": 0,
  "generation_seconds": 0.0,
  "tokens_per_second": 0.0,
  "peak_vram_mb": 0,
  "timestamp": "..."
}
```

## Generation settings

For the first deterministic baseline, prefer controlled settings such as:

```text
do_sample = false
temperature = not applicable
max_new_tokens = fixed
```

Later add sampled experiments with fixed seeds.

Do not silently change decoding parameters between models.

## VRAM measurement

Before generation:

```python
torch.cuda.reset_peak_memory_stats()
```

After generation:

```python
peak = torch.cuda.max_memory_allocated() / (1024 ** 2)
```

Also record actual wall-clock generation time.

## Cleanup between models

When models are loaded sequentially:

```python
del model
del tokenizer

import gc
import torch

gc.collect()
torch.cuda.empty_cache()
torch.cuda.ipc_collect()
```

If a Python process still owns VRAM, terminate that process rather than killing Xwayland.

## Definition of done

At least one BF16 model and one 4-bit model can be run through the same experiment interface and produce standardized output files.

---

# Phase 4 — Build the Kazakh morphology benchmark/prompt set

## Goal

Create a reusable test set specifically designed to expose agglutinative and morphotactic errors.

This is not intended to be a generic Kazakh knowledge benchmark.

## Initial target

Create **15 core test items**:

- 5 direct prompts;
- 5 requests/instructions;
- 5 questions.

This safely covers the supervisor note of “5 each” while giving enough material for initial testing.

Later expand to 30–100+ items if the baseline shows useful error patterns.

## Morphological phenomena that must be covered

### A. Vowel harmony

Examples should require selection between suffix variants such as:

```text
-лар / -лер
-дар / -дер
-тар / -тер
```

The test should make the model naturally produce several inflected nouns.

### B. Plural formation

Test plural formation with roots from different phonological classes.

### C. Possessive morphology

Examples requiring forms corresponding to:

```text
my ...
your ...
his/her ...
our ...
```

### D. Case suffixes

Cover at least:

- nominative;
- genitive;
- dative;
- accusative;
- locative;
- ablative;
- instrumental.

### E. Multi-suffix chains

Test words that contain several morphemes.

Example conceptual pattern:

```text
root + plural + possessive + case
```

For example, forms structurally similar to:

```text
дос + тар + ым + мен
```

### F. Verb agreement

Generate sentences with different:

- persons;
- numbers;
- tenses;
- negation where useful.

### G. Derivational morphology

Prompts that cause the model to form a derived word rather than simply retrieve a common surface form.

### H. Loanwords and exceptions

Include words such as international/borrowed vocabulary so that the future analyzer does **not** implement the naive rule:

```text
all vowels in the word must have the same harmony class
```

Unknown or borrowed forms must not automatically be marked invalid.

### I. Free generation

Include longer natural Kazakh output.

Reason:

A model may succeed on artificial suffix exercises but fail during unconstrained text generation.

### J. Error correction

Give valid/invalid candidate forms and ask the model to reason about them.

Important:

Do not use only error-correction prompts. The main research question concerns what the model spontaneously **generates**, not only whether it can recognize an error.

## Prompt schema

Use JSONL:

```json
{
  "id": "VH_001",
  "category": "vowel_harmony",
  "type": "generation",
  "prompt_kk": "...",
  "target_phenomenon": "plural suffix harmony",
  "notes": ""
}
```

## Freeze versions

Once the first experiment starts, do not keep silently changing prompts.

Use:

```text
morphology_v1.jsonl
morphology_v2.jsonl
```

and document why each version changed.

## Definition of done

The first prompt set has at least 15 reviewed tests and covers multiple distinct Kazakh morphological phenomena.

---

# Phase 5 — Run the unconstrained baseline

## Goal

Answer the first research question:

> How often do the selected models produce morphologically incorrect Kazakh forms without any explicit morphological control?

## Important rule

**No morphology constraint is allowed in this phase.**

No:

- post-generation correction;
- suffix blacklist;
- custom logits processor;
- FST restriction;
- morphology-aware reranking.

This phase measures the model as-is.

## Models

Run at least:

1. Sherkala 8B — quantized;
2. KazLLM 8B — quantized;
3. Qwen3 8B — quantized;
4. Qwen3 1.7B — BF16;
5. SozKZ 1B — BF16.

## Suggested first pass

For debugging:

```text
15 prompts × 5 models × 1 deterministic run
= 75 generations
```

Do not immediately run huge experiments before validating the pipeline.

## Second pass

After the pipeline is stable:

```text
15+ prompts × selected models × multiple seeds
```

For sampled generation, use fixed seeds such as:

```text
42
123
2026
```

or another predefined set.

## Save raw outputs permanently

Never overwrite them.

Example:

```text
results/raw/
  baseline_v1/
    sherkala-8b-nf4/
      seed_42.jsonl
    kazllm-8b-q4km/
      seed_42.jsonl
    qwen3-8b-q4km/
      seed_42.jsonl
    qwen3-1.7b-bf16/
      seed_42.jsonl
    sozkz-1b-bf16/
      seed_42.jsonl
```

## Definition of done

All primary models have completed the exact same prompt suite and their untouched raw outputs are saved with metadata.

---

# Phase 6 — Annotate and measure morphology errors

## Goal

Turn raw generations into an actual baseline measurement.

## Main metric

Primary metric:

```text
morphologically incorrect word forms
-------------------------------------
total evaluated word forms
```

This needs a clearly written annotation protocol.

## Annotation labels

At minimum:

```text
VALID
INVALID
UNKNOWN
```

This is essential.

An unfamiliar word is **not automatically incorrect**.

Possible richer labels:

```text
VALID
INVALID_VOWEL_HARMONY
INVALID_SUFFIX_ORDER
INVALID_CASE
INVALID_POSSESSIVE
INVALID_AGREEMENT
INVALID_OTHER
UNKNOWN
FOREIGN_OR_CODE_SWITCHED
TOKENIZATION_OR_FORMATTING
```

## Annotation format

Example:

```json
{
  "model_id": "sherkala-8b-nf4",
  "prompt_id": "VH_001",
  "surface_form": "балалер",
  "label": "INVALID_VOWEL_HARMONY",
  "suggested_valid_form": "балалар",
  "annotator": "A1",
  "notes": ""
}
```

## Independent evaluation principle

The future morphology constraint must not grade itself.

If the same analyzer is used for:

1. blocking words;
2. declaring the generated result correct;

the evaluation becomes circular.

Prefer:

- native-speaker/manual annotation for the gold set;
- agreement between annotators where possible;
- automated tools only as supporting signals.

## Additional baseline metrics

Alongside morphology error rate, track:

- output length;
- fluency;
- lexical diversity;
- code-switching;
- repetition;
- generation speed;
- peak VRAM;
- failure/OOM rate.

## Error taxonomy report

Create:

```text
reports/baseline_report.md
```

Include:

1. error count by model;
2. error rate by model;
3. error type distribution;
4. examples;
5. which prompt categories trigger errors;
6. whether errors appear mostly in forced morphology tasks or natural free generation;
7. uncertainty/unknown cases.

## Decision gate

At the end of Phase 6 ask:

### Case A — Morphology errors are frequent enough

Proceed to constrained decoding.

### Case B — Errors exist but only in certain categories

Focus the constraint system on those categories.

### Case C — Errors are extremely rare

Do not force the original hypothesis.

Possible research value may instead lie in:

- systematic measurement;
- morphology benchmark creation;
- tokenizer/morpheme efficiency;
- lower-resource Kazakh models;
- quantization effects.

## Definition of done

I have a defensible baseline error rate, examples, an annotation guide, and a clear decision about whether constrained decoding is worth implementing.

---

# Phase 7 — Controlled quantization study

## Goal

Separate the effect of model architecture from the effect of quantization.

A comparison such as:

```text
Sherkala 8B Q4
vs
Qwen3 1.7B BF16
```

does **not** isolate quantization because parameter count, training data, architecture and specialization all differ.

## Required controlled comparison

Use the **same model** in at least two precisions.

Recommended:

```text
Qwen3 1.7B BF16
Qwen3 1.7B 4-bit
```

Optional:

```text
Qwen3 1.7B BF16
Qwen3 1.7B 8-bit
Qwen3 1.7B 4-bit
```

Keep constant:

- prompts;
- tokenizer;
- generation parameters;
- seed;
- maximum generated tokens;
- chat template.

Measure:

- morphology error rate;
- exact/near output differences;
- fluency;
- lexical diversity;
- tokens/sec;
- peak VRAM;
- model load memory;
- latency.

## bitsandbytes configuration to standardize

For a 4-bit Transformers experiment, record every option explicitly.

Example target configuration:

```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
```

Do not just write “4-bit”.

## GGUF experiments

If using GGUF, save the exact quant type:

```text
Q4_K_M
Q5_K_M
Q6_K
Q8_0
```

and exact file/model revision.

Do not mix bitsandbytes NF4 and GGUF Q4_K_M under one generic label without documenting the difference.

## Output

Create:

```text
reports/quantization_report.md
```

## Definition of done

At least one model has been evaluated in a controlled non-quantized vs quantized comparison.

---

# Phase 8 — Select the primary research model(s)

## Goal

Do not build the constrained decoder for every model immediately.

Choose one primary model and one secondary validation model.

## Selection criteria

Consider:

1. Kazakh fluency;
2. baseline morphology error rate;
3. compatibility with Transformers logits access;
4. VRAM requirement;
5. speed;
6. tokenizer behavior;
7. reproducibility;
8. whether constraints can be inserted cleanly during decoding.

## Likely initial choice

A practical initial strategy:

```text
Primary:
Sherkala 8B 4-bit
or another Kazakh-focused model that exposes generation logits cleanly.

Development/debug model:
Qwen3 1.7B BF16
```

The small model is useful because experiments and debugging are much faster.

## Important implementation consideration

For constrained decoding, a Transformers model is preferable during development because custom `LogitsProcessor` logic can be integrated directly.

GGUF/llama.cpp can remain useful for baseline inference, but it may complicate rapid experimental modification of token-level logits.

## Definition of done

One model is formally chosen for implementation/debugging and at least one different model is reserved for testing whether the method generalizes.

---

# Phase 9 — Build the morphology analyzer prototype

## Goal

Create a component that answers:

> Given the partial/current Kazakh word, which morphological continuations are legal?

The analyzer should not initially try to solve all of Kazakh morphology.

Start with a minimal, testable subset.

## Required output states

Every analyzed form/continuation should result in one of:

```text
LEGAL
ILLEGAL
UNKNOWN
```

### Conservative rule

`UNKNOWN` must not be treated as `ILLEGAL`.

This prevents the system from blocking:

- names;
- loanwords;
- rare words;
- technical vocabulary;
- words absent from the lexicon.

## Initial morphology scope

Implement progressively:

### Step 1

Vowel harmony for a limited known vocabulary.

### Step 2

Plural allomorph selection.

### Step 3

Common case endings.

### Step 4

Possessive suffixes.

### Step 5

Multi-suffix order.

### Step 6

Common phonological alternations.

### Step 7

Exceptions and loanwords.

Do not try to implement every edge case before validating the decoding pipeline.

## Tests first

For each morphology rule, add unit tests.

Example:

```python
def test_plural_vowel_harmony():
    assert analyze("балалар") == LEGAL
    assert analyze("балалер") == ILLEGAL
```

Also test unknowns:

```python
assert analyze("some_unknown_name") == UNKNOWN
```

## FST direction

Once the rule-based prototype works, evaluate whether the rules should be represented using a finite-state automaton/transducer.

The decoding system ultimately needs fast legality checks, because they may happen at every generation step.

## Definition of done

The analyzer correctly handles a documented subset of morphology and has tests for valid, invalid, and unknown forms.

---

# Phase 10 — Implement constrained decoding

## Goal

Intervene **during token generation**, rather than fixing the text afterward.

Conceptually:

```text
model
  ↓
raw logits
  ↓
morphology/pragmatic control
  ↓
modified logits
  ↓
token selection
```

## Part A — Hard morphological constraint

For candidates that definitely create an illegal form:

```text
logit = -infinity
```

They become impossible after softmax.

Important:

Only block **known illegal** candidates.

Do not block unknown candidates by default.

## Part B — Fallback/reversibility

The constrained decoder must never deadlock generation.

If the filter removes every viable candidate:

1. detect that no valid continuation remains;
2. disable/relax the constraint for that step;
3. allow the original model distribution;
4. log the fallback event.

This event itself becomes an experimental metric.

## Part C — Soft control

Add only after hard morphology works.

Concept:

```text
final_logits =
    model_logits
    + lambda * pragmatic_score
    + hard_morphology_mask
```

Possible soft preferences:

- Kazakh lexical preference;
- reduction of unnecessary code-switching;
- register/style preferences.

Do not mix soft-control development with hard morphology debugging at the beginning.

## Part D — Tokenization problem

The major technical problem:

```text
LLM tokens != morphemes
```

The current word can span several BPE tokens.

The decoding layer therefore needs state tracking for:

- current text;
- current partial word;
- token-to-string reconstruction;
- possible roots/morpheme states;
- candidate next-token text.

Candidate legality must be checked against the reconstructed word state, not by pretending every token is a suffix.

## Candidate filtering efficiency

Do not evaluate the full vocabulary using expensive morphology logic at every step.

Possible approach:

1. obtain model logits;
2. take top-K plausible next tokens;
3. evaluate morphology only for those candidates;
4. mask illegal candidates;
5. renormalize/select.

Benchmark multiple K values later.

## Instrumentation

For every constrained generation save:

```text
number of generated tokens
number of steps where filter was active
number of candidate tokens rejected
number of fallback events
time spent in analyzer
total generation time
tokens/sec
peak VRAM
```

## Definition of done

The model can generate text end-to-end with the morphology layer turned on/off using a configuration flag.

---

# Phase 11 — Controlled constrained-decoding experiments

## Goal

Measure the contribution of each system component.

## Required experiment conditions

For the same model/prompt/settings compare:

### C0 — Baseline

```text
No morphology control
No soft control
```

### C1 — Hard only

```text
Morphological hard constraint
No soft control
```

### C2 — Soft only

```text
No hard morphology constraint
Soft preference layer only
```

### C3 — Full

```text
Hard morphology constraint
+
Soft preference layer
```

If soft control is not implemented or justified yet, first compare:

```text
C0 baseline
vs
C1 hard morphology
```

Do not delay useful results for unnecessary complexity.

## Lambda sweep

When the soft layer exists, test predefined values.

Example:

```text
lambda = 0
lambda = 0.25
lambda = 0.5
lambda = 1.0
lambda = 2.0
```

The exact values can change after pilot experiments, but they must be documented.

## Multiple seeds

For stochastic generation run multiple seeds per configuration.

Do not interpret one lucky generation as a result.

## Main metrics

### Primary

- proportion of morphologically incorrect generated word forms.

### Control metrics

- fluency;
- lexical diversity;
- output length;
- repetition;
- code-switching;
- generation latency;
- tokens/sec;
- slowdown factor;
- peak VRAM;
- constraint intervention rate;
- fallback rate.

## Slowdown

Compute:

```text
constrained_generation_time
---------------------------
baseline_generation_time
```

or equivalently compare tokens/sec.

A morphology method that is correct but makes generation unusably slow is still an important negative/engineering result.

## Constraint intervention rate

Measure how often the method actually changes something.

For example:

```text
generation steps where ≥1 candidate was blocked
-----------------------------------------------
total generation steps
```

If the intervention rate is nearly zero, the quality difference may naturally be tiny.

## Statistical reporting

As the dataset grows, report:

- mean;
- median where useful;
- standard deviation;
- confidence intervals where appropriate;
- per-prompt-category results;
- per-model results.

Avoid relying only on a single global average.

## Definition of done

I have a reproducible baseline-vs-constrained comparison with enough samples to identify whether morphology control helps, hurts, or has little effect.

---

# Phase 12 — Analysis, reproducibility, and final report

## Goal

Turn code and generations into a research result that another person can inspect and reproduce.

## Final report structure

### 1. Problem

Explain the issue of Kazakh morphological generation and why agglutination is relevant.

### 2. Research question

Example:

> How frequently do local LLMs produce morphologically invalid Kazakh word forms, and can inference-time morphological constraints reduce these errors without unacceptable degradation in fluency or generation speed?

### 3. Hardware and software

Include:

- RTX 4060 8 GB;
- system RAM;
- driver;
- Python;
- PyTorch;
- Transformers;
- exact model repositories;
- exact model revisions;
- quantization method.

### 4. Models

For every model include:

- parameters;
- precision;
- quantization;
- language specialization;
- inference backend.

### 5. Benchmark

Describe:

- prompt categories;
- number of prompts;
- versions;
- how prompts were designed;
- why each morphology phenomenon is represented.

### 6. Baseline results

Report morphology errors before any intervention.

### 7. Morphology analyzer

Document:

- rules covered;
- known limitations;
- handling of unknown words;
- exceptions;
- tests.

### 8. Constrained decoding

Explain:

- state tracking;
- token reconstruction;
- candidate filtering;
- hard mask;
- fallback behavior;
- soft layer if implemented.

### 9. Experiments

Compare configurations fairly.

### 10. Results

Report both morphology and quality/performance metrics.

### 11. Error analysis

Show examples where:

- baseline was wrong and constraint fixed it;
- both were correct;
- constraint incorrectly blocked something;
- constraint reduced fluency;
- word was unknown;
- tokenizer made analysis difficult.

### 12. Limitations

Explicitly document:

- incomplete morphology coverage;
- annotation uncertainty;
- loanwords;
- named entities;
- tokenizer mismatch;
- dataset size;
- quantization effects;
- hardware limits.

### 13. Conclusion

The result can legitimately be any of:

```text
Strong improvement
Moderate improvement
No meaningful improvement
Baseline morphology errors were already rare
Constraints damage fluency/performance too much
```

A negative result is still useful if the experiment is well designed.

---

# Experiment Naming Convention

Every run should be identifiable.

Example:

```text
baseline-v1__qwen3-1.7b__bf16__seed42
baseline-v1__qwen3-1.7b__nf4__seed42
baseline-v1__sherkala-8b__nf4__seed42

hard-v1__sherkala-8b__nf4__seed42
full-v1__sherkala-8b__nf4__lambda0.5__seed42
```

Do not use ambiguous folders such as:

```text
test2/
new/
final-final/
working/
```

---

# Reproducibility Rules

I will follow these rules throughout the project.

- [ ] All Python dependencies are declared through `uv`.
- [ ] `uv.lock` is committed.
- [ ] Every model repository ID is saved.
- [ ] Model revision/commit is saved when possible.
- [ ] Quantization method is always explicitly recorded.
- [ ] Generation parameters are saved with every result.
- [ ] Random seeds are saved.
- [ ] Raw model outputs are never edited.
- [ ] Processed/annotated results are stored separately.
- [ ] Prompt datasets are versioned.
- [ ] Morphology-rule changes are versioned.
- [ ] Hardware/software environment is recorded.
- [ ] Failed/OOM runs are recorded rather than silently ignored.
- [ ] The evaluator is independent from the morphology constraint.
- [ ] Unknown forms are not automatically marked as errors.

---

# Immediate Work Checklist

This is the order I should execute now.

## Milestone 1 — Environment

- [ ] Create repository.
- [ ] Run `uv init --python 3.12`.
- [ ] Add dependencies.
- [ ] Run `uv sync`.
- [ ] Verify PyTorch CUDA.
- [ ] Record environment.
- [ ] Commit.

## Milestone 2 — First local model

- [ ] Implement minimal Transformers loader.
- [ ] Run Qwen3 1.7B BF16.
- [ ] Send one Kazakh prompt.
- [ ] Record VRAM.
- [ ] Record tokens/sec.
- [ ] Save JSON output.

## Milestone 3 — Quantized inference

- [ ] Add bitsandbytes configuration.
- [ ] Run one model in 4-bit.
- [ ] Confirm actual VRAM reduction.
- [ ] Save exact quantization settings.

## Milestone 4 — Required Kazakh model

- [ ] Download/load Sherkala 8B.
- [ ] Run Sherkala in 4-bit.
- [ ] Confirm stable Kazakh generation.
- [ ] Save resource measurements.

## Milestone 5 — All five models

- [ ] Sherkala 8B.
- [ ] KazLLM 8B.
- [ ] Qwen3 8B.
- [ ] Qwen3 1.7B.
- [ ] SozKZ 1B.
- [ ] Update `reports/model_inventory.md`.

## Milestone 6 — Prompt benchmark

- [ ] Write 15 initial morphology tests.
- [ ] Assign category IDs.
- [ ] Review them.
- [ ] Freeze as `morphology_v1.jsonl`.

## Milestone 7 — Baseline

- [ ] Run exact same prompt set on all five models.
- [ ] Save raw outputs.
- [ ] Check missing/failed runs.
- [ ] Do not implement constraints yet.

## Milestone 8 — Annotation

- [ ] Create annotation guideline.
- [ ] Label valid/invalid/unknown word forms.
- [ ] Create error taxonomy.
- [ ] Calculate baseline error rate.
- [ ] Write `baseline_report.md`.

## Milestone 9 — Quantization experiment

- [ ] Run Qwen3 1.7B BF16.
- [ ] Run the same Qwen3 1.7B in 4-bit.
- [ ] Use identical prompts and decoding settings.
- [ ] Compare morphology, quality, VRAM and speed.
- [ ] Write `quantization_report.md`.

## Milestone 10 — Research decision

- [ ] Decide whether morphology errors are sufficiently frequent.
- [ ] Select primary model.
- [ ] Select secondary/generalization model.
- [ ] Decide which morphology phenomena to constrain first.

## Milestone 11 — Morphology engine

- [ ] Implement legal/illegal/unknown interface.
- [ ] Start with vowel harmony.
- [ ] Add plural suffixes.
- [ ] Add cases.
- [ ] Add possessives.
- [ ] Add suffix chains.
- [ ] Add unit tests.
- [ ] Handle unknowns conservatively.

## Milestone 12 — Constrained decoding

- [ ] Track current partial word.
- [ ] Map candidate tokens to candidate continuations.
- [ ] Add hard-logit mask.
- [ ] Add fallback if everything is blocked.
- [ ] Log every intervention.
- [ ] Compare ON/OFF using one command.

## Milestone 13 — Full experiments

- [ ] Baseline.
- [ ] Hard constraint.
- [ ] Soft-only if implemented.
- [ ] Full configuration.
- [ ] Multiple seeds.
- [ ] Multiple models.
- [ ] Compute metrics.
- [ ] Analyze failure cases.

## Milestone 14 — Final research package

- [ ] Clean README.
- [ ] Environment documentation.
- [ ] Model inventory.
- [ ] Prompt benchmark.
- [ ] Annotation protocol.
- [ ] Raw results metadata.
- [ ] Processed results.
- [ ] Reproducible experiment commands.
- [ ] Final report.
- [ ] Limitations.
- [ ] Conclusions.

---

# Recommended First Commands

When beginning work, the first terminal session should approximately be:

```bash
mkdir kazakh-morphology
cd kazakh-morphology

git init
uv init --python 3.12

uv add torch transformers accelerate bitsandbytes safetensors sentencepiece
uv add huggingface-hub numpy pandas psutil pynvml tqdm pydantic rich
uv add --dev pytest ruff

uv sync

uv run python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NO CUDA')"

nvidia-smi
free -h

git add .
git commit -m "Initialize Kazakh morphology research project"
```

After that, the **first model to make work end-to-end** should be:

```text
Qwen3 1.7B BF16
```

because it is small enough to simplify debugging.

Then move to:

```text
Sherkala 8B 4-bit
```

because Sherkala is a central Kazakh-specific model for the project.

---

# Useful Model Links

Sherkala:

https://huggingface.co/inceptionai/Llama-3.1-Sherkala-8B-Chat

ISSAI KazLLM:

https://huggingface.co/issai/LLama-3.1-KazLLM-1.0-8B

ISSAI KazLLM GGUF:

https://huggingface.co/issai/LLama-3.1-KazLLM-1.0-8B-GGUF4

Qwen3 8B:

https://huggingface.co/Qwen/Qwen3-8B

Qwen3 8B GGUF:

https://huggingface.co/Qwen/Qwen3-8B-GGUF

Qwen3 1.7B:

https://huggingface.co/Qwen/Qwen3-1.7B

SozKZ:

https://huggingface.co/stukenov/sozkz-core-llama-1b-kk-instruct-v2

---

# `uv` Workflow Rules

Use:

```bash
uv add PACKAGE
```

to add normal dependencies.

Use:

```bash
uv add --dev PACKAGE
```

for development-only dependencies.

Use:

```bash
uv sync
```

to synchronize the environment.

Use:

```bash
uv run python script.py
```

to execute project Python scripts.

Use:

```bash
uv run pytest
```

for tests.

Use:

```bash
uv run ruff check .
```

for linting.

Do not maintain a manually edited `requirements.txt` as the primary environment specification. The source of truth is:

```text
pyproject.toml
uv.lock
```

---

# What I should NOT do yet

Until the baseline is complete, avoid spending significant time on:

- training or fine-tuning a model;
- implementing a complete Kazakh FST;
- building a UI;
- deploying an API;
- optimizing llama.cpp kernels;
- huge benchmark datasets;
- complicated automatic grading;
- soft pragmatic control;
- paper-quality plots;
- supporting every local model;
- manually correcting model outputs.

The immediate objective is much simpler:

> **Get reproducible local inference working, measure Kazakh morphology failures, and use those measurements to decide what the constrained-decoding system actually needs to solve.**

---

# Project Success Criteria

The project is successful if I can answer these questions with evidence:

1. Which tested local models generate the most/least Kazakh morphology errors?
2. Which morphology categories are most difficult?
3. Do Kazakh-specialized models outperform general multilingual models?
4. Does 4-bit quantization measurably affect Kazakh morphological correctness?
5. Can an inference-time morphology constraint reduce invalid word forms?
6. How often does the constraint intervene?
7. Does the constraint incorrectly block legal words?
8. Does it harm fluency or lexical diversity?
9. What is the generation-speed cost?
10. Does the approach generalize to more than one model?
11. What are the main failure cases and limits of the method?

Those questions should guide implementation decisions throughout the project.
