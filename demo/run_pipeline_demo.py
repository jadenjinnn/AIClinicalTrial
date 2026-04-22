import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError

from src.pipeline.audit_pipeline import PipelineConfig, format_cli_report, run_audit_pipeline
from src.schemas.patient import PatientProfile


def _load_scenarios() -> list[dict]:
    scenarios_path = Path("demo/scenarios/patient_scenarios.json")
    return json.loads(scenarios_path.read_text(encoding="utf-8"))


def _find_scenario(scenarios: list[dict], scenario_id: str) -> dict:
    for scenario in scenarios:
        if scenario["scenario_id"] == scenario_id:
            return scenario
    raise ValueError(f"scenario_id '{scenario_id}' not found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run end-to-end trial audit pipeline")
    parser.add_argument("--scenario-id", default="hf_stable_candidate", help="Scenario ID to run")
    parser.add_argument(
        "--output",
        choices=["report", "json"],
        default="report",
        help="Output mode: CLI report or full JSON payload",
    )
    parser.add_argument("--list-scenarios", action="store_true", help="List available scenarios")
    args = parser.parse_args()

    scenarios = _load_scenarios()
    if args.list_scenarios:
        payload = [
            {"scenario_id": item["scenario_id"], "description": item["description"]}
            for item in scenarios
        ]
        print(json.dumps(payload, indent=2))
        return

    try:
        scenario = _find_scenario(scenarios, args.scenario_id)
        patient = PatientProfile(**scenario["patient"])
        config = PipelineConfig(
            protocol_focus=scenario["protocol_focus"],
            fetch_query=scenario.get("fetch_query", "heart failure"),
            top_k=int(scenario.get("top_k", 3)),
        )
        report = run_audit_pipeline(patient=patient, config=config)
    except ValueError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, indent=2))
        return
    except (HTTPError, URLError, TimeoutError) as exc:  # pragma: no cover - network path
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Pipeline failed to fetch ClinicalTrials.gov evidence",
                    "details": str(exc),
                },
                indent=2,
            )
        )
        return

    if args.output == "json":
        print(json.dumps(report, indent=2))
        return

    print(format_cli_report(report, scenario_id=args.scenario_id))


if __name__ == "__main__":
    main()
