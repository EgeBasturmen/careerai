from src.infrastructure.llm.base import LLMClient
from src.infrastructure.llm.prompt_loader import PromptLoader
from dataclasses import dataclass

@dataclass
class LLMSummaryResult:
    summary: str
    prompt_name: str
    prompt_version: str
    provider: str

class LLMSummaryAgent:
    PROMPT_PATH = (
        "src/infrastructure/llm/prompts/"
        "cv_improvement_summary.txt"
    )

    def __init__(
        self,
        llm_client: LLMClient,
    ):
        self.llm_client = llm_client
        self.prompt_loader = PromptLoader()

    def generate_summary(
        self,
        target_role: str | None,
        matched_skills: list[str],
        missing_skills: list[str],
        language:str="en",
    ) -> LLMSummaryResult:
        template = self.prompt_loader.load(
            self.PROMPT_PATH,
        )

        prompt = template.content.format(
            target_role=target_role,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            language=language,
        )

        try:
            summary = self.llm_client.generate(
                prompt=prompt,
                prompt_name=template.name,
                prompt_version=template.version,
            )
            if not summary or not summary.strip():
                summary = self._fallback_summary(
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                )

            provider = self.llm_client.provider_name

            return LLMSummaryResult(
                summary=summary,
                prompt_name=template.name,
                prompt_version=template.version,
                provider=provider,
            )

        except Exception:
            return LLMSummaryResult(
                summary=self._fallback_summary(
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    language=language,
                ),
                prompt_name=template.name,
                prompt_version=template.version,
                provider="fallback",
            )

    def _fallback_summary(
        self,
        matched_skills: list[str],
        missing_skills: list[str],
        language: str = "en",
    ) -> str:

        if language == "tr":
            if not matched_skills:
                return (
                    "Bu iş şu an zayıf bir eşleşme. "
                    "CV'niz bu rol için gerekli temel becerileri net şekilde göstermiyor."
                )

            if not missing_skills:
                return (
                    "Bu iş güçlü bir eşleşme. "
                    "CV'niz bu rol için gerekli ana becerileri zaten gösteriyor."
                )

            return (
                "Bu iş kısmi bir eşleşme. "
                "CV'niz bazı güçlü yönleri gösteriyor ancak eksik beceriler geliştirilmelidir."
            )
        if not matched_skills:
            return (
                "This job is currently a weak match. "
                "Your CV does not clearly show the core skills required for this role."
            )

        if not missing_skills:
            return (
                "This job is a strong match. "
                "Your CV already shows the main required skills for this role."
            )

        return (
            "This job is a partial match. "
            "Your CV shows some relevant strengths, but the missing skills should be improved."
        )
