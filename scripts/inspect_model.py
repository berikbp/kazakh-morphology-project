"""Inspect a model: load it, record properties, test generation, and unload."""

import argparse
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


def main():
    parser = argparse.ArgumentParser(description="Inspect a model")
    parser.add_argument("--model", required=True, help="Model ID")
    parser.add_argument("--prompt", default="Қазақ тілінде бір сөйлем жаз.", help="Test prompt")
    args = parser.parse_args()

    model_config = load_model_config(args.model)

    runner = TransformersRunner(
        model_id=model_config["id"],
        repository=model_config["repository"],
        quantization=model_config.get("quantization"),
        dtype=model_config.get("dtype", "bfloat16"),
    )

    try:
        import torch

        runner.load_model()

        print(f"\nModel: {model_config['name']}")
        print(f"Repository: {model_config['repository']}")
        print(f"Quantization: {model_config.get('quantization', 'None')}")
        print(f"Dtype: {model_config.get('dtype', 'bfloat16')}")

        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            print(f"GPU VRAM total: {props.total_memory / (1024**2):.0f} MB")

        record = runner.generate(
            prompt=args.prompt,
            prompt_id="inspect",
            seed=42,
            max_new_tokens=100,
        )

        print(f"\nTest prompt: {args.prompt}")
        print(f"Output: {record.output}")
        print(f"Generated tokens: {record.generated_tokens}")
        print(f"Generation time: {record.generation_seconds:.2f}s")
        print(f"Tokens/sec: {record.tokens_per_second:.1f}")
        print(f"Peak VRAM: {record.peak_vram_mb:.0f} MB")

    finally:
        runner.unload_model()


if __name__ == "__main__":
    main()
