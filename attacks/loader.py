import json


def load_dataset(filename: str = "attacks/dataset.jsonl") -> list:
    with open(filename, "r") as f:
        prompts = []
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            data = json.loads(line)
            prompts.append(data)
        return prompts

def get_prompts_by_category():
    dataset = load_dataset()

    category_seen = {}

    for item in dataset:
        category = item["category"]
        if category not in category_seen:
            category_seen[category] = []
        category_seen[category].append(item)

    return category_seen

if __name__ == "__main__":

    print(load_dataset())

    group_prompt = get_prompts_by_category()
    print(group_prompt["prompt_leaking"])