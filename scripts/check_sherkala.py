import json

with open("results/raw/sherkala-8b-cpu/seed_42.jsonl", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        print(f"--- {r['prompt_id']} ---")
        print(f"Prompt: {r['prompt'][:100]}")
        print(f"Output: {r['output'][:300]}")
        print()
