"""Summarize results from a JSONL results directory into a summary report."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_results(results_dir: str) -> list[dict]:
    results = []
    results_path = Path(results_dir)
    for jsonl_file in results_path.rglob("*.jsonl"):
        with open(jsonl_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    results.append(json.loads(line))
    return results


def summarize(results: list[dict]) -> dict:
    by_model = defaultdict(list)
    for r in results:
        by_model[r["model_id"]].append(r)

    summary = {}
    for model_id, records in by_model.items():
        total_tokens = sum(r["generated_tokens"] for r in records)
        total_time = sum(r["generation_seconds"] for r in records)
        avg_tok_per_sec = total_tokens / total_time if total_time > 0 else 0
        peak_vram = max(r["peak_vram_mb"] for r in records)

        summary[model_id] = {
            "num_prompts": len(records),
            "total_generated_tokens": total_tokens,
            "total_generation_seconds": round(total_time, 2),
            "avg_tokens_per_second": round(avg_tok_per_sec, 1),
            "peak_vram_mb": round(peak_vram, 0),
            "prompt_ids": [r["prompt_id"] for r in records],
        }

    return summary


def main():
    parser = argparse.ArgumentParser(description="Summarize experiment results")
    parser.add_argument("--results-dir", required=True, help="Directory with JSONL results")
    parser.add_argument("--output", default=None, help="Output JSON file")
    args = parser.parse_args()

    results = load_results(args.results_dir)

    if not results:
        print("No results found.", file=sys.stderr)
        return

    summary = summarize(results)
    output = json.dumps(summary, ensure_ascii=False, indent=2)
    print(output)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\nSaved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
