import asyncio
from db.mongodb import connect_db, close_db
from db.repositories import company_repository

test_data = {
    "schema_version": "1.0",
    "profile_meta": {
        "company_name": "업스테이지",
        "industry": "unknown",
        "primary_domain": "upstage.ai",
        "analyzed_scope": "company",
        "analyzed_date": "2025-12-18",
        "source_docs": [
            {
                "doc_id": "job_posting",
                "filename": "unknown",
                "url": "unknown"
            }
        ]
    },
    "company_info_fields": {
        "basic_profile": {
            "summary": "AI 기술을 활용하여 비즈니스 문제를 해결",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "AI 기술을 활용하여 비즈니스 문제를 해결"
                }
            ]
        },
        "technical_environment": {
            "stack": {
                "languages": ["Python", "Js", "Ts", "Java"],
                "frameworks": ["Spring F/W", "Tomcat"],
                "data": ["RDBMS", "NoSQL", "OAuth", "HTTP", "XML/JSON"],
                "infra_cloud": ["AWS", "GCP", "Azure", "Docker", "Kubernetes(K8s)", "Linux"],
                "ops_tools": ["Prometheus", "Grafana", "Jira", "Git", "Slack", "CI/CD"]
            },
            "ops_deploy_experience_required_or_mentioned": "yes",
            "scale_traffic_platform_mentioned": "unknown",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "CI/CD 파이프라인 구축 및 인프라 레벨 배포 자동화 수행 역량"
                }
            ]
        },
        "role_and_hiring_signals": {
            "hiring_summary": "AI DevOps (정규직), 모집 절차 전체 온라인 진행",
            "open_roles_mentioned": ["AI DevOps"],
            "employment_type": "full_time",
            "location": "unknown",
            "remote_hybrid_onsite": "remote",
            "required_experience": "API 설계, 개발 및 유지보수 경력 3~10년 또는 그에 준하는 개발 업무 역량",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "근무 환경\nAnywhere On Earth But Together! '어디서든' 함께 일할 수 있습니다."
                }
            ]
        },
        "execution_culture_signals": {
            "summary": "개선과 혁신을 추구하며 최신 기술을 실무에 적용, 내부 솔루션 자체 개발 언급",
            "speed_vs_stability": "unknown",
            "prototype_vs_structure": "unknown",
            "business_impact_vs_tech_quality": "unknown",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "끊임없이 개선과 혁신을 추구"
                }
            ]
        },
        "collaboration_culture_signals": {
            "summary": "고객 요구사항 파악 및 다양한 팀 협업, 파트너 협력 체계 언급",
            "code_review_culture": "unknown",
            "documentation_culture": "unknown",
            "cross_functional_collaboration": "mentioned",
            "decision_making_process": "unknown",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "다양한 팀의 협업을 통해"
                }
            ]
        },
        "ownership_expectation_signals": {
            "summary": "고객사 연계 설계/개발, 배포 프로토콜/방법론 개발, 운영 표준/도구 직접 개발 등 책임 범위 언급",
            "problem_definition_expected": "unknown",
            "decision_making_expected": "unknown",
            "role_positioning": "owner",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "자동화 도구와 운영 표준을 직접 개발"
                }
            ]
        },
        "growth_learning_culture_signals": {
            "summary": "성장 비용(도서/교육/어학) 지원 및 최신 기술 실무 적용 언급",
            "learning_support": "mentioned",
            "new_tech_adoption": "unknown",
            "feedback_culture": "unknown",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "도서, 자료, 교육 및 어학 수강비 등 성장에 필요한 비용을 지원"
                }
            ]
        },
        "work_environment_expectations": {
            "summary": "원격 근무 및 원격 장비/카페/공유오피스/운동비/보험/건강검진 지원 언급",
            "work_mode": "remote",
            "wlb_vs_immersion": "unknown",
            "pace_intensity": "unknown",
            "oncall_or_shift": "unknown",
            "overtime_or_night_work": "unknown",
            "benefits_or_perks": [
                "원격 근무 장비를 500만원 예산 내 자유롭게 선택",
                "카페 이용 시 음료 비용 지원",
                "스터디룸 혹은 공유오피스 이용 비용 지원",
                "업무 관련 소프트웨어/도서/자료/교육/어학 수강비 지원",
                "운동비 지원",
                "직장 단체보험 지원",
                "종합건강검진 지원"
            ],
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "Anywhere On Earth But Together! '어디서든' 함께 일할 수 있습니다."
                }
            ]
        },
        "verification_needed_areas": {
            "missing_or_unmentioned": [
                "industry (정식 업종 표기)",
                "official company URLs (채용 페이지/공식 사이트 URL)",
                "scale/traffic/platform 명시",
                "code review culture",
                "documentation culture",
                "decision making process",
                "feedback culture",
                "oncall/shift, overtime/night work"
            ],
            "needs_followup_questions": [
                "공식 회사 홈페이지/채용 페이지/기술 블로그 URL을 제공할 수 있나요?",
                "플랫폼 규모/트래픽/서비스 운영 규모에 대한 공식 문구가 있나요?",
                "코드 리뷰/문서화/피드백 관련 공식 프로세스 문구가 있나요?",
                "온콜/교대/야간 대응 등 운영 근무 형태가 공식적으로 명시되어 있나요?"
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
                "3": "clear evidence (multiple instances or concrete practices)",
                "4": "strong evidence (clear ownership + concrete policies/practices)"
            },
            "unknown_handling": "If evidence is missing, score must be 0 and confidence must be low."
        },
        "technical_fit_company": {
            "score": 2,
            "summary": "DevOps/배포 자동화, CI/CD, Docker/Kubernetes, 모니터링(Prometheus/Grafana) 등이 명시됨",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "Prometheus, Grafana 등 오픈소스 모니터링 스택 구성 및 운영 경험"
                }
            ],
            "subsignals": {
                "languages_frameworks_depth": 1,
                "infra_cloud_exposure": 2,
                "ops_deploy_monitoring_exposure": 2,
                "scale_platform_exposure": 0
            }
        },
        "execution_style_company": {
            "score": 1,
            "summary": "개선/혁신 및 최신 기술 실무 적용, 내부 솔루션 자체 개발 언급",
            "confidence": "low",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "끊임없이 개선과 혁신을 추구"
                }
            ],
            "subsignals": {
                "speed_vs_stability": "unknown",
                "prototype_vs_structure": "unknown",
                "business_impact_vs_tech_quality": "unknown"
            }
        },
        "collaboration_style_company": {
            "score": 1,
            "summary": "고객 요구사항 파악 및 다양한 팀 협업/파트너 협력 언급",
            "confidence": "low",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "다양한 팀의 협업을 통해"
                }
            ],
            "subsignals": {
                "code_review": 0,
                "documentation": 0,
                "cross_functional": 1
            }
        },
        "ownership_company": {
            "score": 2,
            "summary": "운영 표준/자동화 도구 직접 개발, 고객사 연계 설계/개발 등 책임 범위 언급",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "자동화 도구와 운영 표준을 직접 개발"
                }
            ],
            "subsignals": {
                "problem_definition_involvement": 0,
                "decision_making": 0,
                "role_self_positioning": "owner"
            }
        },
        "growth_orientation_company": {
            "score": 2,
            "summary": "성장 비용(도서/교육/어학) 지원 및 최신 기술 실무 적용 언급",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "도서, 자료, 교육 및 어학 수강비 등 성장에 필요한 비용을 지원"
                }
            ],
            "subsignals": {
                "new_tech_adoption": 1,
                "self_directed_learning": 1,
                "feedback_loop": 0
            }
        },
        "work_expectation_company": {
            "score": 2,
            "summary": "원격 근무 및 장비/업무환경/건강 관련 지원이 구체적으로 명시됨",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "원격 근무에 필요한 장비를 500만원 예산 내에 자유롭게 선택"
                }
            ],
            "subsignals": {
                "pace_intensity_preference": 0,
                "wlb_vs_immersion_preference": 0,
                "responsibility_density_signals": 1
            }
        }
    },
    "extraction_quality": {
        "unknown_policy_applied": "yes",
        "notes": "공식 사이트 URL/라인 번호가 제공되지 않아 line_refs와 url은 unknown으로 처리함. 입력 텍스트에서 명시된 문구만 반영함."
    }
}


