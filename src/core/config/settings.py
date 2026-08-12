from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CareerAI"
    app_env: str = "development"
    debug: bool = True

    database_url: str
    gemini_api_key: str | None = None
    llm_provider: str = "fake"
    llm_timeout_seconds:int=20
    llm_max_retries: int = 2
    adzuna_app_id: str | None = None
    adzuna_app_key: str | None = None
    adzuna_country: str = "gb"
    adzuna_results_per_page: int = 20
    adzuna_request_timeout_seconds: int = 15
    embedding_provider: str = "fake"

    embedding_model_name: str = (
        "BAAI/bge-small-en-v1.5"
    )
    

    embedding_device: str = "cpu"

    embedding_batch_size: int = 32

    embedding_normalize: bool = True
    
    matching_skill_weight: float = 0.50
    matching_semantic_weight: float = 0.20
    matching_reranker_weight: float = 0.10
    matching_seniority_weight: float = 0.10
    matching_location_weight: float = 0.10

    matching_default_candidate_limit: int = 100
    matching_default_minimum_similarity: float = 0.20

    matching_low_skill_threshold: float = 15.0
    matching_low_semantic_threshold: float = 30.0
    matching_zero_skill_semantic_threshold: float = 45.0

    matching_low_relevance_cap: float = 20.0
    matching_zero_skill_cap: float = 30.0
    

    matching_algorithm_version: str = (
        "hybrid-v3-cross-encoder"
    )

    knowledge_reranker_enabled: bool = True

    knowledge_reranker_model_name: str = (
        "cross-encoder/ms-marco-MiniLM-L6-v2"
    )
    knowledge_retriever_name: str = "hybrid"

    knowledge_reranker_candidate_multiplier: int = 3

    knowledge_reranker_batch_size: int = 16

    knowledge_reranker_minimum_score: float = 0.0
    knowledge_retrieval_cache_enabled: bool = True

    knowledge_retrieval_cache_ttl_seconds: int = 300

    knowledge_retrieval_cache_redis_db: int = 1

    matching_reranker_enabled: bool = False

    matching_reranker_model_name: str = (
        "cross-encoder/ms-marco-MiniLM-L6-v2"
    )

    matching_reranker_batch_size: int = 16

    matching_reranker_candidate_limit: int = 50

    matching_reranker_result_limit: int = 20

    matching_reranker_minimum_score: float = 0.0


    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    backend_cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    matching_ml_shadow_enabled: bool = False

    matching_ml_model_path: str = (
        "artifacts/matching/models/"
        "baseline_match_model_v1.joblib"
    )
    postgres_db: str
    postgres_user: str
    postgres_password: str

    redis_host: str
    redis_port: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def is_development(
        self,
    ) -> bool:
        return self.app_env == "development"

    @property
    def is_production(
        self,
    ) -> bool:
        return self.app_env == "production"


settings = Settings()