from pydantic import BaseModel, Field
from typing import Optional


# ============================================================
# Meta
# ============================================================

class MatchingMeta(BaseModel):
    generated_at: str
    scoring_version: str = "alignment-v1"
    axes_used: list[str] = []
    notes: str = ""


# ============================================================
# Inputs (참조 정보)
# ============================================================

class SourceDocRef(BaseModel):
    doc_id: str
    filename: str = "unknown"


class ProfileRef(BaseModel):
    profile_id: str
    source_docs: list[SourceDocRef] = []


class MatchingInputs(BaseModel):
    company_profile_ref: ProfileRef
    developer_profile_ref: ProfileRef


# ============================================================
# Evidence References
# ============================================================

class EvidenceRef(BaseModel):
    path: str
    quote: str


class AxisEvidenceRefs(BaseModel):
    company: list[EvidenceRef] = []
    developer: list[EvidenceRef] = []


# ============================================================
# Axis Rationale
# ============================================================

class AxisRationale(BaseModel):
    company_signals: list[str] = []
    developer_signals: list[str] = []
    comparison_notes: str = ""


# ============================================================
# Axis Alignment (각 축별 정합성)
# ============================================================

class AxisAlignment(BaseModel):
    status: str = "unknown"  # "aligned", "partial", "misaligned", "unknown"
    axis_score: int | str = "unknown"  # 0-100 또는 "unknown"
    summary: str = ""
    rationale: AxisRationale
    evidence_refs: AxisEvidenceRefs
    followup_questions: list[str] = []


class AxisAlignments(BaseModel):
    technical_fit: Optional[AxisAlignment] = None
    execution_style: Optional[AxisAlignment] = None
    collaboration_style: Optional[AxisAlignment] = None
    growth_learning_orientation: Optional[AxisAlignment] = None
    product_user_impact_orientation: Optional[AxisAlignment] = None
    ops_quality_responsibility: Optional[AxisAlignment] = None
    ownership: Optional[AxisAlignment] = None
    work_expectation: Optional[AxisAlignment] = None


# ============================================================
# Overall Scoring
# ============================================================

class ScoringWeights(BaseModel):
    technical_fit: float = 1.0
    execution_style: float = 1.0
    collaboration_style: float = 1.0
    growth_learning_orientation: float = 1.0
    product_user_impact_orientation: float = 1.0
    ops_quality_responsibility: float = 1.0


class ScoringDetails(BaseModel):
    weights: ScoringWeights
    excluded_axes: list[str] = []
    calculation_notes: str = ""


class OverallResult(BaseModel):
    match_score: int = Field(ge=0, le=100)
    score_band: str = "unknown"  # "high", "medium", "low"
    confidence: float = Field(ge=0.0, le=1.0)
    scoring: ScoringDetails
    high_alignment_axes: list[str] = []
    risk_or_mismatch_axes: list[str] = []
    unknown_axes: list[str] = []
    overall_notes: str = ""


# ============================================================
# Main Schema
# ============================================================

class MatchingResultCreate(BaseModel):
    schema_version: str = "1.0"
    meta: MatchingMeta
    inputs: MatchingInputs
    axis_alignments: AxisAlignments
    overall: OverallResult


class MatchingResultResponse(MatchingResultCreate):
    id: str