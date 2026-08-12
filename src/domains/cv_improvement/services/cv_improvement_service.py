from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.domains.cv_improvement.agents.improvement_agent import (
    ImprovementAgent,
)
from src.domains.cv_improvement.agents.recommendation_agent import (
    RecommendationAgent,
)
from src.domains.cv_improvement.agents.resume_analyzer_agent import (
    ResumeAnalyzerAgent,
)
from src.domains.cv_improvement.agents.skill_gap_agent import (
    SkillGapAgent,
)
from src.domains.cv_improvement.agents.llm_summary_agent import (
    LLMSummaryAgent,
)


from src.infrastructure.llm.llm_factory import get_llm_client

from src.domains.cv_improvement.agents.strength_agent import (
    StrengthAgent,
)
from src.domains.cv_improvement.schemas.cv_improvement_schema import (
    CVImprovementResponse,
    SavedCVImprovementResponse,
    JobSummary,
    LLMMetadata,
)
from src.domains.jobs.repositories.job_repository import JobRepository
from src.domains.resumes.repositories.resume_repository import (
    ResumeRepository,
)
from src.domains.users.models.user import User

from src.domains.cv_improvement.agents.rewrite_suggestion_agent import (
    RewriteSuggestionAgent,
)
from src.domains.cv_improvement.repositories.cv_improvement_repository import (
    CVImprovementRepository,
)

class CVImprovementService:
    def __init__(
        self,
        db: Session,
    ):
        self.cv_improvement_repository = CVImprovementRepository(db)
        self.llm_summary_agent = LLMSummaryAgent(
            llm_client=get_llm_client(),
        )

        self.rewrite_suggestion_agent = RewriteSuggestionAgent()
        self.resume_repository = ResumeRepository(db)
        self.job_repository = JobRepository(db)

        self.resume_analyzer_agent = ResumeAnalyzerAgent()
        self.skill_gap_agent = SkillGapAgent()
        self.strength_agent = StrengthAgent()
        self.improvement_agent = ImprovementAgent()
        self.recommendation_agent = RecommendationAgent()

    def improve_for_job(
        self,
        current_user: User,
        resume_id: int,
        job_id: int,
        language:str="en",
    ) -> CVImprovementResponse:
        resume = self.resume_repository.get_by_id_and_user(
            resume_id=resume_id,
            user_id=current_user.id,
        )

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        if not resume.parsed_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume has not been parsed yet",
            )

        job = self.job_repository.get_by_id(
            job_id,
        )

        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        resume_analysis = self.resume_analyzer_agent.analyze(
            resume_profile=resume.parsed_profile,
        )

        skill_gap = self.skill_gap_agent.analyze(
            resume_skills=resume_analysis.skills,
            job_required_skills=job.required_skills or [],
        )

        strengths = self.strength_agent.analyze(
            matched_skills=skill_gap.matched_skills,
        )

        suggestions = self.improvement_agent.generate(
            missing_skills=skill_gap.missing_skills,
            matched_skills=skill_gap.matched_skills,
            language=language,
        )

        refined_suggestions = self.recommendation_agent.refine(
            suggestions=suggestions,
        )

        llm_summary_result = self.llm_summary_agent.generate_summary(
            target_role=resume_analysis.target_role,
            matched_skills=skill_gap.matched_skills,
            missing_skills=skill_gap.missing_skills,
            language=language,
        )

        summary = llm_summary_result.summary

        llm_metadata = LLMMetadata(
            provider=llm_summary_result.provider,
            prompt_name=llm_summary_result.prompt_name,
            prompt_version=llm_summary_result.prompt_version,
        )
        rewrite_suggestions = self.rewrite_suggestion_agent.generate(
            matched_skills=skill_gap.matched_skills,
            missing_skills=skill_gap.missing_skills,
            target_role=resume_analysis.target_role,
            language=language,
        )
        job_summary = JobSummary(
            job_id=job.id,
            title=job.title,
            company_name=job.company_name,
            seniority=job.seniority,
            required_skills=job.required_skills or [],
        )      
        response = CVImprovementResponse(
            resume_id=resume.id,
            job_id=job.id,
            summary=summary,
            resume_analysis=resume_analysis,
            skill_gap=skill_gap,
            strengths=strengths,
            language=language,
            llm_metadata=llm_metadata,
            suggestions=refined_suggestions,
            rewrite_suggestions=rewrite_suggestions,
            job_summary=job_summary,
        )
        self.cv_improvement_repository.upsert(
            resume_id=resume.id,
            job_id=job.id,
            language=language,
            result=response.model_dump(),
        )
        return response
    
    def get_saved_improvements(
        self,
        current_user: User,
        resume_id: int,
        language:str,
    ) -> list[SavedCVImprovementResponse]:
        resume = self.resume_repository.get_by_id_and_user(
            resume_id=resume_id,
            user_id=current_user.id,
        )

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        improvements = self.cv_improvement_repository.list_by_resume(
            resume_id=resume.id,
            language=language,
        )

        return [
            SavedCVImprovementResponse.model_validate(improvement)
            for improvement in improvements
        ]

