from src.domains.cv_improvement.schemas.cv_improvement_schema import (
    ResumeAnalysisResult,
)


class ResumeAnalyzerAgent:
    def analyze(
        self,
        resume_profile: dict,
    ) -> ResumeAnalysisResult:
        return ResumeAnalysisResult(
            skills=resume_profile.get("skills", []),
            target_role=resume_profile.get("target_role"),
            seniority=resume_profile.get("seniority"),
        )