import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException
from db.repositories import *
from schema.request_analyze import *
from services.analyze_service import *
from services.s3_service import *

router = APIRouter(prefix="/api/analyze", tags=["candidates"])

# 분석 상태 저장소 (프로덕션에서는 Redis 권장)
analysis_status = {}


# ============================================================
# 더미 분석 함수들 (TODO: LangChain으로 교체)
# ============================================================

async def analyze_jd(jd_url: str) -> dict:
    """
    JD(채용공고) 분석 - 더미 함수
    TODO: LangChain으로 JD URL에서 회사 정보 추출
    """
    await asyncio.sleep(2)  # 분석 시간 시뮬레이션
    return {
        "company_name": "토스",
        "position": "DevOps Engineer",
        "tech_stack": ["Kubernetes", "Docker", "Jenkins"]
    }


async def analyze_resume(result_key: str) -> dict:
    """
    이력서/포트폴리오 분석 - 더미 함수
    TODO: LangChain으로 S3에서 파일 읽어서 분석
    """
    await asyncio.sleep(2)  # 분석 시간 시뮬레이션
    return {
        "candidate_name": "홍길동",
        "skills": ["Python", "React", "AWS"],
        "experience_years": 3
    }


async def calculate_culture_fit(company_data: dict, candidate_data: dict) -> dict:
    """
    컬쳐핏 매칭 점수 계산 - 더미 함수
    TODO: LangChain으로 회사-지원자 매칭 분석
    """
    await asyncio.sleep(2)  # 분석 시간 시뮬레이션
    return {
        "match_score": 75,
        "score_band": "high",
        "strengths": ["기술 스택 일치", "성장 지향성"],
        "risks": ["경력 부족"]
    }


# ============================================================
# 백그라운드 분석 작업
# ============================================================

async def run_analysis(result_key: str, jd_url: str):
    """백그라운드에서 실행되는 전체 분석 파이프라인"""
    try:
        # 1. JD 분석
        analysis_status[result_key] = {
            "status": "processing",
            "step": "jd_analysis",
            "progress": 10,
            "message": "채용공고 분석 중..."
        }
        company_data = await analyze_jd(jd_url)
        analysis_status[result_key]["progress"] = 30

        # 2. 이력서/포트폴리오 분석
        analysis_status[result_key].update({
            "step": "resume_analysis",
            "progress": 40,
            "message": "이력서 분석 중..."
        })
        candidate_data = await analyze_resume(result_key)
        analysis_status[result_key]["progress"] = 60

        # 3. 컬쳐핏 매칭
        analysis_status[result_key].update({
            "step": "culture_fit",
            "progress": 70,
            "message": "컬쳐핏 매칭 중..."
        })
        matching_result = await calculate_culture_fit(company_data, candidate_data)
        analysis_status[result_key]["progress"] = 90

        # 4. DB 저장 (TODO: 실제 저장 로직)
        # company_id = await company_repository.create_company(company_data)
        # candidate_id = await candidate_repository.create_candidate(candidate_data)
        # matching_id = await culture_fit_result_repository.create_matching_result(matching_result)

        # 5. 완료
        analysis_status[result_key] = {
            "status": "completed",
            "step": "done",
            "progress": 100,
            "message": "분석 완료",
            "result": {
                "company": company_data,
                "candidate": candidate_data,
                "culture_fit": matching_result
            }
        }

    except Exception as e:
        analysis_status[result_key] = {
            "status": "failed",
            "step": "error",
            "progress": 0,
            "message": f"분석 실패: {str(e)}"
        }


# ============================================================
# API 엔드포인트
# ============================================================

@router.post("/upload")
async def upload(data: RequestAnalyze):
    """1단계: Presigned URL 발급"""
    presigned_urls = []
    result_key = generate_result_key()

    for f in data.files:
        presigned_urls.append(generated_presigned_url(result_key, f.file_name, f.content_type))

    # 상태 초기화
    analysis_status[result_key] = {
        "status": "pending",
        "step": "upload",
        "progress": 0,
        "message": "파일 업로드 대기 중...",
        "jd_url": data.jd_url
    }

    return {
        "result_key": result_key,
        "presigned_urls": presigned_urls
    }


@router.post("/start/{result_key}")
async def start_analysis(result_key: str, background_tasks: BackgroundTasks):
    """2단계: 파일 업로드 완료 후 분석 시작"""
    if result_key not in analysis_status:
        raise HTTPException(status_code=404, detail="result_key not found")

    jd_url = analysis_status[result_key].get("jd_url", "")

    # 백그라운드에서 분석 실행
    background_tasks.add_task(run_analysis, result_key, jd_url)

    return {
        "result_key": result_key,
        "status": "started",
        "message": "분석이 시작되었습니다."
    }


@router.get("/status/{result_key}")
async def get_status(result_key: str, timeout: int = 30):
    """3단계: Long Polling으로 상태 확인"""
    if result_key not in analysis_status:
        raise HTTPException(status_code=404, detail="result_key not found")

    elapsed = 0
    poll_interval = 1

    while elapsed < timeout:
        status = analysis_status.get(result_key)

        # 완료/실패 시 즉시 반환
        if status["status"] in ["completed", "failed"]:
            return status

        await asyncio.sleep(poll_interval)
        elapsed += poll_interval

    # 타임아웃 시 현재 상태 반환
    return analysis_status.get(result_key)


@router.get("/result/{result_key}")
async def get_result(result_key: str):
    """최종 결과만 조회"""
    if result_key not in analysis_status:
        raise HTTPException(status_code=404, detail="result_key not found")

    status = analysis_status.get(result_key)

    if status["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"분석이 완료되지 않았습니다. 현재 상태: {status['status']}"
        )

    return status["result"]


@router.get("/test")
async def get_test_result():
    company = await company_repository.get_company("6943abdef7b7923a729dc29e")
    candidate = await candidate_repository.get_candidate("6943abaef7b7923a729dc29d")
    result = await culture_fit_result_repository.get_matching_result("6943ae7ca29d0aaf389dc29d")

    return {
        "company_analysis": company,
        "candidate_analysis": candidate,
        "culture_fit_result": result
    }
