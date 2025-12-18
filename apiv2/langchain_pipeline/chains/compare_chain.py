"""
컬쳐핏 비교 체인

파이프라인 흐름:
회사 컬쳐핏 JSON + 구직자 컬쳐핏 JSON → 비교 분석 → 매칭 점수 출력

AI팀 프롬프트 적용 (matching_prompt_gemini01.txt)
"""

import logging
import json
import re
from typing import Any, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from apiv2.langchain_pipeline.config import GOOGLE_API_KEY
from apiv2.langchain_pipeline.utils.db_handler import DatabaseHandler
from apiv2.langchain_pipeline.utils.schema_loader import get_schema_for_prompt
from apiv2.langchain_pipeline.prompts import culture_compare

logger = logging.getLogger(__name__)


def parse_json_with_markdown(response) -> dict:
    """마크다운 코드블록이 포함된 JSON 파싱 (robust)"""
    original_response = response  # 디버깅용 원본 저장

    # AIMessage 또는 content 속성이 있는 객체 처리
    if hasattr(response, 'content'):
        text = response.content
    else:
        text = str(response)

    text = text.strip()

    # ```json ... ``` 또는 ``` ... ``` 제거
    if "```json" in text:
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            text = match.group(1)
    elif "```" in text:
        match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            text = match.group(1)

    # JSON 객체 시작점 찾기
    first_brace = text.find('{')
    if first_brace != -1:
        text = text[first_brace:]

    # JSON 객체 끝점 찾기
    last_brace = text.rfind('}')
    if last_brace != -1:
        text = text[:last_brace + 1]

    # Trailing comma 제거 (LLM이 자주 만드는 오류)
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)

    # JSON 파싱 시도 (여러 방법)
    try:
        # 1차 시도: 표준 json.loads
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    try:
        # 2차 시도: raw_decode (extra data 무시)
        decoder = json.JSONDecoder()
        result, _ = decoder.raw_decode(text)
        return result
    except json.JSONDecodeError as e:
        logger.error("=" * 70)
        logger.error(f"[compare_chain] JSON 파싱 실패: {e}")
        logger.error("=" * 70)
        logger.error(f"에러 위치: line {e.lineno}, column {e.colno}")
        logger.error("-" * 70)

        # 에러 위치 주변 텍스트 표시
        lines = text.split('\n')
        error_line = e.lineno - 1
        start_line = max(0, error_line - 2)
        end_line = min(len(lines), error_line + 3)

        logger.error("에러 위치 주변:")
        for i in range(start_line, end_line):
            prefix = ">>> " if i == error_line else "    "
            line_content = lines[i][:200] + "..." if len(lines[i]) > 200 else lines[i]
            logger.error(f"{prefix}{i+1:4d} | {line_content}")

        logger.error("-" * 70)
        logger.error(f"원본 응답 타입: {type(original_response).__name__}")
        logger.error(f"처리된 텍스트 길이: {len(text)} chars")
        logger.error("=" * 70)
        raise


