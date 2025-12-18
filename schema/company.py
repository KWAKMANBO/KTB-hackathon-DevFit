from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


# ============================================================
# Evidence 관련
# ============================================================

class Evidence(BaseModel):
    doc_id: str
    line_refs: list[str] = ["unknown"]
    quote: str


# ============================================================
# Profile Meta
# ============================================================

class SourceDoc(BaseModel):
    doc_id: str
    filename: str = "unknown"
    url: str = "unknown"


class ProfileMeta(BaseModel):
    company_name: str
    industry: str = "unknown"
    primary_domain: str = "unknown"
    analyzed_scope: str = "company"
    analyzed_date: str
    source_docs: list[SourceDoc] = []


# ============================================================
# Company Info Fields
# ============================================================

class BasicProfile(BaseModel):
    summary: str
    evidence: list[Evidence] = []


class TechStack(BaseModel):
    languages: list[str] = []
    frameworks: list[str] = []
    data: list[str] = []
    infra_cloud: list[str] = []
    ops_tools: list[str] = []


class TechnicalEnvironment(BaseModel):
    stack: TechStack
    ops_deploy_experience_required_or_mentioned: str = "unknown"
    scale_traffic_platform_mentioned: str = "unknown"
    evidence: list[Evidence] = []


class RoleAndHiringSignals(BaseModel):
    hiring_summary: str = "unknown"
    open_roles_mentioned: list[str] = []
    employment_type: str = "unknown"
    location: str = "unknown"
    remote_hybrid_onsite: str = "unknown"
    required_experience: str = "unknown"
    evidence: list[Evidence] = []


class ExecutionCultureSignals(BaseModel):
    summary: str = "unknown"
    speed_vs_stability: str = "unknown"
    prototype_vs_structure: str = "unknown"
    business_impact_vs_tech_quality: str = "unknown"
    evidence: list[Evidence] = []


class CollaborationCultureSignals(BaseModel):
    summary: str = "unknown"
    code_review_culture: str = "unknown"
    documentation_culture: str = "unknown"
    cross_functional_collaboration: str = "unknown"
    decision_making_process: str = "unknown"
    evidence: list[Evidence] = []


class OwnershipExpectationSignals(BaseModel):
    summary: str = "unknown"
    problem_definition_expected: str = "unknown"
    decision_making_expected: str = "unknown"
    role_positioning: str = "unknown"
    evidence: list[Evidence] = []


class GrowthLearningCultureSignals(BaseModel):
    summary: str = "unknown"
    learning_support: str = "unknown"
    new_tech_adoption: str = "unknown"
    feedback_culture: str = "unknown"
    evidence: list[Evidence] = []


class WorkEnvironmentExpectations(BaseModel):
    summary: str = "unknown"
    work_mode: str = "unknown"
    wlb_vs_immersion: str = "unknown"
    pace_intensity: str = "unknown"
    oncall_or_shift: str = "unknown"
    overtime_or_night_work: str = "unknown"
    benefits_or_perks: list[str] = []
    evidence: list[Evidence] = []


class VerificationNeededAreas(BaseModel):
    missing_or_unmentioned: list[str] = []
    needs_followup_questions: list[str] = []


class CompanyInfoFields(BaseModel):
    basic_profile: BasicProfile
    technical_environment: TechnicalEnvironment
    role_and_hiring_signals: RoleAndHiringSignals
    execution_culture_signals: ExecutionCultureSignals
    collaboration_culture_signals: CollaborationCultureSignals
    ownership_expectation_signals: OwnershipExpectationSignals
    growth_learning_culture_signals: GrowthLearningCultureSignals
    work_environment_expectations: WorkEnvironmentExpectations
    verification_needed_areas: VerificationNeededAreas


# ============================================================
# Scoring Axes
# ============================================================

