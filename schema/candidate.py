from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# ============================================================
# 공통 모델
# ============================================================

class Evidence(BaseModel):
    """근거 자료"""
    doc_id: str  # "resume", "essay", "portfolio"
    line_refs: list[str] = []
    quote: str


class SourceDoc(BaseModel):
    """원본 문서 정보"""
    doc_id: str
    filename: str

# 1. Enum 정의 (타입 안정성 확보)
# 경력과
# class SeniorityLevel(str, Enum):
#     JUNIOR = "junior"
#     MID = "mid"
#     SENIOR = "senior"
#     LEAD = "lead"
#
# class ScoreConfidence(str, Enum):
#     HIGH = "high"
#     MEDIUM = "medium"
#     LOW = "low"


# ============================================================
# profile_meta
# ============================================================

class ProfileMeta(BaseModel):
    """지원자 기본 프로필 메타정보"""
    candidate_name: str
    primary_role: str  # "backend", "frontend", "fullstack", etc.
    target_role: str
    seniority: str  # "junior", "mid", "senior", "lead"
    years_experience: int
    source_docs: list[SourceDoc] = []


# ============================================================
# user_info_fields 하위 모델들
# ============================================================

class BasicProfile(BaseModel):
    """기본 프로필 요약"""
    summary: str
    evidence: list[Evidence] = []


class TechStack(BaseModel):
    """기술 스택"""
    languages: list[str] = []
    frameworks: list[str] = []
    data: list[str] = []  # DB 관련
    infra_cloud: list[str] = []
    ops_tools: list[str] = []


class TechnicalCapability(BaseModel):
    """기술 역량"""
    stack: TechStack
    ops_deploy_experience: str = "unknown"  # "yes", "no", "unknown"
    scale_traffic_platform_mentioned: str = "unknown"
    evidence: list[Evidence] = []


class OutcomeMetric(BaseModel):
    """프로젝트 성과 지표"""
    metric: str
    before: Optional[str] = None
    after: Optional[str] = None
    notes: Optional[str] = None


class Project(BaseModel):
    """프로젝트 경험"""
    name: str
    timeframe: Optional[str] = None
    context_problem: Optional[str] = None
    responsibility_scope: Optional[str] = None
    technical_decisions: list[str] = []
    outcomes_metrics: list[OutcomeMetric] = []
    evidence: list[Evidence] = []


class ProjectBehaviorData(BaseModel):
    """프로젝트 행동 데이터"""
    projects: list[Project] = []


class CollaborationExperience(BaseModel):
    """협업 경험"""
    summary: str
    code_review_participation: str = "unknown"  # "yes", "no", "unknown"
    documentation_communication: str = "unknown"  # "high", "medium", "low", "unknown"
    cross_functional_collaboration: str = "unknown"  # "frequent", "occasional", "rare", "unknown"
    conflict_coordination_experience: str = "unknown"  # "mentioned", "not_mentioned", "unknown"
    evidence: list[Evidence] = []


class GrowthTendency(BaseModel):
    """성장 성향"""
    summary: str
    learning_mode: str = "unknown"  # "self_directed", "structured", "mixed", "unknown"
    new_tech_adoption: str = "unknown"  # "high", "medium", "low", "unknown"
    feedback_receptiveness: str = "unknown"  # "high", "medium", "low", "unknown"
    evidence: list[Evidence] = []


class WorkEnvironmentSignals(BaseModel):
    """근무 환경 선호 신호"""
    summary: str
    work_mode_preference: str = "unknown"  # "remote", "hybrid", "office", "unknown"
    work_life_balance_vs_immersion: str = "unknown"  # "balanced", "wlb_focused", "immersion_focused", "unknown"
    pace_intensity_preference: str = "unknown"  # "high", "moderate", "low", "unknown"
    evidence: list[Evidence] = []


class VerificationNeededAreas(BaseModel):
    """추가 확인 필요 영역"""
    missing_or_unmentioned: list[str] = []
    needs_followup_questions: list[str] = []


class UserInfoFields(BaseModel):
    """지원자 상세 정보"""
    basic_profile: BasicProfile
    technical_capability: TechnicalCapability
    project_behavior_data: ProjectBehaviorData
    collaboration_experience: CollaborationExperience
    growth_tendency: GrowthTendency
    work_environment_signals: WorkEnvironmentSignals
    verification_needed_areas: Optional[VerificationNeededAreas] = None


# ============================================================
# scoring_axes 하위 모델들
# ============================================================

class ScoringPolicy(BaseModel):
    """점수 정책"""
    scale: str = "0-4"
    meaning: dict[str, str] = {
        "0": "no explicit signal",
        "1": "weak/indirect mention",
        "2": "some evidence (limited scope)",
        "3": "clear evidence (multiple instances or concrete responsibilities)",
        "4": "strong evidence (clear ownership + concrete outcomes/metrics where applicable)"
    }
    unknown_handling: str = "If evidence is missing, score must be 0 and confidence must be low."