class CultureCompareChain:
    """컬쳐핏 비교 체인"""

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.0,
        save_to_db: bool = True
    ):
        """
        Args:
            model_name: Gemini 모델명
            temperature: 생성 온도
            save_to_db: DB 저장 여부
        """
        logger.info(f"Initializing CultureCompareChain with model='{model_name}', temperature={temperature}, save_to_db={save_to_db}")
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=GOOGLE_API_KEY,
            temperature=temperature,
        )
        self.save_to_db = save_to_db
        self.db = DatabaseHandler() if save_to_db else None

        # 프롬프트 템플릿 설정
        self._setup_prompts()
        logger.info("CultureCompareChain initialized successfully.")

    def _setup_prompts(self):
        """프롬프트 템플릿 초기화"""
        self.compare_prompt = ChatPromptTemplate.from_messages([
            ("system", culture_compare.SYSTEM_MESSAGE),
            ("human", culture_compare.HUMAN_MESSAGE_TEMPLATE),
        ])

        self.json_parser = JsonOutputParser()

    async def compare(
        self,
        company_profile: dict[str, Any],
        developer_profile: dict[str, Any]
    ) -> dict[str, Any]:
        """
        회사-구직자 컬쳐핏 비교

        Args:
            company_profile: 회사 컬쳐핏 분석 결과
            developer_profile: 구직자 프로필 분석 결과

        Returns:
            비교 분석 결과 (6축 매칭 점수, overall score 등)
        """
        # 스키마 로드
        schema = get_schema_for_prompt("matching_schema")

        chain = self.compare_prompt | self.llm

        response = await chain.ainvoke({
            "company_profile": json.dumps(company_profile, ensure_ascii=False, indent=2),
            "developer_profile": json.dumps(developer_profile, ensure_ascii=False, indent=2),
            "output_schema": schema,
        })

        return parse_json_with_markdown(response)

    async def run(
        self,
        company_profile: dict[str, Any],
        developer_profile: dict[str, Any],
        company_name: Optional[str] = None,
        developer_name: Optional[str] = None
    ) -> dict[str, Any]:
        """
        전체 비교 파이프라인 실행

        Args:
            company_profile: 회사 컬쳐핏 분석 결과
            developer_profile: 구직자 프로필 분석 결과
            company_name: 회사명 (메타데이터용)
            developer_name: 구직자명 (메타데이터용)

        Returns:
            최종 비교 결과 (6축 매칭 + overall score)
        """
        import time
        total_start = time.time()

        _company_name = company_name or company_profile.get("_meta", {}).get("company_name", "unknown")
        _developer_name = developer_name or developer_profile.get("profile_meta", {}).get("candidate_name", "unknown")

        logger.info(f"🔄 [Match] 매칭 분석 시작")
        logger.info(f"   회사: {_company_name}")
        logger.info(f"   지원자: {_developer_name}")

        # 1. 비교 분석
        step_start = time.time()
        logger.info("🔄 [Match] 1/1 LLM 매칭 분석 중...")
        comparison = await self.compare(company_profile, developer_profile)
        logger.info(f"🔄 [Match] 1/1 LLM 분석 완료 ({time.time() - step_start:.1f}초)")

        # 메타데이터 추가
        result = {
            "_meta": {
                "company_name": _company_name,
                "developer_name": _developer_name,
            },
            **comparison,
        }

        # 2. DB 저장 (옵션)
        if self.save_to_db and self.db:
            doc_id = self.db.save_comparison_result(result)
            result["_id"] = doc_id
            logger.info(f"🔄 [Match] DB 저장 완료: {doc_id}")

        logger.info(f"🔄 [Match] ✅ 매칭 분석 완료! 총 소요시간: {time.time() - total_start:.1f}초")
        return result

    async def run_from_db(
        self,
        company_name: str,
        developer_name: str
    ) -> dict[str, Any]:
        """
        DB에서 프로필 로드 후 비교

        Args:
            company_name: 회사명
            developer_name: 구직자명

        Returns:
            비교 결과

        Raises:
            ValueError: 프로필을 찾을 수 없는 경우
        """
        if not self.db:
            raise ValueError("DB 핸들러가 초기화되지 않았습니다.")

        company_profile = self.db.get_company_profile(company_name)
        if not company_profile:
            raise ValueError(f"회사 프로필을 찾을 수 없습니다: {company_name}")

        developer_profile = self.db.get_applicant_profile(developer_name)
        if not developer_profile:
            raise ValueError(f"구직자 프로필을 찾을 수 없습니다: {developer_name}")

        return await self.run(
            company_profile=company_profile,
            developer_profile=developer_profile,
            company_name=company_name,
            developer_name=developer_name
        )

    def close(self):
        """리소스 정리"""
        if self.db:
            self.db.close()
