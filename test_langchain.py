"""
LangChain 파이프라인 빠른 테스트 스크립트

실행: python test_langchain.py
"""

import asyncio
import sys

def test_imports():
    """1. Import 테스트"""
    print("=" * 50)
    print("1. Import 테스트")
    print("=" * 50)

    try:
        from apiv2.langchain_pipeline.config import (
            GOOGLE_API_KEY, MONGODB_URI, S3_BUCKET_NAME,
            AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
        )
        print(f"   GOOGLE_API_KEY: {'설정됨' if GOOGLE_API_KEY else '❌ 미설정'}")
        print(f"   MONGODB_URI: {MONGODB_URI[:30]}...")
        print(f"   S3_BUCKET_NAME: {S3_BUCKET_NAME or '❌ 미설정'}")
        print(f"   AWS_ACCESS_KEY_ID: {'설정됨' if AWS_ACCESS_KEY_ID else '❌ 미설정'}")
        print(f"   AWS_SECRET_ACCESS_KEY: {'설정됨' if AWS_SECRET_ACCESS_KEY else '❌ 미설정'}")
        print("✅ Config import 성공\n")
    except Exception as e:
        print(f"❌ Config import 실패: {e}\n")
        return False

    try:
        from apiv2.langchain_pipeline.chains.company_chain import CompanyAnalysisChain
        print("✅ CompanyAnalysisChain import 성공")
    except Exception as e:
        print(f"❌ CompanyAnalysisChain import 실패: {e}")
        return False

    try:
        from apiv2.langchain_pipeline.chains.applicant_chain import ApplicantAnalysisChain
        print("✅ ApplicantAnalysisChain import 성공")
    except Exception as e:
        print(f"❌ ApplicantAnalysisChain import 실패: {e}")
        return False

    try:
        from apiv2.langchain_pipeline.chains.compare_chain import CultureCompareChain
        print("✅ CultureCompareChain import 성공")
    except Exception as e:
        print(f"❌ CultureCompareChain import 실패: {e}")
        return False

    try:
        from apiv2.langchain_pipeline.utils.db_handler import DatabaseHandler
        print("✅ DatabaseHandler import 성공")
    except Exception as e:
        print(f"❌ DatabaseHandler import 실패: {e}")
        return False

    print()
    return True


def test_db_connection():
    """2. MongoDB 연결 테스트"""
    print("=" * 50)
    print("2. MongoDB 연결 테스트")
    print("=" * 50)

    try:
        from apiv2.langchain_pipeline.utils.db_handler import DatabaseHandler

        db = DatabaseHandler()
        # ping 테스트
        db.client.admin.command('ping')
        print("✅ MongoDB 연결 성공")

        # 컬렉션 확인
        collections = db.db.list_collection_names()
        print(f"   컬렉션 목록: {collections}")

        db.close()
        print()
        return True
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}\n")
        return False


def test_chain_init():
    """3. Chain 초기화 테스트 (save_to_db=False로 DB 없이)"""
    print("=" * 50)
    print("3. Chain 초기화 테스트")
    print("=" * 50)

    try:
        from apiv2.langchain_pipeline.chains.company_chain import CompanyAnalysisChain
        chain = CompanyAnalysisChain(save_to_db=False)
        print("✅ CompanyAnalysisChain 초기화 성공")
        chain.close()
    except Exception as e:
        print(f"❌ CompanyAnalysisChain 초기화 실패: {e}")
        return False

    try:
        from apiv2.langchain_pipeline.chains.applicant_chain import ApplicantAnalysisChain
        chain = ApplicantAnalysisChain(save_to_db=False)
        print("✅ ApplicantAnalysisChain 초기화 성공")
        chain.close()
    except Exception as e:
        print(f"❌ ApplicantAnalysisChain 초기화 실패: {e}")
        return False

    try:
        from apiv2.langchain_pipeline.chains.compare_chain import CultureCompareChain
        chain = CultureCompareChain(save_to_db=False)
        print("✅ CultureCompareChain 초기화 성공")
        chain.close()
    except Exception as e:
        print(f"❌ CultureCompareChain 초기화 실패: {e}")
        return False

    print()
    return True


async def test_company_analysis_quick():
    """4. 회사 분석 실제 테스트 (선택)"""
    print("=" * 50)
    print("4. 회사 분석 실제 테스트 (토스 채용공고)")
    print("=" * 50)

    try:
        from apiv2.langchain_pipeline.chains.company_chain import CompanyAnalysisChain

        chain = CompanyAnalysisChain(save_to_db=False)

        # 토스 채용공고 테스트
        test_url = "https://toss.im/career/jobs/4829381"
        print(f"   테스트 URL: {test_url}")
        print("   분석 중... (1-2분 소요)")

        result = await chain.run(test_url)

        print(f"✅ 회사 분석 성공!")
        print(f"   회사명: {result.get('_meta', {}).get('company_name', 'N/A')}")
        print(f"   결과 키: {list(result.keys())}")

        chain.close()
        print()
        return True
    except Exception as e:
        print(f"❌ 회사 분석 실패: {e}\n")
        return False


def main():
    print("\n" + "=" * 50)
    print("  LangChain 파이프라인 테스트")
    print("=" * 50 + "\n")

    results = []

    # 1. Import 테스트
    results.append(("Import", test_imports()))

    # 2. DB 연결 테스트
    results.append(("MongoDB", test_db_connection()))

    # 3. Chain 초기화 테스트
    results.append(("Chain Init", test_chain_init()))

    # 결과 요약
    print("=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {name}: {status}")

    # 실제 분석 테스트 여부 확인
    if all(r[1] for r in results):
        print("\n기본 테스트 모두 통과!")

        if len(sys.argv) > 1 and sys.argv[1] == "--full":
            print("\n--full 옵션: 실제 회사 분석 테스트 실행")
            asyncio.run(test_company_analysis_quick())
        else:
            print("실제 분석 테스트를 하려면: python test_langchain.py --full")
    else:
        print("\n❌ 일부 테스트 실패. 위 에러 메시지를 확인하세요.")


if __name__ == "__main__":
    main()