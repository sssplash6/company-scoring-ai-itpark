from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Evidence:
    source_url: str
    snippet: str
    source_type: str
    retrieved_at: datetime
    confidence: float


@dataclass
class Feature:
    name: str
    value: Any
    confidence: float
    evidence: List[Evidence] = field(default_factory=list)


@dataclass
class CriterionScore:
    criterion_id: str
    name: str
    category: str
    score: float
    max_score: float
    weight: float
    rationale: str


@dataclass
class Scorecard:
    overall_score: float
    coverage: float
    confidence: float
    category_scores: Dict[str, float]
    criteria: List[CriterionScore]
    flags: List[str]


@dataclass
class CompanyResult:
    company_name: str
    website: Optional[str]
    features: Dict[str, Feature]
    scorecard: Scorecard
    run_id: str
