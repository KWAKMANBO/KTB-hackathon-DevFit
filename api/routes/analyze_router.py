import asyncio
import logging
import time
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from db.repositories import *
from schema.request_analyze import *
from services.analyze_service import *
from services.s3_service import *

# LangChain 파이프라인
from apiv2.langchain_pipeline.chains.company_chain import CompanyAnalysisChain
from apiv2.langchain_pipeline.chains.applicant_chain import ApplicantAnalysisChain
from apiv2.langchain_pipeline.chains.compare_chain import CultureCompareChain

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analyze", tags=["candidates"])

# 분석 상태 저장소 (프로덕션에서는 Redis 권장)
analysis_status = {}


# ============================================================
# 백그라운드 분석 작업
# ============================================================

async def run_analysis(result_key: str, jd_url: str, s3_keys: list[str]):
    """백그라운드에서 실행되는 전체 분석 파이프라인 (LangChain)"""
    company_chain = None
    applicant_chain = None
    compare_chain = None
    total_start = time.time()

    logger.info(f"{'=' * 60}")
    logger.info(f"🚀 분석 시작 | result_key: {result_key}")
    logger.info(f"   JD URL: {jd_url}")
    logger.info(f"   S3 Keys: {s3_keys}")
    logger.info(f"{'=' * 60}")

    try:
        # 체인 초기화 (save_to_db=True로 LangChain에서 직접 DB 저장)
        logger.info("⚙️  체인 초기화 중...")
        company_chain = CompanyAnalysisChain(save_to_db=True)
        applicant_chain = ApplicantAnalysisChain(save_to_db=True)
        compare_chain = CultureCompareChain(save_to_db=True)
        logger.info("✅ 체인 초기화 완료")

        # 1. 회사 + 구직자 병렬 분석
        logger.info(f"\n{'─' * 40}")
        logger.info("🚀 [1/3] 회사 + 구직자 병렬 분석 시작")
        logger.info(f"   📋 회사 JD: {jd_url}")
        logger.info(f"   📄 구직자 S3: {s3_keys[0] if s3_keys else 'N/A'}")
        step_start = time.time()

        if not s3_keys:
            raise ValueError("분석할 파일이 없습니다.")

        analysis_status[result_key] = {
            "status": "processing",
            "step": "parallel_analysis",
            "progress": 10,
            "message": "회사 + 구직자 병렬 분석 중..."
        }

        # 병렬 실행
        company_data, candidate_data = await asyncio.gather(
            company_chain.run(jd_url),
            applicant_chain.run_from_s3(s3_keys[0])
        )

        analysis_status[result_key]["progress"] = 70
        logger.info(f"✅ [1/3] 병렬 분석 완료 ({time.time() - step_start:.1f}초)")
        logger.info(f"   회사명: {company_data.get('profile_meta', {}).get('company_name', 'N/A')}")
        logger.info(f"   지원자명: {candidate_data.get('profile_meta', {}).get('candidate_name', 'N/A')}")

        # 2. 컬쳐핏 매칭
        logger.info(f"\n{'─' * 40}")
        logger.info("🔄 [2/3] 컬쳐핏 매칭 시작")
        step_start = time.time()
        analysis_status[result_key].update({
            "step": "culture_fit",
            "progress": 80,
            "message": "컬쳐핏 매칭 중..."
        })
        matching_result = await compare_chain.run(company_data, candidate_data)
        analysis_status[result_key]["progress"] = 95
        logger.info(f"✅ [2/3] 컬쳐핏 매칭 완료 ({time.time() - step_start:.1f}초)")
        logger.info(f"   매칭 점수: {matching_result.get('overall', {}).get('match_score', 'N/A')}")

        # 3. DB 저장 완료 확인 (LangChain에서 이미 저장됨)
        logger.info(f"\n{'─' * 40}")
        logger.info("💾 [3/3] DB 저장 완료 (LangChain 내부에서 저장됨)")
        company_id = company_data.get("_id", "N/A")
        candidate_id = candidate_data.get("_id", "N/A")
        matching_id = matching_result.get("_id", "N/A")
        logger.info(f"   company_id: {company_id}")
        logger.info(f"   candidate_id: {candidate_id}")
        logger.info(f"   matching_id: {matching_id}")

        # 4. 완료
        analysis_status[result_key] = {
            "status": "completed",
            "step": "done",
            "progress": 100,
            "message": "분석 완료",
            "result": {
                "company_id": company_id,
                "candidate_id": candidate_id,
                "matching_id": matching_id,
                "company": company_data,
                "candidate": candidate_data,
                "culture_fit": matching_result
            }
        }

        logger.info(f"\n{'=' * 60}")
        logger.info(f"🎉 분석 완료! 총 소요시간: {time.time() - total_start:.1f}초")
        logger.info(f"{'=' * 60}\n")

    except Exception as e:
        logger.error(f"\n{'=' * 60}")
        logger.error(f"❌ 분석 실패: {str(e)}")
        logger.error(f"{'=' * 60}\n")
        analysis_status[result_key] = {
            "status": "failed",
            "step": "error",
            "progress": 0,
            "message": f"분석 실패: {str(e)}"
        }

    finally:
        # 리소스 정리
        logger.info("🧹 리소스 정리 중...")
        if company_chain:
            company_chain.close()
        if applicant_chain:
            applicant_chain.close()
        if compare_chain:
            compare_chain.close()
        logger.info("✅ 리소스 정리 완료")


