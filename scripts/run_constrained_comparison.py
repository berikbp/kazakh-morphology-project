"""Run constrained vs unconstrained decoding comparison."""

import argparse
import json
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from kazakh_morphology.decoding.constrained_generator import ConstrainedGenerator
from kazakh_morphology.inference.transformers_runner import TransformersRunner


def load_model_config(model_id: str) -> dict:
    config_path = Path(__file__).resolve().parent.parent / "configs" / "models.yaml"
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    for m in config["models"]:
        if m["id"] == model_id:
            return m
    raise ValueError(f"Model '{model_id}' not found")


def load_prompts(prompt_file: str) -> list[dict]:
    prompts = []
    with open(prompt_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                prompts.append(json.loads(line))
    return prompts


def main():
    parser = argparse.ArgumentParser(description="Constrained vs unconstrained decoding")
    parser.add_argument("--model", required=True, help="Model ID")
    parser.add_argument("--prompt-file", required=True, help="JSONL prompt file")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--max-new-tokens", type=int, default=200, help="Max new tokens")
    parser.add_argument("--output-dir", default="results/raw", help="Output directory")
    args = parser.parse_args()

    model_config = load_model_config(args.model)
    prompts = load_prompts(args.prompt_file)

    output_dir = Path(args.output_dir)
    unconstrained_dir = output_dir / "constrained-v1" / f"{args.model}__unconstrained"
    constrained_dir = output_dir / "constrained-v1" / f"{args.model}__hard_constraint"
    unconstrained_dir.mkdir(parents=True, exist_ok=True)
    constrained_dir.mkdir(parents=True, exist_ok=True)

    unconstrained_file = unconstrained_dir / f"seed_{args.seed}.jsonl"
    constrained_file = constrained_dir / f"seed_{args.seed}.jsonl"

    # Run unconstrained
    print("=" * 60)
    print("RUNNING UNCONSTRAINED BASELINE")
    print("=" * 60)

    runner = TransformersRunner(
        model_id=model_config["id"],
        repository=model_config["repository"],
        quantization=model_config.get("quantization"),
        dtype=model_config.get("dtype", "bfloat16"),
    )

    unconstrained_results = []
    try:
        runner.load_model()

        for i, prompt_data in enumerate(prompts):
            prompt_id = prompt_data.get("id", f"prompt_{i}")
            prompt_text = prompt_data.get("prompt_kk", prompt_data.get("prompt", ""))
            print(f"[UNCONSTRAINED {i+1}/{len(prompts)}] {prompt_id}")

            record = runner.generate(
                prompt=prompt_text,
                prompt_id=prompt_id,
                experiment_id="constrained-v1",
                seed=args.seed,
                max_new_tokens=args.max_new_tokens,
            )

            result = {
                "experiment_id": "constrained-v1__unconstrained",
                "model_id": record.model_id,
                "precision": record.precision,
                "quantization": record.quantization,
                "prompt_id": record.prompt_id,
                "prompt": record.prompt,
                "seed": record.seed,
                "output": record.output,
                "generated_tokens": record.generated_tokens,
                "generation_seconds": record.generation_seconds,
                "tokens_per_second": record.tokens_per_second,
                "peak_vram_mb": record.peak_vram_mb,
            }
            unconstrained_results.append(result)

    finally:
        runner.unload_model()

    with open(unconstrained_file, "w", encoding="utf-8") as f:
        for r in unconstrained_results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Saved {len(unconstrained_results)} unconstrained results")

    # Run constrained
    print("\n" + "=" * 60)
    print("RUNNING CONSTRAINED DECODING")
    print("=" * 60)

    gen = ConstrainedGenerator(
        model_id=model_config["id"],
        repository=model_config["repository"],
        quantization=model_config.get("quantization"),
        dtype=model_config.get("dtype", "bfloat16"),
    )

    constrained_results = []
    try:
        gen.load_model()

        for i, prompt_data in enumerate(prompts):
            prompt_id = prompt_data.get("id", f"prompt_{i}")
            prompt_text = prompt_data.get("prompt_kk", prompt_data.get("prompt", ""))
            print(f"[CONSTRAINED {i+1}/{len(prompts)}] {prompt_id}")

            record, stats = gen.generate(
                prompt=prompt_text,
                prompt_id=prompt_id,
                experiment_id="constrained-v1",
                seed=args.seed,
                max_new_tokens=args.max_new_tokens,
                constrained=True,
                top_k=50,
            )

            result = {
                "experiment_id": "constrained-v1__hard_constraint",
                "model_id": record.model_id,
                "precision": record.precision,
                "quantization": record.quantization,
                "prompt_id": record.prompt_id,
                "prompt": record.prompt,
                "seed": record.seed,
                "output": record.output,
                "generated_tokens": record.generated_tokens,
                "generation_seconds": record.generation_seconds,
                "tokens_per_second": record.tokens_per_second,
                "peak_vram_mb": record.peak_vram_mb,
                "constraint_stats": stats,
            }
            constrained_results.append(result)

    finally:
        gen.unload_model()

    with open(constrained_file, "w", encoding="utf-8") as f:
        for r in constrained_results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Saved {len(constrained_results)} constrained results")

    # Summary
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)

    u_total_time = sum(r["generation_seconds"] for r in unconstrained_results)
    c_total_time = sum(r["generation_seconds"] for r in constrained_results)
    u_total_tokens = sum(r["generated_tokens"] for r in unconstrained_results)
    c_total_tokens = sum(r["generated_tokens"] for r in constrained_results)

    total_rejected = sum(
        r.get("constraint_stats", {}).get("candidates_rejected", 0)
        for r in constrained_results
    )
    total_steps = sum(
        r.get("constraint_stats", {}).get("steps", 0)
        for r in constrained_results
    )
    steps_with_filter = sum(
        r.get("constraint_stats", {}).get("steps_with_filter", 0)
        for r in constrained_results
    )
    fallback_events = sum(
        r.get("constraint_stats", {}).get("fallback_events", 0)
        for r in constrained_results
    )

    print(f"Unconstrained: {u_total_tokens} tokens in {u_total_time:.1f}s ({u_total_tokens/u_total_time:.1f} tok/s)")
    print(f"Constrained:   {c_total_tokens} tokens in {c_total_time:.1f}s ({c_total_tokens/c_total_time:.1f} tok/s)")
    print(f"Slowdown: {c_total_time/u_total_time:.2f}x")
    print(f"Constraint steps: {steps_with_filter}/{total_steps} ({100*steps_with_filter/total_steps:.0f}%)" if total_steps > 0 else "N/A")
    print(f"Candidates rejected: {total_rejected}")
    print(f"Fallback events: {fallback_events}")


if __name__ == "__main__":
    main()
