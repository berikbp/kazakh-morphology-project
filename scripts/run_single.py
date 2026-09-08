"""Run a single prompt through a model and output the result as JSON."""

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
    raise ValueError(f"Model '{model_id}' not found in configs/models.yaml")


def main():
    parser = argparse.ArgumentParser(description="Run single prompt inference")
    parser.add_argument("--model", required=True, help="Model ID from configs/models.yaml")
    parser.add_argument("--prompt", required=True, help="Prompt text")
    parser.add_argument("--prompt-id", default="manual", help="Prompt identifier")
    parser.add_argument("--experiment-id", default="single-test", help="Experiment identifier")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--max-new-tokens", type=int, default=200, help="Max new tokens")
    parser.add_argument("--do-sample", action="store_true", help="Enable sampling")
    parser.add_argument("--temperature", type=float, default=0.0, help="Temperature")
    parser.add_argument("--output", type=str, default=None, help="Output JSON file")
    args = parser.parse_args()

    model_config = load_model_config(args.model)

    runner = TransformersRunner(
        model_id=model_config["id"],
        repository=model_config["repository"],
        quantization=model_config.get("quantization"),
        dtype=model_config.get("dtype", "bfloat16"),
    )

    try:
        runner.load_model()

        record = runner.generate(
            prompt=args.prompt,
            prompt_id=args.prompt_id,
            experiment_id=args.experiment_id,
            seed=args.seed,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            do_sample=args.do_sample,
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

        print(json.dumps(result, ensure_ascii=False, indent=2))

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\nSaved to {output_path}", file=sys.stderr)

    finally:
        runner.unload_model()


if __name__ == "__main__":
    main()
