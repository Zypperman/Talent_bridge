"""
Loads and validates sandbox scenario definitions from YAML files. Each
scenario drives three things from one config: the mock topology (Helm
chart), how the fault gets injected (Terraform module or Helm overlay),
and the verifier that proves the exercise is complete.

See docs/Sandbox_Architecture.md section 3.1 for the format this expects.
Named scenario_registry rather than scenarios to avoid colliding with the
sibling scenarios/ data directory this loads from.
"""

import os

import yaml

_SCENARIOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenarios")
_REQUIRED_KEYS = {"id", "title", "description", "topology", "fault", "verifier", "session"}


class ScenarioValidationError(ValueError):
    pass


def _validate(raw: dict, source: str) -> dict:
    missing = _REQUIRED_KEYS - raw.keys()
    if missing:
        raise ScenarioValidationError(f"{source}: missing required keys {sorted(missing)}")

    fault = raw["fault"]
    if fault.get("layer") not in ("infra", "app"):
        raise ScenarioValidationError(f"{source}: fault.layer must be 'infra' or 'app'")
    if fault["layer"] == "infra" and "terraform_module" not in fault:
        raise ScenarioValidationError(f"{source}: infra-layer fault requires fault.terraform_module")

    verifier = raw["verifier"]
    if "image" not in verifier or "command" not in verifier:
        raise ScenarioValidationError(f"{source}: verifier requires image and command")

    topology = raw["topology"]
    if not topology.get("components"):
        raise ScenarioValidationError(f"{source}: topology requires at least one component")

    return raw


def load_all(scenarios_dir: str = _SCENARIOS_DIR) -> dict:
    """Loads every *.yaml/*.yml scenario in scenarios_dir, keyed by scenario id."""
    scenarios = {}
    if not os.path.isdir(scenarios_dir):
        return scenarios
    for filename in sorted(os.listdir(scenarios_dir)):
        if not filename.endswith((".yaml", ".yml")):
            continue
        path = os.path.join(scenarios_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        scenario = _validate(raw, filename)
        scenarios[scenario["id"]] = scenario
    return scenarios


def get(scenario_id: str, scenarios_dir: str = _SCENARIOS_DIR):
    return load_all(scenarios_dir).get(scenario_id)
