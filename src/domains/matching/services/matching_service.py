from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.config.settings import settings
from src.domains.embeddings.clients.factory import (
    get_embedding_client,
)
from src.domains.embeddings.repositories.entity_embedding_repository import (
    EntityEmbeddingRepository,
)
from src.domains.embeddings.repositories.semantic_search_repository import (
    SemanticSearchRepository,
)
from src.domains.jobs.repositories.job_repository import (
    JobRepository,
)
from src.domains.matching.repositories.match_repository import (
    MatchRepository,
)
from src.domains.matching.schemas.matching_schema import (
    JobMatchResponse,
    ResumeMatchesResponse,
    MatchingConfigurationResponse,
    SavedMatchResponse,
    
)
from src.domains.matching.services.match_explanation_builder import (
    MatchExplanationBuilder,
)
from src.domains.matching.services.match_score_calculator import (
    MatchScoreCalculator,
)
from src.domains.resumes.repositories.resume_repository import (
    ResumeRepository,
)
from src.domains.skills.services.skill_normalizer import (
    SkillNormalizer,
)
from src.domains.skills.services.skill_ontology_service import (
    SkillOntologyService,
)
from src.domains.users.models.user import User
from pathlib import Path

from src.domains.matching.ml.match_model_predictor import (
    MatchModelPredictor,
)

from pathlib import Path

