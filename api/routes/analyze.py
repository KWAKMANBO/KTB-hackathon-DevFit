from fastapi import FastAPI, APIRouter
from db.repositories import *

router = APIRouter(prefix="/api/analyze", tags=["candidates"])


@router.post("/")
async def create_candidate(data: dict):
    """지원자 생성"""
    candidate_id = await candidate_repository.create_candidate(data)
    return {"id": candidate_id}


@router.get("/test")
async def get_test_result():
    company = await company_repository.get_company("694387b2ee91fdb7676a6872")
    candidate = await candidate_repository.get_candidate("6943597c52402882d12e5f89")
    result = await culture_fit_result_repository.get_matching_result("69438f21103b5004a1629126")

    return {
        "company_analysis": company,
        "candidate_analysis": candidate,
        "culture_fit_result": result
    }
