import asyncio
from db.mongodb import connect_db, close_db
from db.repositories import culture_fit_result_repository

test_data = {
    "schema_version": "1.0",
    "meta": {
        "generated_at": "2025-12-18",
        "scoring_version": "v1.0-equal-weights",
        "axes_used": [
            "technical_fit",
            "execution_style",
            "collaboration_style",
            "growth_learning_orientation",
            "product_user_impact_orientation",
            "ops_quality_responsibility"
        ],
        "notes": "명시적 JSON 신호만 사용. 프론트엔드 신입 개발자와 DevOps 중심 회사 포지션 간 비교."
    },
    "inputs": {
        "company_profile_ref": {
            "profile_id": "toss_devops_company_profile",
            "source_docs": [
                {
                    "doc_id": "job_posting",
                    "filename": "unknown"
                }
            ]
        },
        "developer_profile_ref": {
            "profile_id": "P2_LeeDaeun_frontend_entry",
            "source_docs": [
                {
                    "doc_id": "portfolio",
                    "filename": "Portfolio – 이다은 (Lee Da-eun).pdf"
                },
                {
                    "doc_id": "resume",
                    "filename": "이력서 – 이다은 (Lee Da-eun).pdf"
                },
                {
                    "doc_id": "essay",
                    "filename": "자기소개서 – 이다은.pdf"
                }
            ]
        }
    },
    "axis_alignments": {},
    "overall": {
        "match_score": 45,
        "score_band": "medium",
        "confidence": 0.65,
        "scoring": {
            "weights": {
                "technical_fit": 1,
                "execution_style": 1,
                "collaboration_style": 1,
                "growth_learning_orientation": 1,
                "product_user_impact_orientation": 1,
                "ops_quality_responsibility": 1
            },
            "excluded_axes": [],
            "calculation_notes": "프론트엔드 신입 개발자와 DevOps 중심 회사 포지션 간 비교"
        },
        "high_alignment_axes": [],
        "risk_or_mismatch_axes": ["technical_fit"],
        "unknown_axes": [],
        "overall_notes": "프론트엔드 신입 개발자와 DevOps 중심 회사 포지션 간 기술 스택 불일치"
    }
}


async def main():
    # DB 연결
    await connect_db()
    print("✅ DB 연결 완료")

    # 1. 저장
    result_id = await culture_fit_result_repository.create_matching_result(test_data)
    print(f"✅ 저장 완료 - ID: {result_id}")

    # 2. 조회
    saved = await culture_fit_result_repository.get_matching_result(result_id)
    print(f"\n📄 저장된 데이터 조회:")
    print(f"  - 회사: {saved['inputs']['company_profile_ref']['profile_id']}")
    print(f"  - 개발자: {saved['inputs']['developer_profile_ref']['profile_id']}")
    print(f"  - 매칭 점수: {saved['overall']['match_score']}점")
    print(f"  - 점수 밴드: {saved['overall']['score_band']}")
    print(f"  - 신뢰도: {saved['overall']['confidence']}")
    print(f"  - 리스크 축: {saved['overall']['risk_or_mismatch_axes']}")

    # 3. 전체 목록 조회
    all_results = await culture_fit_result_repository.get_all_matching_results()
    print(f"\n📋 전체 매칭 결과 수: {len(all_results)}개")

    # DB 연결 종료
    await close_db()
    print("\n✅ 테스트 완료")


if __name__ == "__main__":
    asyncio.run(main())