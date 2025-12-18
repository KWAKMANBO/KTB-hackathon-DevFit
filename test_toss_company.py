import asyncio
from db.mongodb import connect_db, close_db
from db.repositories import company_repository

test_data = {
    "schema_version": "1.0",
    "profile_meta": {
        "company_name": "토스",
        "industry": "unknown",
        "primary_domain": "toss.im",
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
            "summary": "unknown",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "㈜비바리퍼블리카"
                }
            ]
        },
        "technical_environment": {
            "stack": {
                "languages": ["Java"],
                "frameworks": ["Spring Framework", "JPA/Hibernate"],
                "data": ["Kafka", "Elastic", "InfluxData", "Memcached"],
                "infra_cloud": ["Kubernetes", "Cloud Native", "Istio", "Docker"],
                "ops_tools": ["Jenkins", "Git", "Grafana", "Gradle"]
            },
            "ops_deploy_experience_required_or_mentioned": "yes",
            "scale_traffic_platform_mentioned": "yes",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "Jenkins, Git, Docker, Kubernetes + Istio"
                }
            ]
        },
        "role_and_hiring_signals": {
            "hiring_summary": "DevOps Engineer (토스 소속), SRE & DevOps팀",
            "open_roles_mentioned": ["DevOps Engineer"],
            "employment_type": "full_time",
            "location": "unknown",
            "remote_hybrid_onsite": "unknown",
            "required_experience": "unknown",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "DevOps Engineer\n토스 소속\n정규직"
                }
            ]
        },
        "execution_culture_signals": {
            "summary": "unknown",
            "speed_vs_stability": "unknown",
            "prototype_vs_structure": "unknown",
            "business_impact_vs_tech_quality": "unknown",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "배포 과정을 혁신해요."
                }
            ]
        },
        "collaboration_culture_signals": {
            "summary": "SRE, devops, SE 간 업무 분담 및 협업 구조가 언급됨",
            "code_review_culture": "unknown",
            "documentation_culture": "unknown",
            "cross_functional_collaboration": "mentioned",
            "decision_making_process": "unknown",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "SE분들이 담당... devops는 ... 소프트웨어 영역들을 모두 책임지고 운영"
                }
            ]
        },
        "ownership_expectation_signals": {
            "summary": "장애 대응 시 root cause 분석 및 구조적 개선 책임, 오픈소스 수정/기여 언급",
            "problem_definition_expected": "unknown",
            "decision_making_expected": "unknown",
            "role_positioning": "owner",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "root cause 분석과 구조적 개선까지 책임지는 분"
                }
            ]
        },
        "growth_learning_culture_signals": {
            "summary": "기술 도입/검증 프로세스에서 작게 실험하고 측정하며 가설 검증 언급",
            "learning_support": "unknown",
            "new_tech_adoption": "unknown",
            "feedback_culture": "unknown",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "작게 실험하고 측정하면서 가설들을 검증"
                }
            ]
        },
        "work_environment_expectations": {
            "summary": "보안 규정 준수(전자금융감독규정) 및 보안엔지니어 협업 언급",
            "work_mode": "unknown",
            "wlb_vs_immersion": "unknown",
            "pace_intensity": "unknown",
            "oncall_or_shift": "unknown",
            "overtime_or_night_work": "unknown",
            "benefits_or_perks": [],
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "전자금융감독규정을 지키고... 보안엔지니어분들과 최대한 협업"
                }
            ]
        },
        "verification_needed_areas": {
            "missing_or_unmentioned": [
                "industry",
                "company summary/mission (company-wide)",
                "company official URLs",
                "work mode (remote/hybrid/onsite)",
                "work location (company-level)",
                "required experience range",
                "benefits/perks",
                "code review culture",
                "documentation culture",
                "decision making process"
            ],
            "needs_followup_questions": [
                "공식 회사 홈페이지/채용 페이지/기술블로그 URL을 제공할 수 있나요?",
                "근무 형태(원격/하이브리드/상주) 및 근무지는 어디인가요?",
                "경력 요건(연차 범위)과 직급/레벨 표기가 있나요?",
                "복지/혜택, 근무시간/유연근무 관련 공식 문구가 있나요?"
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
            "summary": "DevOps 관련 기술/도구 스택이 명시됨 (예: Kubernetes, Istio, Jenkins, Grafana 등)",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "Jenkins, Git, Docker, Kubernetes + Istio"
                }
            ],
            "subsignals": {
                "languages_frameworks_depth": 1,
                "infra_cloud_exposure": 2,
                "ops_deploy_monitoring_exposure": 2,
                "scale_platform_exposure": 1
            }
        },
        "execution_style_company": {
            "score": 1,
            "summary": "배포 과정 혁신 및 장애 대응을 위한 메트릭 도출 언급",
            "confidence": "low",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "배포 과정을 혁신해요."
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
            "summary": "devops/SRE/SE 간 업무 분담과 협업 구조 및 보안엔지니어 협업 언급",
            "confidence": "low",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "보안엔지니어분들과 최대한 협업"
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
            "summary": "장애 대응 시 root cause 분석과 구조적 개선 책임, 오픈소스 수정/기여 언급",
            "confidence": "medium",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "root cause 분석과 구조적 개선까지 책임"
                }
            ],
            "subsignals": {
                "problem_definition_involvement": 1,
                "decision_making": 0,
                "role_self_positioning": "owner"
            }
        },
        "growth_orientation_company": {
            "score": 1,
            "summary": "기술 도입/검증에서 실험-측정 기반 가설 검증 언급",
            "confidence": "low",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "작게 실험하고 측정하면서 가설들을 검증"
                }
            ],
            "subsignals": {
                "new_tech_adoption": 1,
                "self_directed_learning": 0,
                "feedback_loop": 0
            }
        },
        "work_expectation_company": {
            "score": 1,
            "summary": "금융서비스 운영 관련 규정 준수 및 보안 협업 언급",
            "confidence": "low",
            "evidence": [
                {
                    "doc_id": "job_posting",
                    "line_refs": ["unknown"],
                    "quote": "전자금융감독규정을 지키고"
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
        "notes": "라인 번호/공식 URL이 제공되지 않아 line_refs와 url은 unknown으로 처리함. 회사 공식 사이트 텍스트가 별도로 제공되지 않아 company-level 정보는 제한적으로만 채움."
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
    print(f"  - 채용 포지션: {saved['company_info_fields']['role_and_hiring_signals']['open_roles_mentioned']}")
    print(f"  - 기술 스택: {saved['company_info_fields']['technical_environment']['stack']['infra_cloud']}")
    print(f"  - technical_fit 점수: {saved['scoring_axes']['technical_fit_company']['score']}")
    print(f"  - ownership 점수: {saved['scoring_axes']['ownership_company']['score']}")

    # 3. 전체 목록 조회
    all_companies = await company_repository.get_all_companies()
    print(f"\n📋 전체 회사 수: {len(all_companies)}개")

    # DB 연결 종료
    await close_db()
    print("\n✅ 테스트 완료")


if __name__ == "__main__":
    asyncio.run(main())