async def main():
    # DB 연결
    await connect_db()
    print("✅ DB 연결 완료")

    # 1. 저장
    company_id = await company_repository.create_company(test_data)
    print(f"✅ 저장 완료 - ID: {company_id}")

    # 2. 조회
    saved = await company_repository.get_company(company_id)
    print(f"\n📄 저장된 데이터 조회:")
    print(f"  - 회사명: {saved['profile_meta']['company_name']}")
    print(f"  - 도메인: {saved['profile_meta']['primary_domain']}")
    print(f"  - 근무형태: {saved['company_info_fields']['work_environment_expectations']['work_mode']}")
    print(f"  - 기술 스택: {saved['company_info_fields']['technical_environment']['stack']['languages']}")
    print(f"  - technical_fit 점수: {saved['scoring_axes']['technical_fit_company']['score']}")
    print(f"  - ownership 점수: {saved['scoring_axes']['ownership_company']['score']}")

    # 3. 전체 목록 조회
    all_companies = await company_repository.get_all_companies()
    print(f"\n📋 전체 회사 수: {len(all_companies)}개")

    # 4. 검색 테스트
    remote_companies = await company_repository.find_by_work_mode("remote")
    print(f"📋 원격 근무 회사 수: {len(remote_companies)}개")

    # DB 연결 종료
    await close_db()
    print("\n✅ 테스트 완료")


if __name__ == "__main__":
    asyncio.run(main())