"""Validate hybrid penalty transitions against an exact S01 analytical oracle."""
import csv
import math
from pathlib import Path

from src.config_loader import load_config
from experiments.e06_hybrid_penalty import run


def main():
    config = load_config()
    regions = config["regions"]
    if len(regions) != 5 or any(r["demand"] != 200 or r["allocation_cost"] != 10 for r in regions) or config["inventory"]["available_units"] != 800:
        raise ValueError("This analytical oracle is specific to symmetric S01")
    coefficient = 0.625
    root = Path("results/S01/E06C")
    root.mkdir(parents=True, exist_ok=True)
    thresholds = [1250, 2083.75, 4166.25, 12500]
    values = sorted({0, 5000, 20000, *(t + d for t in thresholds for d in (-1, 0, 1))})
    rows = []
    for fixed in values:
        expected = {}
        for k in range(1, 6):
            a, r = divmod(200, k)
            expected[k] = 8000 + fixed*k + coefficient*((k-r)*a*a + r*(a+1)**2)
        optimum = min(expected.values())
        counts = [k for k, val in expected.items() if math.isclose(val, optimum, rel_tol=0, abs_tol=1e-7)]
        # Tighten the gap so near-threshold alternatives can be distinguished.
        config["solver"]["mip_gap"] = 0
        result = run(config, root / str(fixed), fixed=fixed, severity="quadratic", coefficient=coefficient)
        passed = (result["status"] == "OPTIMAL" and result.get("violated_regions") in counts
                  and math.isclose(result.get("objective", math.inf), optimum, rel_tol=0, abs_tol=1e-5))
        rows.append({"fixed_coefficient": fixed, "expected_counts": "|".join(map(str, counts)),
                     "actual_count": result.get("violated_regions"), "expected_objective": optimum,
                     "actual_objective": result.get("objective"), "runtime_seconds": result["runtime_seconds"],
                     "maximum_shortage": result.get("maximum_shortage"), "passed": passed})
    with (root / "summary.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row)
    print(f"Validated {sum(r['passed'] for r in rows)}/{len(rows)} cases")
    if not all(r["passed"] for r in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