from src.core.logging.logger import logger
from src.domains.matching.ml.match_model_predictor import (
    MatchModelPredictor,
)
from src.domains.matching.ml.shadow_prediction_status import (
    ShadowPredictionStatus,
)
from src.domains.matching.rerankers.job_cross_encoder_reranker import (
    JobCrossEncoderReranker,
)
from src.domains.embeddings.builders.resume_text_builder import (
    ResumeTextBuilder,
)
class MatchingService:
    RESUME_ENTITY_TYPE = "resume"

    def __init__(
        self,
        db: Session,
    ):
        self.resume_repository = ResumeRepository(
            db,
        )

        self.job_repository = JobRepository(
            db,
        )

        self.match_repository = MatchRepository(
            db,
        )

        self.skill_normalizer = SkillNormalizer()
        self.skill_ontology = SkillOntologyService()

        self.score_calculator = MatchScoreCalculator()
        self.explanation_builder = (
            MatchExplanationBuilder()
        )

        self.embedding_client = (
            get_embedding_client()
        )

        self.entity_embedding_repository = (
            EntityEmbeddingRepository(
                db,
            )
        )

        self.semantic_search_repository = (
            SemanticSearchRepository(
                db,
            )
        )

        self.resume_text_builder = (
            ResumeTextBuilder()
        )

        self.job_reranker: (
            JobCrossEncoderReranker | None
        ) = None

        if settings.matching_reranker_enabled:
            self.job_reranker = (
                JobCrossEncoderReranker(
                    model_name=(
                        settings
                        .matching_reranker_model_name
                    ),
                    batch_size=(
                        settings
                        .matching_reranker_batch_size
                    ),
                )
            )

        self.ml_predictor: (
            MatchModelPredictor | None
        ) = None

        self.ml_predictor_status = (
            ShadowPredictionStatus.DISABLED
        )

        self.ml_predictor_error: str | None = None

        if settings.matching_ml_shadow_enabled:
            model_path = Path(
                settings.matching_ml_model_path,
            )

            if not model_path.exists():
                self.ml_predictor_status = (
                    ShadowPredictionStatus
                    .MODEL_NOT_FOUND
                )

                self.ml_predictor_error = (
                    "ML model artifact was not found: "
                    f"{model_path}"
                )

                logger.warning(
                    self.ml_predictor_error
                )

            else:
                try:
                    self.ml_predictor = (
                        MatchModelPredictor(
                            model_path=str(
                                model_path
                            ),
                        )
                    )

                    self.ml_predictor_status = (
                        ShadowPredictionStatus.READY
                    )

                except Exception as exc:
                    self.ml_predictor_status = (
                        ShadowPredictionStatus.FAILURE
                    )

                    self.ml_predictor_error = (
                        f"{type(exc).__name__}: {exc}"
                    )

                    logger.exception(
                        "Failed to load ML shadow model"
                    )

    def match_resume_to_jobs(
        self,
        current_user: User,
        resume_id: int,
        seniority: str | None = None,
        remote_type: str | None = None,
        location: str | None = None,
        limit: int = 20,
        offset: int = 0,
        candidate_limit: int | None = None,
        minimum_similarity: float | None = None,
    ) -> ResumeMatchesResponse:
        resolved_candidate_limit = (
            candidate_limit
            if candidate_limit is not None
            else settings.matching_default_candidate_limit
        )

        resolved_minimum_similarity = (
            minimum_similarity
            if minimum_similarity is not None
            else settings.matching_default_minimum_similarity
        )

        matching_configuration = (
            MatchingConfigurationResponse(
                algorithm_version=(
                    settings.matching_algorithm_version
                ),
                skill_weight=(
                    settings.matching_skill_weight
                ),
                semantic_weight=(
                    settings.matching_semantic_weight
                ),
                seniority_weight=(
                    settings.matching_seniority_weight
                ),
                location_weight=(
                    settings.matching_location_weight
                ),
                minimum_similarity=(
                    resolved_minimum_similarity
                ),
                reranker_weight=(
                    settings.matching_reranker_weight
                ),
                candidate_limit=(
                    resolved_candidate_limit
                ),
            )
        )

        resume = (
            self.resume_repository
            .get_by_id_and_user(
                resume_id=resume_id,
                user_id=current_user.id,
            )
        )

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        if not resume.parsed_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Resume has not been parsed yet"
                ),
            )

        resume_profile = resume.parsed_profile

        resume_embedding = (
            self.entity_embedding_repository
            .get_by_entity_and_model(
                entity_type=self.RESUME_ENTITY_TYPE,
                entity_id=resume.id,
                model_name=(
                    self.embedding_client.model_name
                ),
            )
        )

        if resume_embedding is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Resume embedding has not been "
                    "generated yet"
                ),
            )

        if (
            resume_embedding.dimension
            != self.embedding_client.embedding_dimension
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Resume embedding dimension does "
                    "not match the active model"
                ),
            )

        resume_vector = list(
            resume_embedding.embedding,
        )

        resume_skills = (
            self.skill_ontology.expand_skills(
                resume_profile.get(
                    "skills",
                    [],
                )
            )
        )

        semantic_candidates = (
            self.semantic_search_repository
            .find_similar_job_ids(
                query_vector=resume_vector,
                model_name=(
                    self.embedding_client.model_name
                ),
                candidate_limit=(
                    resolved_candidate_limit
                ),
                minimum_similarity=(
                    resolved_minimum_similarity
                ),
            )
        )

        if not semantic_candidates:
            return ResumeMatchesResponse(
                resume_id=resume.id,
                total_candidates=0,
                returned_count=0,
                limit=limit,
                offset=offset,
                configuration=(
                    matching_configuration
                ),
                matches=[],
            )

        candidate_job_ids = [
            job_id
            for job_id, _ in semantic_candidates
        ]

        semantic_similarities = {
            job_id: similarity
            for job_id, similarity in semantic_candidates
        }

        jobs = self.job_repository.list_by_ids(
            job_ids=candidate_job_ids,
            seniority=seniority,
            remote_type=remote_type,
            location=location,
        )

        reranker_raw_scores: dict[int, float] = {}
        reranker_normalized_scores: dict[int, float] = {}

        if (
            self.job_reranker is not None
            and jobs
        ):
            resume_text = (
                self.resume_text_builder.build(
                    resume_profile,
                )
            )

            reranker_candidate_limit = min(
                len(jobs),
                settings
                .matching_reranker_candidate_limit,
            )

            reranker_candidates = [
                (
                    job,
                    semantic_similarities.get(
                        job.id,
                        0.0,
                    ),
                )
                for job in jobs[
                    :reranker_candidate_limit
                ]
            ]

            reranked_results = (
                self.job_reranker.rerank(
                    query_text=resume_text,
                    jobs=reranker_candidates,
                    limit=(
                        settings
                        .matching_reranker_result_limit
                    ),
                    minimum_score=(
                        settings
                        .matching_reranker_minimum_score
                    ),
                )
            )

            jobs = [
                result.job
                for result in reranked_results
            ]

            reranker_raw_scores = {
                result.job.id: (
                    result.reranker_score
                )
                for result in reranked_results
            }

            reranker_normalized_scores = (
                self._normalize_reranker_scores(
                    reranker_raw_scores
                )
            )

        matches: list[JobMatchResponse] = []

        for job in jobs:
            required_skills = (
                job.required_skills
                or []
            )

            normalized_required_skills = {
                self._normalize_skill(
                    skill,
                )
                for skill in required_skills
            }

            matched_normalized_skills = (
                resume_skills
                & normalized_required_skills
            )

            matched_skills = [
                skill
                for skill in required_skills
                if self._normalize_skill(
                    skill,
                )
                in matched_normalized_skills
            ]

            missing_skills = [
                skill
                for skill in required_skills
                if self._normalize_skill(
                    skill,
                )
                not in matched_normalized_skills
            ]

            skill_score = (
                self.score_calculator
                .calculate_skill_score(
                    matched_count=len(
                        matched_skills
                    ),
                    required_count=len(
                        required_skills
                    ),
                )
            )

            semantic_similarity = (
                semantic_similarities.get(
                    job.id,
                )
            )

            semantic_score = (
                self.score_calculator
                .calculate_semantic_score(
                    semantic_similarity,
                )
            )

            seniority_score = (
                self.score_calculator
                .calculate_seniority_score(
                    resume_profile=resume_profile,
                    job_seniority=job.seniority,
                )
            )

            location_score = (
                self.score_calculator
                .calculate_location_score(
                    resume_profile=resume_profile,
                    job_location=job.location,
                    remote_type=job.remote_type,
                )
            )

            reranker_raw_score = (
                reranker_raw_scores.get(
                    job.id,
                )
            )

            normalized_reranker_score = (
                reranker_normalized_scores.get(
                    job.id,
                    0.0,
                )
            )

            final_score = (
                self.score_calculator
                .calculate_final_score(
                    skill_score=skill_score,
                    semantic_score=semantic_score,
                    reranker_score=(
                        normalized_reranker_score
                    ),
                    seniority_score=seniority_score,
                    location_score=location_score,
                )
            )

            final_score = (
                self.score_calculator
                .apply_relevance_gate(
                    final_score=final_score,
                    skill_score=skill_score,
                    semantic_score=semantic_score,
                )
            )

            ml_prediction = None

            ml_prediction_status = (
                self.ml_predictor_status.value
            )

            ml_prediction_error = (
                self.ml_predictor_error
            )

            if self.ml_predictor is not None:
                ml_feature_values = {
                    "skill_score": skill_score,
                    "semantic_score": semantic_score,
                    "seniority_score": seniority_score,
                    "location_score": location_score,
                    "matched_skill_count": len(
                        matched_skills
                    ),
                    "missing_skill_count": len(
                        missing_skills
                    ),
                    "required_skill_count": len(
                        required_skills
                    ),
                }

                if (
                    "match_score"
                    in self.ml_predictor.feature_columns
                ):
                    ml_feature_values[
                        "match_score"
                    ] = final_score

                try:
                    ml_prediction = (
                        self.ml_predictor.predict(
                            feature_values=(
                                ml_feature_values
                            ),
                        )
                    )

                    ml_prediction_status = (
                        ShadowPredictionStatus
                        .SUCCESS
                        .value
                    )

                    ml_prediction_error = None

                except Exception as exc:
                    ml_prediction_status = (
                        ShadowPredictionStatus
                        .FAILURE
                        .value
                    )

                    ml_prediction_error = (
                        f"{type(exc).__name__}: {exc}"
                    )[:1000]

                    logger.exception(
                        "ML shadow prediction failed "
                        "for resume_id=%s job_id=%s",
                        resume.id,
                        job.id,
                    )

            explanation = (
                self.explanation_builder.build(
                    final_score=final_score,
                    skill_score=skill_score,
                    semantic_score=semantic_score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                )
            )

            score_breakdown = {
                "skill_score": round(
                    skill_score,
                    2,
                ),
                "semantic_score": round(
                    semantic_score,
                    2,
                ),
                "seniority_score": round(
                    seniority_score,
                    2,
                ),
                "location_score": round(
                    location_score,
                    2,
                ),
                "reranker_raw_score": (
                    round(
                        reranker_raw_score,
                        6,
                    )
                    if reranker_raw_score is not None
                    else None
                ),
                "reranker_score": round(
                    normalized_reranker_score,
                    2,
                ),
                "matched_skill_count": len(
                    matched_skills
                ),
                "missing_skill_count": len(
                    missing_skills
                ),
                "required_skill_count": len(
                    required_skills
                ),
            }

            rounded_final_score = round(
                final_score,
                2,
            )

            self.match_repository.upsert(
                resume_id=resume.id,
                job_id=job.id,
                match_score=rounded_final_score,
                score_breakdown=score_breakdown,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                algorithm_version=(
                    settings.matching_algorithm_version
                ),
                ml_predicted_relevance=(
                    ml_prediction.predicted_relevance
                    if ml_prediction
                    else None
                ),
                ml_predicted_grade=(
                    ml_prediction.predicted_grade
                    if ml_prediction
                    else None
                ),
                ml_model_name=(
                    ml_prediction.model_name
                    if ml_prediction
                    else None
                ),
                ml_model_version=(
                    ml_prediction.model_version
                    if ml_prediction
                    else None
                ),
                ml_feature_set_identifier=(
                    ml_prediction.feature_set_identifier
                    if ml_prediction
                    else None
                ),
                ml_prediction_status=(
                    ml_prediction_status
                ),
                ml_prediction_error=(
                    ml_prediction_error
                ),
            )

            matches.append(
                JobMatchResponse(
                    job_id=job.id,
                    title=job.title,
                    company_name=(
                        job.company_name
                    ),
                    match_score=(
                        rounded_final_score
                    ),
                    score_breakdown=(
                        score_breakdown
                    ),
                    matched_skills=(
                        matched_skills
                    ),
                    missing_skills=(
                        missing_skills
                    ),
                    explanation=explanation,
                )
            )

        matches.sort(
            key=lambda item: item.match_score,
            reverse=True,
        )

        total_candidates = len(
            matches
        )

        paginated_matches = matches[
            offset: offset + limit
        ]

        return ResumeMatchesResponse(
            resume_id=resume.id,
            total_candidates=total_candidates,
            returned_count=len(
                paginated_matches
            ),
            limit=limit,
            offset=offset,
            configuration=(
                matching_configuration
            ),
            matches=paginated_matches,
        )

    def get_saved_matches(
        self,
        current_user: User,
        resume_id: int,
        
    ) -> list[SavedMatchResponse]:
        resume = (
            self.resume_repository
            .get_by_id_and_user(
                resume_id=resume_id,
                user_id=current_user.id,
            )
        )

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        matches = (
            self.match_repository
            .list_by_resume(
                resume_id=resume.id,
            )
        )

        return [
            SavedMatchResponse.model_validate(
                match,
            )
            for match in matches
        ]

    def _normalize_reranker_scores(
        self,
        scores: dict[int, float],
    ) -> dict[int, float]:
        if not scores:
            return {}

        minimum_score = min(
            scores.values()
        )

        maximum_score = max(
            scores.values()
        )

        score_range = (
            maximum_score - minimum_score
        )

        if score_range <= 0:
            return {
                job_id: 100.0
                for job_id in scores
            }

        return {
            job_id: (
                (
                    raw_score
                    - minimum_score
                )
                / score_range
            ) * 100
            for job_id, raw_score
            in scores.items()
        }

    def _normalize_skill(
        self,
        skill: str,
    ) -> str:
        return self.skill_normalizer.normalize(
            skill,
        )