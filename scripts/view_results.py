import json
import sys

results_file = sys.argv[1] if len(sys.argv) > 1 else "results/raw/quantization-v1/qwen3-1.7b-nf4/seed_42.jsonl"

with open(results_file, encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        print(f"--- {r['prompt_id']} ---")
        print(f"Output: {r['output'][:400]}")
        print()
