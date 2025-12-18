from bson import ObjectId
from datetime import datetime
from typing import Optional

from db.mongodb import get_database


def get_collection():
    """companies 컬렉션 반환"""
    return get_database().companies


# ============================================================
# CRUD 기본 함수
# ============================================================

async def create_company(data: dict) -> str:
    """회사 생성

    Args:
        data: CompanyCreate.model_dump() 결과

    Returns:
        생성된 문서의 ObjectId 문자열
    """
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = datetime.utcnow()
    result = await get_collection().insert_one(data)
    return str(result.inserted_id)


async def get_company(company_id: str) -> Optional[dict]:
    """ID로 회사 조회

    Args:
        company_id: ObjectId 문자열

    Returns:
        회사 문서 또는 None
    """
    if not ObjectId.is_valid(company_id):
        return None
    doc = await get_collection().find_one({"_id": ObjectId(company_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def get_all_companies(skip: int = 0, limit: int = 100) -> list[dict]:
    """전체 회사 목록 조회

    Args:
        skip: 건너뛸 문서 수
        limit: 최대 반환 문서 수

    Returns:
        회사 문서 리스트
    """
    cursor = get_collection().find().skip(skip).limit(limit).sort("created_at", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def update_company(company_id: str, data: dict) -> bool:
    """회사 정보 수정

    Args:
        company_id: ObjectId 문자열
        data: 수정할 필드들

    Returns:
        수정 성공 여부
    """
    if not ObjectId.is_valid(company_id):
        return False
    data["updated_at"] = datetime.utcnow()
    result = await get_collection().update_one(
        {"_id": ObjectId(company_id)},
        {"$set": data}
    )
    return result.modified_count > 0


async def delete_company(company_id: str) -> bool:
    """회사 삭제

    Args:
        company_id: ObjectId 문자열

    Returns:
        삭제 성공 여부
    """
    if not ObjectId.is_valid(company_id):
        return False
    result = await get_collection().delete_one({"_id": ObjectId(company_id)})
    return result.deleted_count > 0


# ============================================================
# 검색/필터 함수
# ============================================================

async def find_by_name(name: str) -> list[dict]:
    """회사명으로 검색 (부분 일치)

    Args:
        name: 검색할 회사명

    Returns:
        회사 문서 리스트
    """
    cursor = get_collection().find({
        "profile_meta.company_name": {"$regex": name, "$options": "i"}
    })
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_by_industry(industry: str) -> list[dict]:
    """산업군으로 검색

    Args:
        industry: 산업군

    Returns:
        회사 문서 리스트
    """
    cursor = get_collection().find({"profile_meta.industry": industry})
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_by_work_mode(work_mode: str) -> list[dict]:
    """근무 형태로 검색

    Args:
        work_mode: "remote", "hybrid", "onsite"

    Returns:
        회사 문서 리스트
    """
    cursor = get_collection().find({
        "company_info_fields.work_environment_expectations.work_mode": work_mode
    })
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_by_tech_stack(tech: str) -> list[dict]:
    """특정 기술 스택 사용 회사 검색

    Args:
        tech: "Python", "Kubernetes", "AWS" 등

    Returns:
        회사 문서 리스트
    """
    query = {
        "$or": [
            {"company_info_fields.technical_environment.stack.languages": {"$regex": tech, "$options": "i"}},
            {"company_info_fields.technical_environment.stack.frameworks": {"$regex": tech, "$options": "i"}},
            {"company_info_fields.technical_environment.stack.data": {"$regex": tech, "$options": "i"}},
            {"company_info_fields.technical_environment.stack.infra_cloud": {"$regex": tech, "$options": "i"}},
            {"company_info_fields.technical_environment.stack.ops_tools": {"$regex": tech, "$options": "i"}},
        ]
    }
    cursor = get_collection().find(query)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_by_min_score(axis: str, min_score: int) -> list[dict]:
    """특정 점수 축에서 N점 이상인 회사 검색

    Args:
        axis: "technical_fit_company", "collaboration_style_company" 등
        min_score: 최소 점수 (0-4)

    Returns:
        회사 문서 리스트 (점수 내림차순)
    """
    query = {f"scoring_axes.{axis}.score": {"$gte": min_score}}
    cursor = get_collection().find(query).sort(f"scoring_axes.{axis}.score", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def search_companies(
    name: Optional[str] = None,
    industry: Optional[str] = None,
    work_mode: Optional[str] = None,
    tech: Optional[str] = None,
    min_technical_score: Optional[int] = None,
    min_collaboration_score: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> list[dict]:
    """복합 필터 검색

    Args:
        name: 회사명 필터
        industry: 산업군 필터
        work_mode: 근무 형태 필터
        tech: 기술 스택 필터
        min_technical_score: 최소 기술 점수
        min_collaboration_score: 최소 협업 점수
        skip: 건너뛸 문서 수
        limit: 최대 반환 문서 수

    Returns:
        회사 문서 리스트
    """
    query = {}

    if name:
        query["profile_meta.company_name"] = {"$regex": name, "$options": "i"}

    if industry:
        query["profile_meta.industry"] = industry

    if work_mode:
        query["company_info_fields.work_environment_expectations.work_mode"] = work_mode

    if tech:
        query["$or"] = [
            {"company_info_fields.technical_environment.stack.languages": {"$regex": tech, "$options": "i"}},
            {"company_info_fields.technical_environment.stack.frameworks": {"$regex": tech, "$options": "i"}},
            {"company_info_fields.technical_environment.stack.data": {"$regex": tech, "$options": "i"}},
            {"company_info_fields.technical_environment.stack.infra_cloud": {"$regex": tech, "$options": "i"}},
            {"company_info_fields.technical_environment.stack.ops_tools": {"$regex": tech, "$options": "i"}},
        ]

    if min_technical_score:
        query["scoring_axes.technical_fit_company.score"] = {"$gte": min_technical_score}

    if min_collaboration_score:
        query["scoring_axes.collaboration_style_company.score"] = {"$gte": min_collaboration_score}

    cursor = get_collection().find(query).skip(skip).limit(limit).sort("created_at", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


# ============================================================
# 매칭용 함수
# ============================================================

async def get_scoring_axes(company_id: str) -> Optional[dict]:
    """매칭 계산용 - scoring_axes만 조회 (projection)

    Args:
        company_id: ObjectId 문자열

    Returns:
        scoring_axes 데이터 또는 None
    """
    if not ObjectId.is_valid(company_id):
        return None
    doc = await get_collection().find_one(
        {"_id": ObjectId(company_id)},
        {"scoring_axes": 1, "profile_meta.company_name": 1}
    )
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def get_companies_for_matching(
    work_mode: Optional[str] = None,
    min_score: int = 0,
    limit: int = 50
) -> list[dict]:
    """지원자와 매칭할 회사 목록 조회 (매칭에 필요한 필드만)

    Args:
        work_mode: 근무 형태 필터
        min_score: 최소 기술 점수
        limit: 최대 반환 문서 수

    Returns:
        매칭용 회사 데이터 리스트
    """
    query = {}
    if work_mode:
        query["company_info_fields.work_environment_expectations.work_mode"] = work_mode
    if min_score > 0:
        query["scoring_axes.technical_fit_company.score"] = {"$gte": min_score}

    cursor = get_collection().find(
        query,
        {
            "profile_meta": 1,
            "scoring_axes": 1,
            "company_info_fields.technical_environment.stack": 1,
            "company_info_fields.work_environment_expectations": 1,
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

    await collection.create_index("profile_meta.company_name")
    await collection.create_index("profile_meta.industry")
    await collection.create_index("company_info_fields.work_environment_expectations.work_mode")
    await collection.create_index("scoring_axes.technical_fit_company.score")
    await collection.create_index("scoring_axes.collaboration_style_company.score")
    await collection.create_index("scoring_axes.ownership_company.score")
    await collection.create_index("company_info_fields.technical_environment.stack.languages")
    await collection.create_index("created_at")