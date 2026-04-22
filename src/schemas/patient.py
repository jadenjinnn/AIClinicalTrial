from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PatientProfile:
    patient_id: str
    age: int
    sex: str
    conditions: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    labs: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.patient_id.strip():
            raise ValueError("patient_id must be non-empty")
        if self.age < 0 or self.age > 130:
            raise ValueError("age must be in [0, 130]")
        if self.sex not in {"male", "female", "other", "unknown"}:
            raise ValueError("sex must be one of: male, female, other, unknown")
        self.conditions = [c.lower() for c in self.conditions]
        self.medications = [m.lower() for m in self.medications]
        self.labs = {k.lower(): float(v) for k, v in self.labs.items()}
