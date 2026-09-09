import torch
import json
import time
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path

REPO = "inceptionai/Llama-3.1-Sherkala-8B-Chat"
PROMPT_FILE = "data/prompts/morphology_v1.jsonl"
OUTPUT_DIR = Path("results/raw/sherkala-8b-cpu")
OUTPUT_FILE = OUTPUT_DIR / "seed_42.jsonl"

# Load already done prompts
done_ids = set()
if OUTPUT_FILE.exists():
    with open(OUTPUT_FILE, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            done_ids.add(r["prompt_id"])

print(f"Already done: {done_ids}")

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(REPO, trust_remote_code=True)

print("Loading model on CPU (fp16)...")
t0 = time.time()
model = AutoModelForCausalLM.from_pretrained(
    REPO,
    torch_dtype=torch.float16,
    device_map="cpu",
    trust_remote_code=True,
)
print(f"Model loaded in {time.time()-t0:.0f}s")

prompts = []
with open(PROMPT_FILE, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            p = json.loads(line)
            if p["id"] not in done_ids:
                prompts.append(p)

print(f"Running {len(prompts)} remaining prompts...")

for i, p in enumerate(prompts):
    prompt_id = p["id"]
    prompt_text = p["prompt_kk"]

    print(f"\n[{i+1}/{len(prompts)}] {prompt_id}: {prompt_text[:60]}...")

    inputs = tokenizer(prompt_text, return_tensors="pt")

    t1 = time.time()
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
        )
    elapsed = time.time() - t1
    result = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

    record = {
        "experiment_id": "sherkala-baseline",
        "model_id": "sherkala-8b",
        "model_revision": "",
        "backend": "transformers",
        "precision": "float16",
        "quantization": None,
        "prompt_id": prompt_id,
        "prompt": prompt_text,
        "seed": 42,
        "temperature": 0.7,
        "top_p": 1.0,
        "max_new_tokens": 200,
        "output": result,
        "prompt_tokens": inputs["input_ids"].shape[1],
        "generated_tokens": out.shape[1] - inputs["input_ids"].shape[1],
        "generation_seconds": elapsed,
        "tokens_per_second": (out.shape[1] - inputs["input_ids"].shape[1]) / elapsed,
        "peak_vram_mb": 0,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
    }

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"  Done in {elapsed:.0f}s | Output: {result[:150]}...")

print(f"\nAll done! Results saved to {OUTPUT_FILE}")
