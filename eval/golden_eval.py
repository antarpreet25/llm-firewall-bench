from attacks.loader import load_dataset
from benchmark.scorer import ResponseScorer




class GoldenEvaluation:
    def __init__(self):
        self.scorer = ResponseScorer()

    def eval(self):

        golden_records = load_dataset("eval/golden_set.jsonl")
        dataset_markers = {r["id"]: r["success_marker"] for r in load_dataset()}

        merged = [{**g, "success_marker" : dataset_markers.get(g["id"])} for g in golden_records]

        scored_records = self.scorer.score_all(merged)

        match = nt_total = nt_match = 0
        for s, g in zip(scored_records,golden_records):

            outcome, label = s["outcome"], g["true_outcome"]


            ok = outcome == label
            match += ok

            if g["response"].strip().rstrip(".").upper() != "REFUSED":
                nt_total += 1 
                nt_match += ok

            if not ok:
                print(f"Mismatch found at row id: {g['id']} for label: {label}")
                print(f"scorer: {s['outcome']} | reason: {s['reason']}")

        return print(f"TOTAL Matches: {match}, Non-Trivial: {nt_match/nt_total:.3f}")






if __name__ == "__main__":

    evaluator = GoldenEvaluation()
    evaluator.eval()


    print("ALL DONE!!!!!")



