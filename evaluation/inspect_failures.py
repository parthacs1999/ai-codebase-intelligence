
import csv
from pathlib import Path


RESULTS_PATH = Path(__file__).resolve().parent / "results.csv"


def main():
    with RESULTS_PATH.open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    for row in rows:
        if row["hit_at_5"] != "0":
            continue

        print(
            row["id"],
            row["method"],
            row["query"],
            "Expected chunk not found in top 5"
        )


if __name__ == "__main__":
    main()
