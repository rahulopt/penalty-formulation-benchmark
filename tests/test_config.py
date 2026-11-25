from src.config_loader import load_config


def test_baseline_config():
    config = load_config()
    assert sum(r["demand"] for r in config["regions"]) == 1000
    assert config["inventory"]["available_units"] == 800
    assert len({r["id"] for r in config["regions"]}) == 5
