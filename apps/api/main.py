from fastapi import FastAPI, Depends

from apps.api.routes.auth_routes import router as auth_router
from src.core.config.settings import settings
from src.core.logging.logger import logger
from apps.api.routes.resume_routes import (
    router as resume_router,
)
from apps.api.routes.job_routes import router as job_router

from apps.api.routes.matching_routes import (
    router as matching_router,
)
from apps.api.routes.cv_improvement_routes import (
    router as cv_improvement_router,
)
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.database.session import get_db
from src.domains.health.schemas.health_schema import HealthResponse
from src.domains.health.services.health_service import HealthService
from src.core.exceptions.handlers import (
    http_exception_handler,
    unhandled_exception_handler,
)
from apps.api.middleware.request_logging import (
    request_logging_middleware,
)
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routes.semantic_matching_routes import (
    router as semantic_matching_router,
)
from apps.api.routes.matching_evaluation_routes import (
    router as matching_evaluation_router,
)
from apps.api.routes.match_feedback_routes import (
    router as match_feedback_router,
)
from apps.api.routes.ml_shadow_routes import (
    router as ml_shadow_router,
)
from apps.api.routes.knowledge_routes import (
    router as knowledge_router,
)
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,

    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(
        request_logging_middleware
    )
    app.add_exception_handler(
        HTTPException,
        http_exception_handler,
    )

    app.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )
    

    app.include_router(auth_router)
    app.include_router(
        resume_router,
    )
    app.include_router(job_router)
    app.include_router(matching_router)
    app.include_router(cv_improvement_router)
    app.include_router(
        semantic_matching_router,
    )
    app.include_router(
        matching_evaluation_router,
    )   
    app.include_router(
        match_feedback_router,
    )
    app.include_router(
        ml_shadow_router,
    )
    app.include_router(
        knowledge_router,
    )
    
    
    

    @app.get(
        "/health",
        response_model=HealthResponse,
    )
    def health_check(
        db: Session = Depends(get_db),
    ):
        logger.info("Health check requested")

        service = HealthService(db)

        return service.check_health()

    return app


app = create_app()

