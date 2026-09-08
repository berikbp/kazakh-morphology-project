from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class GenerationRecord:
    experiment_id: str
    model_id: str
    model_revision: str
    backend: str
    precision: str
    quantization: str | None
    prompt_id: str
    prompt: str
    seed: int
    temperature: float
    top_p: float
    max_new_tokens: int
    output: str
    prompt_tokens: int
    generated_tokens: int
    generation_seconds: float
    tokens_per_second: float
    peak_vram_mb: float
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseRunner(ABC):
    @abstractmethod
    def load_model(self) -> None:
        ...

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> GenerationRecord:
        ...

    @abstractmethod
    def unload_model(self) -> None:
        ...
