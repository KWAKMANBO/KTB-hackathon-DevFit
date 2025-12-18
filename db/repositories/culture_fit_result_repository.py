from bson import ObjectId
from datetime import datetime
from typing import Optional

from db.mongodb import get_database


def get_collection():
    """matching_results 컬렉션 반환"""
    return get_database().culture_fit_results


# ============================================================
# CRUD 기본 함수
# ============================================================

async def create_matching_result(data: dict) -> str:
    """매칭 결과 생성

    Args:
        data: MatchingResultCreate.model_dump() 결과

    Returns:
        생성된 문서의 ObjectId 문자열
    """
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = datetime.utcnow()
    result = await get_collection().insert_one(data)
    return str(result.inserted_id)


async def get_matching_result(result_id: str) -> Optional[dict]:
    """ID로 매칭 결과 조회

    Args:
        result_id: ObjectId 문자열

    Returns:
        매칭 결과 문서 또는 None
    """
    if not ObjectId.is_valid(result_id):
        return None
    doc = await get_collection().find_one({"_id": ObjectId(result_id)})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def get_all_matching_results(skip: int = 0, limit: int = 100) -> list[dict]:
    """전체 매칭 결과 목록 조회

    Args:
        skip: 건너뛸 문서 수
        limit: 최대 반환 문서 수

    Returns:
        매칭 결과 문서 리스트
    """
    cursor = get_collection().find().skip(skip).limit(limit).sort("created_at", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def update_matching_result(result_id: str, data: dict) -> bool:
    """매칭 결과 수정

    Args:
        result_id: ObjectId 문자열
        data: 수정할 필드들

    Returns:
        수정 성공 여부
    """
    if not ObjectId.is_valid(result_id):
        return False
    data["updated_at"] = datetime.utcnow()
    result = await get_collection().update_one(
        {"_id": ObjectId(result_id)},
        {"$set": data}
    )
    return result.modified_count > 0


async def delete_matching_result(result_id: str) -> bool:
    """매칭 결과 삭제

    Args:
        result_id: ObjectId 문자열

    Returns:
        삭제 성공 여부
    """
    if not ObjectId.is_valid(result_id):
        return False
    result = await get_collection().delete_one({"_id": ObjectId(result_id)})
    return result.deleted_count > 0


# ============================================================
# 검색/필터 함수
# ============================================================

async def find_by_company(company_profile_id: str) -> list[dict]:
    """회사 프로필 ID로 매칭 결과 검색

    Args:
        company_profile_id: 회사 프로필 ID

    Returns:
        매칭 결과 문서 리스트
    """
    cursor = get_collection().find({
        "inputs.company_profile_ref.profile_id": company_profile_id
    }).sort("overall.match_score", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_by_developer(developer_profile_id: str) -> list[dict]:
    """개발자 프로필 ID로 매칭 결과 검색

    Args:
        developer_profile_id: 개발자 프로필 ID

    Returns:
        매칭 결과 문서 리스트
    """
    cursor = get_collection().find({
        "inputs.developer_profile_ref.profile_id": developer_profile_id
    }).sort("overall.match_score", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_by_company_and_developer(
    company_profile_id: str,
    developer_profile_id: str
) -> Optional[dict]:
    """회사-개발자 쌍으로 매칭 결과 검색

    Args:
        company_profile_id: 회사 프로필 ID
        developer_profile_id: 개발자 프로필 ID

    Returns:
        매칭 결과 문서 또는 None
    """
    doc = await get_collection().find_one({
        "inputs.company_profile_ref.profile_id": company_profile_id,
        "inputs.developer_profile_ref.profile_id": developer_profile_id
    })
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


async def find_by_score_band(score_band: str) -> list[dict]:
    """점수 밴드로 검색

    Args:
        score_band: "high", "medium", "low"

    Returns:
        매칭 결과 문서 리스트
    """
    cursor = get_collection().find({
        "overall.score_band": score_band
    }).sort("overall.match_score", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_by_min_score(min_score: int) -> list[dict]:
    """최소 점수 이상인 매칭 결과 검색

    Args:
        min_score: 최소 매칭 점수 (0-100)

    Returns:
        매칭 결과 문서 리스트 (점수 내림차순)
    """
    cursor = get_collection().find({
        "overall.match_score": {"$gte": min_score}
    }).sort("overall.match_score", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_high_alignment(axis: str) -> list[dict]:
    """특정 축에서 높은 정합성을 보이는 매칭 결과 검색

    Args:
        axis: "technical_fit", "collaboration_style" 등

    Returns:
        매칭 결과 문서 리스트
    """
    cursor = get_collection().find({
        "overall.high_alignment_axes": axis
    }).sort("overall.match_score", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def find_risk_axes(axis: str) -> list[dict]:
    """특정 축에서 리스크가 있는 매칭 결과 검색

    Args:
        axis: "execution_style", "collaboration_style" 등

    Returns:
        매칭 결과 문서 리스트
    """
    cursor = get_collection().find({
        "overall.risk_or_mismatch_axes": axis
    }).sort("overall.match_score", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def search_matching_results(
    company_profile_id: Optional[str] = None,
    developer_profile_id: Optional[str] = None,
    score_band: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> list[dict]:
    """복합 필터 검색

    Args:
        company_profile_id: 회사 프로필 ID 필터
        developer_profile_id: 개발자 프로필 ID 필터
        score_band: 점수 밴드 필터
        min_score: 최소 점수 필터
        max_score: 최대 점수 필터
        skip: 건너뛸 문서 수
        limit: 최대 반환 문서 수

    Returns:
        매칭 결과 문서 리스트
    """
    query = {}

    if company_profile_id:
        query["inputs.company_profile_ref.profile_id"] = company_profile_id

    if developer_profile_id:
        query["inputs.developer_profile_ref.profile_id"] = developer_profile_id

    if score_band:
        query["overall.score_band"] = score_band

    if min_score is not None or max_score is not None:
        query["overall.match_score"] = {}
        if min_score is not None:
            query["overall.match_score"]["$gte"] = min_score
        if max_score is not None:
            query["overall.match_score"]["$lte"] = max_score

    cursor = get_collection().find(query).skip(skip).limit(limit).sort("overall.match_score", -1)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


# ============================================================
# 통계 함수
# ============================================================

async def get_average_score_by_company(company_profile_id: str) -> Optional[float]:
    """특정 회사의 평균 매칭 점수 계산

    Args:
        company_profile_id: 회사 프로필 ID

    Returns:
        평균 점수 또는 None
    """
    pipeline = [
        {"$match": {"inputs.company_profile_ref.profile_id": company_profile_id}},
        {"$group": {"_id": None, "avg_score": {"$avg": "$overall.match_score"}}}
    ]
    async for doc in get_collection().aggregate(pipeline):
        return doc["avg_score"]
    return None


async def get_top_matches_for_developer(
    developer_profile_id: str,
    limit: int = 10
) -> list[dict]:
    """개발자에게 가장 적합한 회사 매칭 결과 조회

    Args:
        developer_profile_id: 개발자 프로필 ID
        limit: 최대 반환 수

    Returns:
        매칭 결과 문서 리스트 (점수 내림차순)
    """
    cursor = get_collection().find({
        "inputs.developer_profile_ref.profile_id": developer_profile_id
    }).sort("overall.match_score", -1).limit(limit)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results


async def get_top_matches_for_company(
    company_profile_id: str,
    limit: int = 10
) -> list[dict]:
    """회사에 가장 적합한 개발자 매칭 결과 조회

    Args:
        company_profile_id: 회사 프로필 ID
        limit: 최대 반환 수

    Returns:
        매칭 결과 문서 리스트 (점수 내림차순)
    """
    cursor = get_collection().find({
        "inputs.company_profile_ref.profile_id": company_profile_id
    }).sort("overall.match_score", -1).limit(limit)
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

    await collection.create_index("inputs.company_profile_ref.profile_id")
    await collection.create_index("inputs.developer_profile_ref.profile_id")
    await collection.create_index("overall.match_score")
    await collection.create_index("overall.score_band")
    await collection.create_index("overall.high_alignment_axes")
    await collection.create_index("overall.risk_or_mismatch_axes")
    await collection.create_index("created_at")

    # 복합 인덱스 (회사-개발자 쌍 검색용)
    await collection.create_index([
        ("inputs.company_profile_ref.profile_id", 1),
        ("inputs.developer_profile_ref.profile_id", 1)
    ], unique=True)