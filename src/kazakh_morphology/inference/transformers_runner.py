from __future__ import annotations

import gc
import time
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from kazakh_morphology.inference.base import BaseRunner, GenerationRecord


class TransformersRunner(BaseRunner):
    def __init__(
        self,
        model_id: str,
        repository: str,
        quantization: str | None = None,
        dtype: str = "bfloat16",
        device_map: str = "auto",
    ):
        self.model_id = model_id
        self.repository = repository
        self.quantization = quantization
        self.dtype_str = dtype
        self.device_map = device_map
        self.model = None
        self.tokenizer = None

    def _get_dtype(self) -> torch.dtype:
        if self.dtype_str == "bfloat16":
            return torch.bfloat16
        elif self.dtype_str == "float16":
            return torch.float16
        return torch.float32

    def _get_bnb_config(self) -> BitsAndBytesConfig | None:
        if self.quantization == "4bit":
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )
        elif self.quantization == "8bit":
            return BitsAndBytesConfig(load_in_8bit=True)
        return None

    def load_model(self) -> None:
        print(f"Loading {self.model_id} from {self.repository}...")
        t0 = time.time()

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.repository, trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        load_kwargs: dict[str, Any] = {
            "device_map": self.device_map,
            "trust_remote_code": True,
        }

        bnb_config = self._get_bnb_config()
        if bnb_config is not None:
            load_kwargs["quantization_config"] = bnb_config
        else:
            load_kwargs["torch_dtype"] = self._get_dtype()

        self.model = AutoModelForCausalLM.from_pretrained(
            self.repository, **load_kwargs
        )

        elapsed = time.time() - t0
        print(f"Model loaded in {elapsed:.1f}s")

    def generate(
        self,
        prompt: str,
        prompt_id: str = "unknown",
        experiment_id: str = "default",
        seed: int = 42,
        max_new_tokens: int = 200,
        temperature: float = 0.0,
        top_p: float = 1.0,
        do_sample: bool = False,
        **kwargs: Any,
    ) -> GenerationRecord:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()

        inputs = self.tokenizer(prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        prompt_tokens = inputs["input_ids"].shape[1]

        t0 = time.time()
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature if do_sample else None,
                top_p=top_p if do_sample else None,
                do_sample=do_sample,
                pad_token_id=self.tokenizer.pad_token_id,
                **kwargs,
            )
        elapsed = time.time() - t0

        generated_ids = outputs[0][prompt_tokens:]
        generated_tokens = len(generated_ids)
        output_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        peak_vram = 0.0
        if torch.cuda.is_available():
            peak_vram = torch.cuda.max_memory_allocated() / (1024**2)

        return GenerationRecord(
            experiment_id=experiment_id,
            model_id=self.model_id,
            model_revision="",
            backend="transformers",
            precision=self.dtype_str,
            quantization=self.quantization,
            prompt_id=prompt_id,
            prompt=prompt,
            seed=seed,
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=max_new_tokens,
            output=output_text,
            prompt_tokens=prompt_tokens,
            generated_tokens=generated_tokens,
            generation_seconds=elapsed,
            tokens_per_second=generated_tokens / elapsed if elapsed > 0 else 0.0,
            peak_vram_mb=peak_vram,
        )

    def unload_model(self) -> None:
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        print(f"Model {self.model_id} unloaded")
