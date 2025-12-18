from bson import ObjectId
from datetime import datetime
from typing import Optional

from db.mongodb import get_database


def get_collection():
    """candidates 컬렉션 반환"""
    return get_database().candidates


# ============================================================
# CRUD 기본 함수
# ============================================================

async def create_candidate(data: dict) -> str:
    """지원자 생성

    Args:
        data: CandidateCreate.model_dump() 결과

    Returns:
        생성된 문서의 ObjectId 문자열
    """
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = datetime.utcnow()
    result = await get_collection().insert_one(data)
    return str(result.inserted_id)


async def get_candidate(candidate_id: str) -> Optional[dict]:
    """ID로 지원자 조회

    Args:
        candidate_id: ObjectId 문자열

    Returns:
        지원자 문서 또는 None
    """
    if not ObjectId.is_valid(candidate_id):
        return None
    doc = await get_collection().find_one({"_id": ObjectId(candidate_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def get_all_candidates(skip: int = 0, limit: int = 100) -> list[dict]:
    """전체 지원자 목록 조회

    Args:
        skip: 건너뛸 문서 수
        limit: 최대 반환 문서 수

    Returns:
        지원자 문서 리스트
    """
    cursor = get_collection().find().skip(skip).limit(limit).sort("created_at", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def update_candidate(candidate_id: str, data: dict) -> bool:
    """지원자 정보 수정

    Args:
        candidate_id: ObjectId 문자열
        data: 수정할 필드들

    Returns:
        수정 성공 여부
    """
    if not ObjectId.is_valid(candidate_id):
        return False
    data["updated_at"] = datetime.utcnow()
    result = await get_collection().update_one(
        {"_id": ObjectId(candidate_id)},
        {"$set": data}
    )
    return result.modified_count > 0


async def delete_candidate(candidate_id: str) -> bool:
    """지원자 삭제

    Args:
        candidate_id: ObjectId 문자열

    Returns:
        삭제 성공 여부
    """
    if not ObjectId.is_valid(candidate_id):
        return False
    result = await get_collection().delete_one({"_id": ObjectId(candidate_id)})
    return result.deleted_count > 0


# ============================================================
# 검색/필터 함수
# ============================================================

async def find_by_name(name: str) -> list[dict]:
    """이름으로 검색 (부분 일치)

    Args:
        name: 검색할 이름

    Returns:
        지원자 문서 리스트
    """
    cursor = get_collection().find({
        "profile_meta.candidate_name": {"$regex": name, "$options": "i"}
    })
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_by_role(role: str) -> list[dict]:
    """역할로 검색

    Args:
        role: "backend", "frontend", "fullstack" 등

    Returns:
        지원자 문서 리스트
    """
    cursor = get_collection().find({"profile_meta.primary_role": role})
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_by_seniority(seniority: str) -> list[dict]:
    """경력 레벨로 검색

    Args:
        seniority: "junior", "mid", "senior", "lead"

    Returns:
        지원자 문서 리스트
    """
    cursor = get_collection().find({"profile_meta.seniority": seniority})
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_by_min_score(axis: str, min_score: int) -> list[dict]:
    """특정 점수 축에서 N점 이상인 지원자 검색

    Args:
        axis: "technical_fit_user", "collaboration_style_user" 등
        min_score: 최소 점수 (0-4)

    Returns:
        지원자 문서 리스트 (점수 내림차순)
    """
    query = {f"scoring_axes.{axis}.score": {"$gte": min_score}}
    cursor = get_collection().find(query).sort(f"scoring_axes.{axis}.score", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_by_tech_stack(tech: str) -> list[dict]:
    """특정 기술 스택 보유자 검색

    Args:
        tech: "Java", "Kubernetes", "React" 등

    Returns:
        지원자 문서 리스트
    """
    query = {
        "$or": [
            {"user_info_fields.technical_capability.stack.languages": {"$regex": tech, "$options": "i"}},
            {"user_info_fields.technical_capability.stack.frameworks": {"$regex": tech, "$options": "i"}},
            {"user_info_fields.technical_capability.stack.data": {"$regex": tech, "$options": "i"}},
            {"user_info_fields.technical_capability.stack.infra_cloud": {"$regex": tech, "$options": "i"}},
            {"user_info_fields.technical_capability.stack.ops_tools": {"$regex": tech, "$options": "i"}},
        ]
    }
    cursor = get_collection().find(query)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def search_candidates(
    role: Optional[str] = None,
    seniority: Optional[str] = None,
    min_years: Optional[int] = None,
    tech: Optional[str] = None,
    min_technical_score: Optional[int] = None,
    min_collaboration_score: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> list[dict]:
    """복합 필터 검색

    Args:
        role: 역할 필터
        seniority: 경력 레벨 필터
        min_years: 최소 경력 연수
        tech: 기술 스택 필터
        min_technical_score: 최소 기술 적합도 점수
        min_collaboration_score: 최소 협업 스타일 점수
        skip: 건너뛸 문서 수
        limit: 최대 반환 문서 수

    Returns:
        지원자 문서 리스트
    """
    query = {}

    if role:
        query["profile_meta.primary_role"] = role

    if seniority:
        query["profile_meta.seniority"] = seniority

    if min_years:
        query["profile_meta.years_experience"] = {"$gte": min_years}

    if tech:
        query["$or"] = [
            {"user_info_fields.technical_capability.stack.languages": {"$regex": tech, "$options": "i"}},
            {"user_info_fields.technical_capability.stack.frameworks": {"$regex": tech, "$options": "i"}},
            {"user_info_fields.technical_capability.stack.data": {"$regex": tech, "$options": "i"}},
            {"user_info_fields.technical_capability.stack.infra_cloud": {"$regex": tech, "$options": "i"}},
            {"user_info_fields.technical_capability.stack.ops_tools": {"$regex": tech, "$options": "i"}},
        ]

    if min_technical_score:
        query["scoring_axes.technical_fit_user.score"] = {"$gte": min_technical_score}

    if min_collaboration_score:
        query["scoring_axes.collaboration_style_user.score"] = {"$gte": min_collaboration_score}

    cursor = get_collection().find(query).skip(skip).limit(limit).sort("created_at", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


# ============================================================
# 매칭용 함수
# ============================================================

async def get_scoring_axes(candidate_id: str) -> Optional[dict]:
    """매칭 계산용 - scoring_axes만 조회 (projection)

    Args:
        candidate_id: ObjectId 문자열

    Returns:
        scoring_axes 데이터 또는 None
    """
    if not ObjectId.is_valid(candidate_id):
        return None
    doc = await get_collection().find_one(
        {"_id": ObjectId(candidate_id)},
        {"scoring_axes": 1, "profile_meta.candidate_name": 1}
    )
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def get_candidates_for_matching(
    role: Optional[str] = None,
    min_score: int = 0,
    limit: int = 50
) -> list[dict]:
    """회사와 매칭할 지원자 목록 조회 (매칭에 필요한 필드만)

    Args:
        role: 역할 필터
        min_score: 최소 기술 점수
        limit: 최대 반환 문서 수

    Returns:
        매칭용 지원자 데이터 리스트
    """
    query = {}
    if role:
        query["profile_meta.primary_role"] = role
    if min_score > 0:
        query["scoring_axes.technical_fit_user.score"] = {"$gte": min_score}

    cursor = get_collection().find(
        query,
        {
            "profile_meta": 1,
            "scoring_axes": 1,
            "user_info_fields.technical_capability.stack": 1,
            "user_info_fields.work_environment_signals": 1,
        }
    ).limit(limit)

    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


# ============================================================
# 인덱스 설정
# ============================================================

async def create_indexes():
    """컬렉션 인덱스 생성 - 앱 시작 시 호출"""
    collection = get_collection()

    await collection.create_index("profile_meta.candidate_name")
    await collection.create_index("profile_meta.primary_role")
    await collection.create_index("profile_meta.seniority")
    await collection.create_index("profile_meta.years_experience")
    await collection.create_index("scoring_axes.technical_fit_user.score")
    await collection.create_index("scoring_axes.collaboration_style_user.score")
    await collection.create_index("scoring_axes.ownership_user.score")
    await collection.create_index("user_info_fields.technical_capability.stack.languages")
    await collection.create_index("created_at")