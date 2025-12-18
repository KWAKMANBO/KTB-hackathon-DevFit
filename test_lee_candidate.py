import asyncio
from db.mongodb import connect_db, close_db
from db.repositories import candidate_repository

test_data = {
    "schema_version": "1.0",
    "profile_meta": {
        "candidate_name": "Lee Da-eun",
        "primary_role": "frontend",
        "target_role": "frontend",
        "seniority": "entry",
        "years_experience": "unknown",
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
    },
    "user_info_fields": {
        "basic_profile": {
            "summary": "비전공 문과 출신으로 프론트엔드 국비지원 부트캠프를 수료한 신입 프론트엔드 엔지니어로, UI 구현을 넘어 컴포넌트 구조와 상태 관리를 중시한다고 명시함.",
            "evidence": [
                {
                    "doc_id": "resume",
                    "line_refs": ["unknown"],
                    "quote": "비전공 문과 출신으로 프론트엔드 국비지원 부트캠프를 수료한 신입 프론트엔드 엔지니어입니다."
                }
            ]
        },
        "technical_capability": {
            "stack": {
                "languages": ["JavaScript", "TypeScript"],
                "frameworks": ["React", "Redux Toolkit", "React Query"],
                "data": [],
                "infra_cloud": [],
                "ops_tools": ["Git", "GitHub", "Vite", "ESLint", "Prettier"]
            },
            "ops_deploy_experience": "unknown",
            "scale_traffic_platform_mentioned": "no",
            "evidence": [
                {
                    "doc_id": "resume",
                    "line_refs": ["unknown"],
                    "quote": "Language: JavaScript(ES6+), TypeScript / Framework: React, Redux Toolkit, React Query"
                }
            ]
        },
        "project_behavior_data": {
            "projects": [
                {
                    "name": "커뮤니티형 웹 서비스",
                    "timeframe": "2024.03 ~ 2024.05",
                    "context_problem": "컴포넌트 간 의존성 증가와 상태 흐름 복잡성으로 인한 불필요한 리렌더링 발생",
                    "responsibility_scope": "팀 내 프론트엔드 개발 담당",
                    "technical_decisions": [
                        "Redux Toolkit을 통한 전역 상태 관리",
                        "UI 상태와 데이터 상태 분리",
                        "React.memo를 통한 리렌더링 감소"
                    ],
                    "outcomes_metrics": [],
                    "evidence": [
                        {
                            "doc_id": "portfolio",
                            "line_refs": ["unknown"],
                            "quote": "Redux Toolkit을 활용해 게시글 데이터와 사용자 상태를 전역으로 관리하고, UI 상태는 로컬 상태로 분리하는 구조를 선택했습니다."
                        }
                    ]
                },
                {
                    "name": "사용자 대시보드 웹 애플리케이션",
                    "timeframe": "2024.06",
                    "context_problem": "서버 상태와 UI 상태를 명확히 분리하고자 함",
                    "responsibility_scope": "기획·디자인·프론트엔드 단독 진행",
                    "technical_decisions": [
                        "React Query 도입",
                        "로딩·에러·성공 상태 분리"
                    ],
                    "outcomes_metrics": [],
                    "evidence": [
                        {
                            "doc_id": "portfolio",
                            "line_refs": ["unknown"],
                            "quote": "React Query를 도입해 서버 상태를 관리하고 로딩, 에러, 성공 상태를 명확히 분리했습니다."
                        }
                    ]
                }
            ]
        },
        "collaboration_experience": {
            "summary": "팀 프로젝트에서 백엔드 개발자와 API 명세를 기준으로 협업하고 PR 기반 코드리뷰를 경험했다고 명시함.",
            "code_review_participation": "yes",
            "documentation_communication": "medium",
            "cross_functional_collaboration": "occasional",
            "conflict_coordination_experience": "mentioned",
            "evidence": [
                {
                    "doc_id": "portfolio",
                    "line_refs": ["unknown"],
                    "quote": "백엔드 개발자와 API 명세를 기준으로 협업하며, 에러 코드에 따른 UI 처리 방식을 함께 논의했습니다."
                }
            ]
        },
        "growth_tendency": {
            "summary": "빠른 성장을 위해 피드백과 시행착오를 중시하며 개인 프로젝트와 반복 학습을 선택했다고 서술함.",
            "learning_mode": "self_directed",
            "new_tech_adoption": "medium",
            "feedback_receptiveness": "medium",
            "evidence": [
                {
                    "doc_id": "essay",
                    "line_refs": ["unknown"],
                    "quote": "편한 환경보다는 실제로 손을 많이 써볼 수 있는 환경이 제게 더 잘 맞는다는 확신을 갖게 되었습니다."
                }
            ]
        },
        "work_environment_signals": {
            "summary": "연봉이나 복지보다 실무 비중과 코드리뷰, 성장 가능한 환경을 선호한다고 명시함.",
            "work_mode_preference": "unknown",
            "work_life_balance_vs_immersion": "immersion",
            "pace_intensity_preference": "high_intensity",
            "evidence": [
                {
                    "doc_id": "essay",
                    "line_refs": ["unknown"],
                    "quote": "연봉이나 복지보다 실제 프론트엔드 실무 비중이 높고 코드리뷰와 피드백이 형식적으로 이루어지지 않는 환경을 선호합니다."
                }
            ]
        },
        "verification_needed_areas": {
            "missing_or_unmentioned": [
                "배포 경험",
                "클라우드/인프라 사용 여부",
                "트래픽 규모 경험"
            ],
            "needs_followup_questions": [
                "배포 및 운영 환경 경험이 있는지",
                "서비스 규모나 사용자 수 관련 경험이 있는지"
            ]
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
            "score": 2,
            "summary": "프론트엔드 기술 스택과 상태 관리 도구 사용 경험이 프로젝트 단위로 명시됨.",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "resume",
                    "line_refs": ["unknown"],
                    "quote": "React, Redux Toolkit, React Query를 활용한 프로젝트 경험"
                }
            ],
            "subsignals": {
                "languages_frameworks_depth": 2,
                "infra_cloud_exposure": 0,
                "ops_deploy_monitoring_exposure": 0,
                "scale_platform_exposure": 0
            }
        },
        "execution_style_user": {
            "score": 3,
            "summary": "문제 인식 후 구조를 재정의하고 개선하는 방식의 실행 스타일이 반복적으로 언급됨.",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "portfolio",
                    "line_refs": ["unknown"],
                    "quote": "어떤 상태가 전역으로 관리되어야 하는지 다시 정의했습니다."
                }
            ],
            "subsignals": {
                "speed_vs_stability": "balanced",
                "prototype_vs_structure": "structure",
                "business_impact_vs_tech_quality": "tech_quality"
            }
        },
        "collaboration_style_user": {
            "score": 2,
            "summary": "PR 기반 코드리뷰와 백엔드와의 협업 경험이 명시됨.",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "portfolio",
                    "line_refs": ["unknown"],
                    "quote": "PR 기반 코드리뷰를 통해 구조와 의도에 대한 질문을 받았습니다."
                }
            ],
            "subsignals": {
                "code_review": 2,
                "documentation": 1,
                "cross_functional": 2
            }
        },
        "ownership_user": {
            "score": 2,
            "summary": "개인 프로젝트에서 기획부터 구현까지 단독으로 수행했다고 명시함.",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "portfolio",
                    "line_refs": ["unknown"],
                    "quote": "역할: 기획 · 디자인 · 프론트엔드 단독 진행"
                }
            ],
            "subsignals": {
                "problem_definition_involvement": 2,
                "decision_making": 2,
                "role_self_positioning": "owner"
            }
        },
        "growth_orientation_user": {
            "score": 3,
            "summary": "빠른 성장을 목표로 피드백과 반복 학습을 중시한다고 여러 문서에서 언급됨.",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "essay",
                    "line_refs": ["unknown"],
                    "quote": "어떻게 하면 실무에서 빠르게 따라잡을 수 있을까라는 질문으로 바뀌었습니다."
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
            "summary": "성장 중심의 환경과 높은 실무 비중을 선호한다고 명시함.",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "essay",
                    "line_refs": ["unknown"],
                    "quote": "힘들 수는 있어도, 이 회사에서 분명히 성장하고 있다는 확신을 가질 수 있다면 기꺼이 도전하고 싶습니다."
                }
            ],
            "subsignals": {
                "pace_intensity_preference": 2,
                "wlb_vs_immersion_preference": 2,
                "responsibility_density_signals": 2
            }
        }
    },
    "extraction_quality": {
        "unknown_policy_applied": "yes",
        "notes": "배포, 인프라, 트래픽 규모 관련 명시적 정보는 제공되지 않아 unknown 처리함."
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
    print(f"  - 경력: {saved['profile_meta']['seniority']}")
    print(f"  - 기술 스택: {saved['user_info_fields']['technical_capability']['stack']['frameworks']}")
    print(f"  - technical_fit 점수: {saved['scoring_axes']['technical_fit_user']['score']}")
    print(f"  - execution_style 점수: {saved['scoring_axes']['execution_style_user']['score']}")
    print(f"  - growth_orientation 점수: {saved['scoring_axes']['growth_orientation_user']['score']}")

    # 3. 전체 목록 조회
    all_candidates = await candidate_repository.get_all_candidates()
    print(f"\n📋 전체 지원자 수: {len(all_candidates)}명")

    # DB 연결 종료
    await close_db()
    print("\n✅ 테스트 완료")


if __name__ == "__main__":
    asyncio.run(main())
