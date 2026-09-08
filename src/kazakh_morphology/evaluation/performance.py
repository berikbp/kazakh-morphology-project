"""Performance metrics for generation experiments."""

import json


def compute_generation_metrics(results_file: str) -> dict:
    results = []
    with open(results_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))

    if not results:
        return {}

    total_tokens = sum(r["generated_tokens"] for r in results)
    total_time = sum(r["generation_seconds"] for r in results)
    avg_tok_per_sec = total_tokens / total_time if total_time > 0 else 0
    peak_vram = max(r["peak_vram_mb"] for r in results)

    return {
        "num_prompts": len(results),
        "total_generated_tokens": total_tokens,
        "total_generation_seconds": round(total_time, 2),
        "avg_tokens_per_second": round(avg_tok_per_sec, 1),
        "peak_vram_mb": round(peak_vram, 0),
        "min_tokens_per_second": round(
            min(r["tokens_per_second"] for r in results), 1
        ),
        "max_tokens_per_second": round(
            max(r["tokens_per_second"] for r in results), 1
        ),
    }