class ScoringPolicyMeaning(BaseModel):
    zero: str = Field(alias="0", default="no explicit signal")
    one: str = Field(alias="1", default="weak/indirect mention")
    two: str = Field(alias="2", default="some evidence (limited scope)")
    three: str = Field(alias="3", default="clear evidence (multiple instances or concrete practices)")
    four: str = Field(alias="4", default="strong evidence (clear ownership + concrete policies/practices)")

    class Config:
        populate_by_name = True


class ScoringPolicy(BaseModel):
    scale: str = "0-4"
    meaning: ScoringPolicyMeaning
    unknown_handling: str = "If evidence is missing, score must be 0 and confidence must be low."


class TechnicalFitSubsignals(BaseModel):
    languages_frameworks_depth: int = 0
    infra_cloud_exposure: int = 0
    ops_deploy_monitoring_exposure: int = 0
    scale_platform_exposure: int = 0


class TechnicalFitCompany(BaseModel):
    score: int = Field(ge=0, le=4)
    summary: str
    confidence: str = "low"
    evidence: list[Evidence] = []
    subsignals: TechnicalFitSubsignals


class ExecutionStyleSubsignals(BaseModel):
    speed_vs_stability: str = "unknown"
    prototype_vs_structure: str = "unknown"
    business_impact_vs_tech_quality: str = "unknown"


class ExecutionStyleCompany(BaseModel):
    score: int = Field(ge=0, le=4)
    summary: str
    confidence: str = "low"
    evidence: list[Evidence] = []
    subsignals: ExecutionStyleSubsignals


class CollaborationStyleSubsignals(BaseModel):
    code_review: int = 0
    documentation: int = 0
    cross_functional: int = 0


class CollaborationStyleCompany(BaseModel):
    score: int = Field(ge=0, le=4)
    summary: str
    confidence: str = "low"
    evidence: list[Evidence] = []
    subsignals: CollaborationStyleSubsignals


class OwnershipSubsignals(BaseModel):
    problem_definition_involvement: int = 0
    decision_making: int = 0
    role_self_positioning: str = "unknown"


class OwnershipCompany(BaseModel):
    score: int = Field(ge=0, le=4)
    summary: str
    confidence: str = "low"
    evidence: list[Evidence] = []
    subsignals: OwnershipSubsignals


class GrowthOrientationSubsignals(BaseModel):
    new_tech_adoption: int = 0
    self_directed_learning: int = 0
    feedback_loop: int = 0


class GrowthOrientationCompany(BaseModel):
    score: int = Field(ge=0, le=4)
    summary: str
    confidence: str = "low"
    evidence: list[Evidence] = []
    subsignals: GrowthOrientationSubsignals


class WorkExpectationSubsignals(BaseModel):
    pace_intensity_preference: int = 0
    wlb_vs_immersion_preference: int = 0
    responsibility_density_signals: int = 0


class WorkExpectationCompany(BaseModel):
    score: int = Field(ge=0, le=4)
    summary: str
    confidence: str = "low"
    evidence: list[Evidence] = []
    subsignals: WorkExpectationSubsignals


class ScoringAxes(BaseModel):
    scoring_policy: ScoringPolicy
    technical_fit_company: TechnicalFitCompany
    execution_style_company: ExecutionStyleCompany
    collaboration_style_company: CollaborationStyleCompany
    ownership_company: OwnershipCompany
    growth_orientation_company: GrowthOrientationCompany
    work_expectation_company: WorkExpectationCompany


# ============================================================
# Extraction Quality
# ============================================================

class ExtractionQuality(BaseModel):
    unknown_policy_applied: str = "yes"
    notes: str = ""


# ============================================================
# Main Schema
# ============================================================

class CompanyCreate(BaseModel):
    schema_version: str = "1.0"
    profile_meta: ProfileMeta
    company_info_fields: CompanyInfoFields
    scoring_axes: ScoringAxes
    extraction_quality: ExtractionQuality


class CompanyResponse(CompanyCreate):
    id: str