# ============================================================
# API 엔드포인트
# ============================================================

@router.post("/upload")
async def upload(data: RequestAnalyze):
    """1단계: Presigned URL 발급"""
    presigned_urls = []
    result_key = generate_result_key()

    logger.info(f"📤 Upload 요청 | JD URL: {data.jd_url}")
    logger.info(f"   파일 수: {len(data.files)}")

    # S3 키 목록 생성
    s3_keys = []
    for f in data.files:
        # s3_key = f"{result_key}/{f.file_name}"
        # s3_keys.append(s3_key)
        presigned_urls.append(generated_presigned_url(result_key, f.file_name, f.content_type))
        logger.info(f"   - {f.file_name} ({f.content_type})")

    # 상태 초기화 (s3_keys 포함)
    analysis_status[result_key] = {
        "status": "pending",
        "step": "upload",
        "progress": 0,
        "message": "파일 업로드 대기 중...",
        "jd_url": data.jd_url,
        # "s3_keys": s3_keys
    }

    # print(analysis_status)

    logger.info(f"✅ result_key 발급: {result_key}")

    return {
        "result_key": result_key,
        "presigned_urls": presigned_urls
    }


@router.post("/start/{result_key}")
# @router.post("/start")
async def start_analysis(result_key: str, background_tasks: BackgroundTasks):
# # async def start_analysis(background_tasks: BackgroundTasks):
#     result_key = 'd1bb78a6-fad5-4583-8f51-c68e989ef059'
#     analysis_status['d1bb78a6-fad5-4583-8f51-c68e989ef059'] = {'status': 'pending', 'step': 'upload', 'progress': 0,
#                                                                'message': '파일 업로드 대기 중...',
#                                                                'jd_url': 'https://toss.im/career/jobs/4829381'}

    """2단계: 파일 업로드 완료 후 분석 시작"""
    if result_key not in analysis_status:
        raise HTTPException(status_code=404, detail="result_key not found")

    jd_url = analysis_status[result_key].get("jd_url", "")

    # S3에서 'result_key/' prefix를 가진 파일 목록을 직접 가져옵니다.
    s3_keys = list_files_in_prefix(result_key)

    if not s3_keys:
        # S3에 파일이 없으면 분석을 시작할 수 없으므로 오류 처리
        raise HTTPException(status_code=400, detail="S3에 업로드된 파일이 없습니다. 파일을 먼저 업로드해주세요.")

    # 백그라운드에서 분석 실행
    background_tasks.add_task(run_analysis, result_key, jd_url, s3_keys)

    # 상태 업데이트: 분석 시작됨을 명시하고, 찾은 s3_keys를 저장
    analysis_status[result_key].update({
        "status": "started",
        "step": "analysis_start",
        "progress": 5,
        "message": "분석이 시작되었습니다.",
        "s3_keys": s3_keys
    })

    return {
        "result_key": result_key,
        "status": "started",
        "message": "분석이 시작되었습니다."
    }


@router.get("/status/{result_key}")
async def get_status(result_key: str, timeout: int = 15):
    """3단계: Long Polling으로 상태 확인

    Response Status Codes:
        200: 분석 완료 (completed)
        202: 분석 진행 중 (processing/timeout)
        404: result_key를 찾을 수 없음
        500: 분석 실패 (failed)
    """
    if result_key not in analysis_status:
        raise HTTPException(status_code=404, detail="result_key not found")

    elapsed = 0
    poll_interval = 1

    while elapsed < timeout:
        status = analysis_status.get(result_key)

        # 완료 시 200 OK 반환 - MongoDB에서 조회하여 반환
        if status["status"] == "completed":
            result = status.get("result", {})
            company_id = result.get("company_id")
            candidate_id = result.get("candidate_id")
            matching_id = result.get("matching_id")

            # MongoDB에서 각 데이터 조회
            company_analysis = await company_repository.get_company(company_id) if company_id else None
            candidate_analysis = await candidate_repository.get_candidate(candidate_id) if candidate_id else None
            culture_fit_result = await culture_fit_result_repository.get_matching_result(matching_id) if matching_id else None

            response_data = {
                "status": "completed",
                "progress": 100,
                "message": "분석 완료",
                "company_analysis": company_analysis,
                "candidate_analysis": candidate_analysis,
                "culture_fit_result": culture_fit_result
            }
            return JSONResponse(status_code=200, content=response_data)

        # 실패 시 500 Internal Server Error 반환
        if status["status"] == "failed":
            return JSONResponse(status_code=500, content=status)

        await asyncio.sleep(poll_interval)
        elapsed += poll_interval

    # 타임아웃 시 202 Accepted (아직 처리 중) 반환
    return JSONResponse(status_code=202, content=analysis_status.get(result_key))


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
