import asyncio
from db.mongodb import connect_db, close_db
from db.repositories import candidate_repository

test_data = {
    "schema_version": "1.0",
    "profile_meta": {
        "candidate_name": "최성민",
        "primary_role": "backend",
        "target_role": "Lead Backend / DevOps Engineer",
        "seniority": "lead",
        "years_experience": 10,
        "source_docs": [
            {
                "doc_id": "resume",
                "filename": "최성민_시니어_리드백엔드_DevOps_이력서.pdf"
            },
            {
                "doc_id": "essay",
                "filename": "최성민_시니어_리드백엔드_DevOps_자기소개서.pdf"
            },
            {
                "doc_id": "portfolio",
                "filename": "최성민_시니어_리드백엔드_DevOps_포트폴리오.pdf"
            }
        ]
    },
    "user_info_fields": {
        "basic_profile": {
            "summary": "백엔드 및 DevOps 영역에서 약 10년간의 실무 경험을 보유한 리드 개발자로, 서버 아키텍처 설계부터 CI/CD 및 클라우드 인프라 운영까지 전반적인 엔지니어링 라이프사이클을 주도한 이력이 명시됨.",
            "evidence": [
                {
                    "doc_id": "resume",
                    "line_refs": ["unknown"],
                    "quote": "백엔드 및 DevOps 영역에서 약 10년간의 실무 경험을 보유한 리드 개발자입니다."
                }
            ]
        },
        "technical_capability": {
            "stack": {
                "languages": ["Java", "Kotlin"],
                "frameworks": ["Spring Boot", "Spring Cloud", "JPA(Hibernate)"],
                "data": ["MySQL", "PostgreSQL", "Redis"],
                "infra_cloud": ["AWS"],
                "ops_tools": ["Docker", "Kubernetes", "GitHub Actions"]
            },
            "ops_deploy_experience": "yes",
            "scale_traffic_platform_mentioned": "yes",
            "evidence": [
                {
                    "doc_id": "resume",
                    "line_refs": ["unknown"],
                    "quote": "CI/CD 파이프라인 구축, 클라우드 인프라 운영까지 전반적인 엔지니어링 라이프사이클을 주도해 왔습니다."
                }
            ]
        },
        "project_behavior_data": {
            "projects": [
                {
                    "name": "모놀리식 서비스의 MSA 전환",
                    "timeframe": "2019.04 – 현재",
                    "context_problem": "단일 모놀리식 구조로 인해 배포 주기가 길고 장애 범위가 넓은 문제",
                    "responsibility_scope": "아키텍처 설계 및 전환 전략 리드",
                    "technical_decisions": ["점진적 MSA 전환", "하이브리드 구조 유지", "도메인 단위 분리"],
                    "outcomes_metrics": [
                        {
                            "metric": "배포 주기",
                            "before": "월 단위",
                            "after": "주 2회 이상",
                            "notes": "배포 자동화 및 구조 개선 결과"
                        }
                    ],
                    "evidence": [
                        {
                            "doc_id": "portfolio",
                            "line_refs": ["unknown"],
                            "quote": "배포 주기는 월 단위에서 주 2회 이상으로 단축되었습니다."
                        }
                    ]
                }
            ]
        },
        "collaboration_experience": {
            "summary": "코드 리뷰 문화 정착, 기술 의사결정 리딩, 주니어·미들 개발자 멘토링 경험이 명시됨.",
            "code_review_participation": "yes",
            "documentation_communication": "high",
            "cross_functional_collaboration": "frequent",
            "conflict_coordination_experience": "mentioned",
            "evidence": [
                {
                    "doc_id": "resume",
                    "line_refs": ["unknown"],
                    "quote": "코드 리뷰 승인 없이는 머지가 불가능한 정책을 도입해 코드 품질을 일정 수준 이상으로 유지했습니다."
                }
            ]
        },
        "growth_tendency": {
            "summary": "장기적인 유지보수성과 아키텍처 개선을 중시하며, 기술 리더로서 조직의 엔지니어링 수준을 높이려는 방향성이 반복적으로 언급됨.",
            "learning_mode": "self_directed",
            "new_tech_adoption": "medium",
            "feedback_receptiveness": "medium",
            "evidence": [
                {
                    "doc_id": "essay",
                    "line_refs": ["unknown"],
                    "quote": "무리한 기술 도입보다는, 팀의 역량과 서비스 특성에 맞는 현실적인 선택을 우선했습니다."
                }
            ]
        },
        "work_environment_signals": {
            "summary": "기술적 판단과 토론이 존중되는 환경, 명확한 아키텍처 기준을 가진 조직을 선호한다고 명시됨.",
            "work_mode_preference": "unknown",
            "work_life_balance_vs_immersion": "balanced",
            "pace_intensity_preference": "moderate",
            "evidence": [
                {
                    "doc_id": "essay",
                    "line_refs": ["unknown"],
                    "quote": "기술적 토론이 존중받는 조직에서 엔지니어링 레벨을 한 단계 끌어올리는 데 기여하고 싶습니다."
                }
            ]
        },
        "verification_needed_areas": {
            "missing_or_unmentioned": ["근무 형태(재택/하이브리드/출근)", "보상 기대 수준"],
            "needs_followup_questions": ["선호하는 근무 방식은 무엇인가?", "팀 규모와 협업 구조에 대한 선호는 있는가?"]
        }
    },
    "scoring_axes": {
        "scoring_policy": {
            "scale": "0-4",
            "meaning": {
                "0": "no explicit signal",
                "1": "weak/indirect mention",
                "2": "some evidence (limited scope)",
                "3": "clear evidence (multiple instances or concrete responsibilities)",
                "4": "strong evidence (clear ownership + concrete outcomes/metrics where applicable)"
            },
            "unknown_handling": "If evidence is missing, score must be 0 and confidence must be low."
        },
        "technical_fit_user": {
            "score": 4,
            "summary": "백엔드 및 DevOps 전반에 걸친 기술 스택, 아키텍처 설계, CI/CD 및 클라우드 운영 경험이 구체적으로 제시됨.",
            "confidence": "high",
            "evidence": [
                {
                    "doc_id": "resume",
                    "line_refs": ["unknown"],
                    "quote": "Java/Kotlin과 Spring 기반의 서버 아키텍처 설계부터 CI/CD 파이프라인 구축, 클라우드 인프라 운영까지"
                }
            ],
            "subsignals": {
                "languages_frameworks_depth": 4,
                "infra_cloud_exposure": 3,
                "ops_deploy_monitoring_exposure": 4,
                "scale_platform_exposure": 3
            }
        },
        "execution_style_user": {
            "score": 3,
            "summary": "단기 속도보다 장기적인 유지보수성과 안정성을 고려한 실행 방식이 반복적으로 언급됨.",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "essay",
                    "line_refs": ["unknown"],
                    "quote": "조금 더 시간이 걸리더라도 장기적으로 유지 가능한 구조를 만들 것인지에 대한 결정을 반복적으로 내려야 했습니다."
                }
            ],
            "subsignals": {
                "speed_vs_stability": "stability",
                "prototype_vs_structure": "structure",
                "business_impact_vs_tech_quality": "balanced"
            }
        },
        "collaboration_style_user": {
            "score": 3,
            "summary": "코드 리뷰, 문서화, 멘토링을 통해 팀 단위 협업을 주도한 경험이 명확히 드러남.",
            "confidence": "high",
            "evidence": [
                {
                    "doc_id": "portfolio",
                    "line_refs": ["unknown"],
                    "quote": "팀 내에서 아키텍처와 설계에 대한 논의 문화가 자리 잡는 변화를 경험했습니다."
                }
            ],
            "subsignals": {
                "code_review": 4,
                "documentation": 3,
                "cross_functional": 2
            }
        },
        "ownership_user": {
            "score": 4,
            "summary": "팀 리드로서 아키텍처, 배포, 운영 정책에 대한 의사결정을 주도한 책임 범위가 명확함.",
            "confidence": "high",
            "evidence": [
                {
                    "doc_id": "resume",
                    "line_refs": ["unknown"],
                    "quote": "백엔드 팀 리드로서 서비스 핵심 도메인의 아키텍처 설계와 기술적 의사결정을 담당했습니다."
                }
            ],
            "subsignals": {
                "problem_definition_involvement": 4,
                "decision_making": 4,
                "role_self_positioning": "lead"
            }
        },
        "growth_orientation_user": {
            "score": 3,
            "summary": "조직과 함께 성장하며 엔지니어링 수준을 끌어올리는 것을 커리어 목표로 명시함.",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "portfolio",
                    "line_refs": ["unknown"],
                    "quote": "조직의 엔지니어링 수준을 한 단계 끌어올리는 기술 리더로서의 역할을 더욱 강화하고자 합니다."
                }
            ],
            "subsignals": {
                "new_tech_adoption": 2,
                "self_directed_learning": 3,
                "feedback_loop": 2
            }
        },
        "work_expectation_user": {
            "score": 2,
            "summary": "기술적 판단이 존중되고 책임과 권한의 균형이 있는 환경을 선호한다는 신호가 존재함.",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "essay",
                    "line_refs": ["unknown"],
                    "quote": "기술 리더로서 충분한 책임은 주어졌지만, 동시에 그에 상응하는 권한은 제한되는 구조"
                }
            ],
            "subsignals": {
                "pace_intensity_preference": 2,
                "wlb_vs_immersion_preference": 2,
                "responsibility_density_signals": 3
            }
        }
    },
    "extraction_quality": {
        "unknown_policy_applied": "yes",
        "notes": "모든 점수는 이력서, 자기소개서, 포트폴리오에 명시된 내용에 한해 부여되었으며, 명시되지 않은 항목은 unknown 처리함."
    }
}


async def main():
    # DB 연결
    await connect_db()
    print("✅ DB 연결 완료")

    # 1. 저장
    candidate_id = await candidate_repository.create_candidate(test_data)
    print(f"✅ 저장 완료 - ID: {candidate_id}")

    # 2. 조회
    saved = await candidate_repository.get_candidate(candidate_id)
    print(f"\n📄 저장된 데이터 조회:")
    print(f"  - 이름: {saved['profile_meta']['candidate_name']}")
    print(f"  - 역할: {saved['profile_meta']['primary_role']}")
    print(f"  - 경력: {saved['profile_meta']['years_experience']}년")
    print(f"  - 기술 스택: {saved['user_info_fields']['technical_capability']['stack']['languages']}")
    print(f"  - technical_fit 점수: {saved['scoring_axes']['technical_fit_user']['score']}")
    print(f"  - ownership 점수: {saved['scoring_axes']['ownership_user']['score']}")

    # 3. 전체 목록 조회
    all_candidates = await candidate_repository.get_all_candidates()
    print(f"\n📋 전체 지원자 수: {len(all_candidates)}명")

    # DB 연결 종료
    await close_db()
    print("\n✅ 테스트 완료")


if __name__ == "__main__":
    asyncio.run(main())