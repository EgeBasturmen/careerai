import redis

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.config.settings import settings
from src.domains.health.schemas.health_schema import HealthResponse


class HealthService:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def check_health(
        self,
    ) -> HealthResponse:
        database_status = self._check_database()
        redis_status = self._check_redis()

        overall_status = (
            "ok"
            if database_status == "ok"
            and redis_status == "ok"
            else "degraded"
        )

        return HealthResponse(
            status=overall_status,
            app=settings.app_name,
            env=settings.app_env,
            database=database_status,
            redis=redis_status,
        )

    def _check_database(
        self,
    ) -> str:
        try:
            self.db.execute(
                text("SELECT 1")
            )
            return "ok"
        except Exception:
            return "error"

    def _check_redis(
        self,
    ) -> str:
        try:
            client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                socket_connect_timeout=2,
                socket_timeout=2,
            )

            client.ping()

            return "ok"

        except Exception:
            return "error"