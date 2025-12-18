import asyncio
from db.mongodb import connect_db, close_db
from db.repositories import culture_fit_result_repository

test_data = {
    "schema_version": "1.0",
    "meta": {
        "generated_at": "2025-12-18",
        "scoring_version": "alignment-v1",
        "axes_used": [
            "technical_fit",
            "execution_style",
            "collaboration_style",
            "growth_learning_orientation",
            "product_user_impact_orientation",
            "ops_quality_responsibility"
        ],
        "notes": "입력 JSON에 명시된 정보만 사용하여 비교함"
    },
    "inputs": {
        "company_profile_ref": {
            "profile_id": "upstage_company_profile",
            "source_docs": [
                {
                    "doc_id": "job_posting",
                    "filename": "unknown"
                }
            ]
        },
        "developer_profile_ref": {
            "profile_id": "P6_Yoon_Jihoon",
            "source_docs": [
                {
                    "doc_id": "portfolio",
                    "filename": "Portfolio – 윤지훈 (Yoon Ji-hoon).pdf"
                },
                {
                    "doc_id": "resume",
                    "filename": "이력서 – 윤지훈 (Yoon Ji-hoon).pdf"
                },
                {
                    "doc_id": "essay",
                    "filename": "자기소개서 – 윤지훈.pdf"
                }
            ]
        }
    },
    "axis_alignments": {
        "technical_fit": {
            "status": "partial",
            "axis_score": 75,
            "summary": "ML 모델 운영 경험과 DevOps/배포 자동화 요구가 부분적으로 겹침",
            "rationale": {
                "company_signals": [
                    "CI/CD 파이프라인 구축",
                    "Docker/Kubernetes, 모니터링 스택 언급"
                ],
                "developer_signals": [
                    "ML 모델 운영 파이프라인 구축",
                    "Airflow 기반 배치/운영 경험"
                ],
                "comparison_notes": "ML 운영 관점에서는 정합성이 있으나, 대규모 플랫폼/트래픽 신호는 양측 모두 명확하지 않음"
            },
            "evidence_refs": {
                "company": [
                    {
                        "path": "company_info_fields.technical_environment.evidence",
                        "quote": "CI/CD 파이프라인 구축 및 인프라 레벨 배포 자동화 수행 역량"
                    }
                ],
                "developer": [
                    {
                        "path": "user_info_fields.technical_capability.evidence",
                        "quote": "Airflow를 통해 배치 파이프라인을 안정화했습니다."
                    }
                ]
            },
            "followup_questions": [
                "Kubernetes 기반 서비스 운영에 직접 참여한 경험이 있는가?"
            ]
        },
        "execution_style": {
            "status": "partial",
            "axis_score": 50,
            "summary": "안정성 중시 성향과 혁신 지향 문화가 일부 교차",
            "rationale": {
                "company_signals": [
                    "끊임없이 개선과 혁신을 추구"
                ],
                "developer_signals": [
                    "유지보수 가능성과 재현성을 우선"
                ],
                "comparison_notes": "회사는 개선/혁신을 강조하나 속도·안정성 기준은 불명확"
            },
            "evidence_refs": {
                "company": [
                    {
                        "path": "company_info_fields.execution_culture_signals.evidence",
                        "quote": "끊임없이 개선과 혁신을 추구"
                    }
                ],
                "developer": [
                    {
                        "path": "scoring_axes.execution_style_user.evidence",
                        "quote": "과도한 커스터마이징보다는 유지보수 가능성과 명확한 구조를 우선했습니다."
                    }
                ]
            },
            "followup_questions": [
                "업무에서 실험/프로토타입 비중은 어느 정도인가?"
            ]
        },
        "collaboration_style": {
            "status": "partial",
            "axis_score": 75,
            "summary": "타 직군 협업과 조율 경험이 회사 기대와 대체로 부합",
            "rationale": {
                "company_signals": [
                    "다양한 팀의 협업 언급"
                ],
                "developer_signals": [
                    "요구사항을 기술적으로 번역·조율"
                ],
                "comparison_notes": "문서화/코드리뷰 문화는 회사 측에서 명시되지 않음"
            },
            "evidence_refs": {
                "company": [
                    {
                        "path": "company_info_fields.collaboration_culture_signals.evidence",
                        "quote": "다양한 팀의 협업을 통해"
                    }
                ],
                "developer": [
                    {
                        "path": "user_info_fields.collaboration_experience.evidence",
                        "quote": "요구사항을 기술적으로 번역하는 역할을 자주 맡아 왔습니다."
                    }
                ]
            },
            "followup_questions": [
                "공식적인 코드 리뷰 프로세스가 존재하는가?"
            ]
        },
        "growth_learning_orientation": {
            "status": "aligned",
            "axis_score": 100,
            "summary": "학습 지원 문화와 운영 중심 성장 경험이 명확히 정합",
            "rationale": {
                "company_signals": [
                    "도서/교육/어학 비용 지원"
                ],
                "developer_signals": [
                    "운영 경험을 통해 관점 전환 및 지속적 학습"
                ],
                "comparison_notes": "성장 지원과 개인 학습 방향이 일관됨"
            },
            "evidence_refs": {
                "company": [
                    {
                        "path": "company_info_fields.growth_learning_culture_signals.evidence",
                        "quote": "성장에 필요한 비용을 지원"
                    }
                ],
                "developer": [
                    {
                        "path": "user_info_fields.growth_tendency.evidence",
                        "quote": "AI의 진짜 난이도는 운영 단계에 있다는 점을 체감했습니다."
                    }
                ]
            },
            "followup_questions": []
        },
        "product_user_impact_orientation": {
            "status": "unknown",
            "axis_score": "unknown",
            "summary": "제품/사용자 임팩트에 대한 명시적 비교 근거 부족",
            "rationale": {
                "company_signals": [],
                "developer_signals": [],
                "comparison_notes": "양측 모두 사용자 임팩트 지표가 구체적으로 제시되지 않음"
            },
            "evidence_refs": {
                "company": [],
                "developer": []
            },
            "followup_questions": [
                "모델 개선이 실제 사용자 지표에 미친 영향은 무엇인가?"
            ]
        },
        "ops_quality_responsibility": {
            "status": "aligned",
            "axis_score": 100,
            "summary": "운영 표준·자동화에 대한 책임 기대와 경험이 강하게 일치",
            "rationale": {
                "company_signals": [
                    "운영 표준 및 자동화 도구 직접 개발"
                ],
                "developer_signals": [
                    "프로세스 중심 운영 전환",
                    "모델 버전/운영 안정성 관리"
                ],
                "comparison_notes": "운영 품질에 대한 오너십 성향이 동일하게 나타남"
            },
            "evidence_refs": {
                "company": [
                    {
                        "path": "company_info_fields.ownership_expectation_signals.evidence",
                        "quote": "자동화 도구와 운영 표준을 직접 개발"
                    }
                ],
                "developer": [
                    {
                        "path": "scoring_axes.ownership_user.evidence",
                        "quote": "개인 의존도를 낮추고 프로세스 중심 운영 전환"
                    }
                ]
            },
            "followup_questions": []
        }
    },
    "overall": {
        "match_score": 83,
        "score_band": "high",
        "confidence": 0.8,
        "scoring": {
            "weights": {
                "technical_fit": 1,
                "execution_style": 1,
                "collaboration_style": 1,
                "growth_learning_orientation": 1,
                "product_user_impact_orientation": 1,
                "ops_quality_responsibility": 1
            },
            "excluded_axes": [
                "product_user_impact_orientation"
            ],
            "calculation_notes": "unknown 축 1개 제외, 나머지 5개 축 평균"
        },
        "high_alignment_axes": [
            "growth_learning_orientation",
            "ops_quality_responsibility"
        ],
        "risk_or_mismatch_axes": [
            "execution_style"
        ],
        "unknown_axes": [
            "product_user_impact_orientation"
        ],
        "overall_notes": "운영 중심 AI/ML 엔지니어 성향과 회사의 DevOps·운영 책임 기대가 전반적으로 정합"
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
    print(f"  - 높은 정합성 축: {saved['overall']['high_alignment_axes']}")
    print(f"  - 리스크 축: {saved['overall']['risk_or_mismatch_axes']}")

    # 3. 축별 점수 출력
    print(f"\n📊 축별 점수:")
    for axis_name, axis_data in saved['axis_alignments'].items():
        if axis_data:
            print(f"  - {axis_name}: {axis_data['axis_score']}점 ({axis_data['status']})")

    # 4. 전체 목록 조회
    all_results = await culture_fit_result_repository.get_all_matching_results()
    print(f"\n📋 전체 매칭 결과 수: {len(all_results)}개")

    # 5. 점수 밴드별 검색 테스트
    high_matches = await culture_fit_result_repository.find_by_score_band("high")
    print(f"📋 높은 적합도 매칭 수: {len(high_matches)}개")

    # DB 연결 종료
    await close_db()
    print("\n✅ 테스트 완료")


if __name__ == "__main__":
    asyncio.run(main())