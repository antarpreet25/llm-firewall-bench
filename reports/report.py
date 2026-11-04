import json
def loader():
    results = []
    with open("results/results.jsonl", "r") as f:
        for line in f:
            data = json.loads(line)
            results.append(data)
    return results


def group_results_by_category(results):
    group = {}
    for r in results:
        category = r["category"]
        if category not in group:
            group[category] = []
        group[category].append(r)
    return group



def summarise():

    results = loader()
    group = group_results_by_category(results)
    print(group)
    labels = list(set(r["score"] for r in group))
    print(f"Labels: {labels}")
    for cat in list(group.keys()):
        total_prompts = len(group[cat])
        print(f"\nCategory: {cat} | Count: {total_prompts}")
        label_counts = {}
        for label in labels:
            label_counts[label] = sum(1 for r in group[cat] if r["score"] == label)
        print(f"Label Counts: {label_counts}")

        return "HELOOOOOOO"

