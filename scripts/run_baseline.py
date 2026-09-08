"""Run a baseline experiment: all prompts through one model, saving raw outputs."""

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

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
    parser = argparse.ArgumentParser(description="Run baseline experiment")
    parser.add_argument("--model", required=True, help="Model ID")
    parser.add_argument("--prompt-file", required=True, help="JSONL prompt file")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--max-new-tokens", type=int, default=200, help="Max new tokens")
    parser.add_argument("--experiment-id", default="baseline-v1", help="Experiment ID")
    parser.add_argument("--output-dir", default="results/raw", help="Output directory")
    args = parser.parse_args()

    model_config = load_model_config(args.model)
    prompts = load_prompts(args.prompt_file)

    output_dir = Path(args.output_dir) / args.experiment_id / args.model
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"seed_{args.seed}.jsonl"

    runner = TransformersRunner(
        model_id=model_config["id"],
        repository=model_config["repository"],
        quantization=model_config.get("quantization"),
        dtype=model_config.get("dtype", "bfloat16"),
    )

    try:
        runner.load_model()

        results = []
        for i, prompt_data in enumerate(prompts):
            prompt_id = prompt_data.get("id", f"prompt_{i}")
            prompt_text = prompt_data.get("prompt_kk", prompt_data.get("prompt", ""))

            print(f"[{i+1}/{len(prompts)}] {prompt_id}")

            record = runner.generate(
                prompt=prompt_text,
                prompt_id=prompt_id,
                experiment_id=args.experiment_id,
                seed=args.seed,
                max_new_tokens=args.max_new_tokens,
            )

            result = {
                "experiment_id": record.experiment_id,
                "model_id": record.model_id,
                "model_revision": record.model_revision,
                "backend": record.backend,
                "precision": record.precision,
                "quantization": record.quantization,
                "prompt_id": record.prompt_id,
                "prompt": record.prompt,
                "seed": record.seed,
                "temperature": record.temperature,
                "top_p": record.top_p,
                "max_new_tokens": record.max_new_tokens,
                "output": record.output,
                "prompt_tokens": record.prompt_tokens,
                "generated_tokens": record.generated_tokens,
                "generation_seconds": record.generation_seconds,
                "tokens_per_second": record.tokens_per_second,
                "peak_vram_mb": record.peak_vram_mb,
                "timestamp": record.timestamp,
            }
            results.append(result)

        with open(output_file, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in results)

        print(f"\nSaved {len(results)} results to {output_file}")

    finally:
        runner.unload_model()


if __name__ == "__main__":
    main()
