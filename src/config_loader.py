from pathlib import Path
import yaml


def load_config(config_path=None):
    if config_path is None:
        config_path = Path(__file__).resolve().parents[1] / "configs" / "base.yaml"
    with open(config_path, encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


if __name__ == "__main__":
    config = load_config()
    demand = sum(r["demand"] for r in config["regions"])
    capacity = config["inventory"]["available_units"]
    print("Scenario:", config["experiment"]["scenario_id"])
    print("Total demand:", demand)
    print("Available inventory:", capacity)
    print("Minimum shortage:", max(0, demand - capacity))
