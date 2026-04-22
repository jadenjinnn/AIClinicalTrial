from dataclasses import asdict, dataclass
from typing import Any

from src.agents.protocol_audit_agent import ProtocolAuditAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.schemas.patient import PatientProfile


@dataclass
class PipelineConfig:
    protocol_focus: str
    fetch_query: str = "heart failure"
    top_k: int = 3


def run_audit_pipeline(
    patient: PatientProfile,
    config: PipelineConfig,
    retrieval_agent: RetrievalAgent | None = None,
    protocol_agent: ProtocolAuditAgent | None = None,
) -> dict[str, Any]:
    retrieval = retrieval_agent or RetrievalAgent()
    protocol = protocol_agent or ProtocolAuditAgent()

    evidence_pack = retrieval.retrieve_evidence(
        patient=patient,
        protocol_focus=config.protocol_focus,
        fetch_query=config.fetch_query,
        top_k=config.top_k,
    )
    decision = protocol.audit(patient=patient, evidence_pack=evidence_pack)

    return {
        "query": evidence_pack.query,
        "citations_count": len(evidence_pack.citations),
        "decision": decision.to_dict(),
        "citations": [asdict(citation) for citation in evidence_pack.citations],
    }


def format_cli_report(report: dict[str, Any], scenario_id: str) -> str:
    def _ascii_safe(value: str) -> str:
        return value.encode("ascii", errors="replace").decode("ascii")

    decision = report["decision"]
    status = "ELIGIBLE" if decision["eligible"] else "NOT_ELIGIBLE"
    top_violations = decision.get("violations", [])[:3]
    top_justifications = decision.get("justifications", [])[:3]
    top_citations = report.get("citations", [])[:3]

    lines = [
        f"Scenario: {scenario_id}",
        f"Decision: {status}",
        f"Confidence: {decision['confidence']:.2f}",
        f"Primary Trial: {decision['trial_id']}",
        f"Citations Retrieved: {report['citations_count']}",
        "",
        "Top Violations:",
    ]
    if top_violations:
        lines.extend([f"- {_ascii_safe(item)}" for item in top_violations])
    else:
        lines.append("- None")

    lines.append("")
    lines.append("Top Justifications:")
    if top_justifications:
        lines.extend([f"- {_ascii_safe(item)}" for item in top_justifications])
    else:
        lines.append("- None")

    lines.append("")
    lines.append("Top Citations:")
    if top_citations:
        for citation in top_citations:
            lines.append(
                f"- [{citation['trial_id']}] {citation['section']}: "
                f"{_ascii_safe(citation['snippet'])} (score={citation['relevance_score']})"
            )
    else:
        lines.append("- None")

    return "\n".join(lines)
