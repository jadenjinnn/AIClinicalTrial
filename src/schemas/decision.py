from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class EvidenceItem:
    source: str
    field: str
    value: str
    rationale: str


@dataclass
class EligibilityDecision:
    patient_id: str
    trial_id: str
    eligible: bool
    confidence: float
    passes: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    missing_data: List[str] = field(default_factory=list)
    evidence: List[EvidenceItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