class TechnicalFitSubsignals(BaseModel):
    """기술 적합도 세부 신호"""
    languages_frameworks_depth: int = Field(ge=0, le=4, default=0)
    infra_cloud_exposure: int = Field(ge=0, le=4, default=0)
    ops_deploy_monitoring_exposure: int = Field(ge=0, le=4, default=0)
    scale_platform_exposure: int = Field(ge=0, le=4, default=0)


class ExecutionStyleSubsignals(BaseModel):
    """실행 스타일 세부 신호"""
    speed_vs_stability: str = "unknown"  # "speed", "stability", "balanced", "unknown"
    prototype_vs_structure: str = "unknown"  # "prototype", "structure", "balanced", "unknown"
    business_impact_vs_tech_quality: str = "unknown"  # "business", "tech", "balanced", "unknown"


class CollaborationStyleSubsignals(BaseModel):
    """협업 스타일 세부 신호"""
    code_review: int = Field(ge=0, le=4, default=0)
    documentation: int = Field(ge=0, le=4, default=0)
    cross_functional: int = Field(ge=0, le=4, default=0)


class OwnershipSubsignals(BaseModel):
    """오너십 세부 신호"""
    problem_definition_involvement: int = Field(ge=0, le=4, default=0)
    decision_making: int = Field(ge=0, le=4, default=0)
    role_self_positioning: str = "unknown"  # "lead", "senior", "mid", "junior", "unknown"


class GrowthOrientationSubsignals(BaseModel):
    """성장 지향성 세부 신호"""
    new_tech_adoption: int = Field(ge=0, le=4, default=0)
    self_directed_learning: int = Field(ge=0, le=4, default=0)
    feedback_loop: int = Field(ge=0, le=4, default=0)


class WorkExpectationSubsignals(BaseModel):
    """근무 기대 세부 신호"""
    pace_intensity_preference: int = Field(ge=0, le=4, default=0)
    wlb_vs_immersion_preference: int = Field(ge=0, le=4, default=0)
    responsibility_density_signals: int = Field(ge=0, le=4, default=0)


class ScoringAxis(BaseModel):
    """점수 축 기본 모델"""
    score: int = Field(ge=0, le=4)
    summary: str
    confidence: str  # "high", "medium", "low"
    evidence: list[Evidence] = []


class TechnicalFitScore(ScoringAxis):
    """기술 적합도 점수"""
    subsignals: TechnicalFitSubsignals = TechnicalFitSubsignals()


class ExecutionStyleScore(ScoringAxis):
    """실행 스타일 점수"""
    subsignals: ExecutionStyleSubsignals = ExecutionStyleSubsignals()


class CollaborationStyleScore(ScoringAxis):
    """협업 스타일 점수"""
    subsignals: CollaborationStyleSubsignals = CollaborationStyleSubsignals()


class OwnershipScore(ScoringAxis):
    """오너십 점수"""
    subsignals: OwnershipSubsignals = OwnershipSubsignals()


class GrowthOrientationScore(ScoringAxis):
    """성장 지향성 점수"""
    subsignals: GrowthOrientationSubsignals = GrowthOrientationSubsignals()


class WorkExpectationScore(ScoringAxis):
    """근무 기대 점수"""
    subsignals: WorkExpectationSubsignals = WorkExpectationSubsignals()


class ScoringAxes(BaseModel):
    """전체 점수 축"""
    scoring_policy: Optional[ScoringPolicy] = ScoringPolicy()
    technical_fit_user: TechnicalFitScore
    execution_style_user: ExecutionStyleScore
    collaboration_style_user: CollaborationStyleScore
    ownership_user: OwnershipScore
    growth_orientation_user: GrowthOrientationScore
    work_expectation_user: WorkExpectationScore


# ============================================================
# extraction_quality
# ============================================================

class ExtractionQuality(BaseModel):
    """추출 품질 메타데이터"""
    unknown_policy_applied: str = "yes"
    notes: Optional[str] = None


# ============================================================
# 메인 Candidate 모델
# ============================================================

class CandidateBase(BaseModel):
    """Candidate 기본 모델"""
    schema_version: str = "1.0"
    profile_meta: ProfileMeta
    user_info_fields: UserInfoFields
    scoring_axes: ScoringAxes
    extraction_quality: Optional[ExtractionQuality] = None


class CandidateCreate(CandidateBase):
    """Candidate 생성용 모델 (API 요청)"""
    pass


class CandidateInDB(CandidateBase):
    """MongoDB에 저장된 Candidate 모델"""
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class CandidateResponse(CandidateBase):
    """API 응답용 Candidate 모델"""
    id: str
    created_at: datetime
    updated_at: datetime