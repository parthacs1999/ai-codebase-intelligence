
import csv
from collections import defaultdict
from pathlib import Path


RESULTS_PATH = Path(__file__).resolve().parent / "results.csv"


def main():
    grouped = defaultdict(dict)

    with RESULTS_PATH.open(encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            grouped[row["id"]][row["method"]] = row

    for query_id, methods in grouped.items():
        hybrid = methods.get("Hybrid")
        symbols = methods.get("Hybrid+Symbols")
        reranked = methods.get("Hybrid+Symbols+Reranker")

        if not all([hybrid, symbols, reranked]):
            continue

        print("\n" + "=" * 70)
        print(query_id, symbols["query"])
        print("Category:", symbols["category"])

        for name, result in [
            ("Hybrid", hybrid),
            ("Hybrid+Symbols", symbols),
            ("Reranked", reranked)
        ]:
            rank = result["rank"] or "Not found"

            print(
                f"{name:<20}"
                f"Rank: {str(rank):<12}"
                f"Latency: {result['latency_ms']} ms"
            )

        if (
            symbols["hit_at_5"] == "1"
            and reranked["hit_at_5"] == "0"
        ):
            print("ISSUE: Reranker removed a relevant result")

        if (
            symbols["hit_at_5"] == "0"
            and reranked["hit_at_5"] == "1"
        ):
            print("IMPROVEMENT: Reranker recovered a relevant result")


if __name__ == "__main__":
    main()
