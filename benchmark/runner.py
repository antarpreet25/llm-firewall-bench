from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from attacks.loader import get_prompts_by_category
from reports.report import summarise
from cache.caching import hash_params

from pathlib import Path
import os
import json
import time
from dotenv import load_dotenv
from cache.config import CONFIG
load_dotenv() 

class BenchmarkRunner:
    def __init__(self):
        self.model_name = CONFIG["model_name"]
        self.max_tokens = CONFIG["max_tokens"]
        self.temp = CONFIG["temp"]
        self.sysprompt = CONFIG["sysprompt"]
        self.canary = CONFIG["canary"]

        self.llm = ChatGroq(model = self.model_name, api_key = os.getenv("GROQ_API_KEY"), max_tokens = self.max_tokens, temperature = self.temp)



        self.cache_path = Path("cache/response_cache.jsonl")
        self.persistent_cache = self.load_cache()



    def load_cache(self) -> dict:

        cache_dict = {}

        self.cache_path.parent.mkdir(parents = True , exist_ok = True)


        if not self.cache_path.exists():
            self.cache_path.touch()
            return cache_dict

            
        with open(self.cache_path, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    cache_dict[data["fingerprint"]] = data["response"]
        return cache_dict




    def caller(self, prompt: str) -> str:

        messages = [
            SystemMessage(content = self.sysprompt),
            HumanMessage(content = prompt)
        ]
        response = self.llm.invoke(messages)
        return response.content


    

    def run(self) -> list:
        results = []
        grouped_prompts = get_prompts_by_category()
        for category, prompts in grouped_prompts.items():
            for prompt in prompts:
                prompt_text = prompt["prompt"]
                fingerprint = hash_params(CONFIG, prompt_text)

                # 1. Resolve response (Cache Hit vs Cache Miss)
                if fingerprint in self.persistent_cache:
                    response = self.persistent_cache[fingerprint]
                else:
                    time.sleep(1)
                    try:
                        response = self.caller(prompt_text)
                    except Exception as e:
                        print(f"Error calling model for {prompt['id']}: {e}")
                        response = None   # scored as ERROR, never cached
                    else:
                        self.persistent_cache[fingerprint] = response
                        cache_entry = {"fingerprint": fingerprint, "response": response}
                        with open(self.cache_path, "a", encoding="utf-8") as f:
                            f.write(json.dumps(cache_entry) + "\n")
                # 2. Build the result entry once for both paths
                results_entry = {
                    "id": prompt["id"],
                    "category": prompt["category"],
                    "prompt": prompt_text,
                    "response": response,
                    "expected": prompt["expected_resistance"],
                    "success_marker": prompt["success_marker"]
                }
                results.append(results_entry)

        return results





    def score_results(self, results: list) -> list:
        from benchmark.scorer import ResponseScorer
        scorer = ResponseScorer()
        scored_results = scorer.score_all(results)
        scorer.logger(scored_results)
        return scored_results









if __name__ == "__main__":
    runner = BenchmarkRunner()

    results = runner.run()
    scored_results = runner.score_results(results)

    for r in scored_results:
        print(f"\n{r['id']} | {r['category']}")
        print(f"Expected: {r['expected']}")
        print(f"Response: {str(r['response'])[:2000]}...")
        print(f"Outcome: {r['outcome']}")
        print(f"Reason: {r['reason']}")
        print(f"Canary leaked: {r['canary_leaked']}")

    