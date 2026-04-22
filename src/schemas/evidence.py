from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class Citation:
    source: str
    trial_id: str
    trial_title: str
    section: str
    snippet: str
    relevance_score: float


@dataclass
class RetrievalEvidencePack:
    query: str
    citations: List[Citation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
