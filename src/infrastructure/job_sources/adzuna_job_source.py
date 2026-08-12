from typing import Any

import httpx

from src.core.config.settings import settings
from src.infrastructure.job_sources.base import (
    ExternalJob,
    JobSourceClient,
)


class AdzunaJobSource(JobSourceClient):
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(
        self,
        query: str = "python developer",
        location: str | None = None,
        page: int = 1,
    ):
        if not settings.adzuna_app_id:
            raise ValueError(
                "ADZUNA_APP_ID is not configured"
            )

        if not settings.adzuna_app_key:
            raise ValueError(
                "ADZUNA_APP_KEY is not configured"
            )

        self.query = query
        self.location = location
        self.page = page

    @property
    def source_name(
        self,
    ) -> str:
        return "adzuna"

    def fetch_jobs(
        self,
    ) -> list[ExternalJob]:
        response = httpx.get(
            self._build_url(),
            params=self._build_params(),
            timeout=settings.adzuna_request_timeout_seconds,
        )

        response.raise_for_status()

        payload = response.json()
        raw_jobs = payload.get("results", [])

        return [
            self._map_job(raw_job)
            for raw_job in raw_jobs
        ]

    def _build_url(
        self,
    ) -> str:
        return (
            f"{self.BASE_URL}/"
            f"{settings.adzuna_country}/search/"
            f"{self.page}"
        )

    def _build_params(
        self,
    ) -> dict[str, str | int]:
        params: dict[str, str | int] = {
            "app_id": settings.adzuna_app_id,
            "app_key": settings.adzuna_app_key,
            "results_per_page": (
                settings.adzuna_results_per_page
            ),
            "what": self.query,
            "content-type": "application/json",
        }

        if self.location:
            params["where"] = self.location

        return params

    def _map_job(
        self,
        raw_job: dict[str, Any],
    ) -> ExternalJob:
        company_data = raw_job.get("company") or {}
        location_data = raw_job.get("location") or {}

        external_id = str(
            raw_job.get("id") or ""
        )

        if not external_id:
            raise ValueError(
                "Adzuna job does not contain an id"
            )

        title = str(
            raw_job.get("title") or ""
        ).strip()

        description = str(
            raw_job.get("description") or ""
        ).strip()

        company_name = str(
            company_data.get("display_name")
            or "Unknown Company"
        ).strip()

        location = self._extract_location(
            location_data
        )

        return ExternalJob(
            external_id=external_id,
            title=title or "Untitled Job",
            company_name=company_name,
            description=description,
            location=location,
            remote_type=self._detect_remote_type(
                title=title,
                description=description,
            ),
            seniority=None,
            source_url=raw_job.get("redirect_url"),
        )

    def _extract_location(
        self,
        location_data: dict[str, Any],
    ) -> str | None:
        display_name = location_data.get(
            "display_name"
        )

        if display_name:
            return str(display_name)

        area = location_data.get("area")

        if isinstance(area, list) and area:
            return ", ".join(
                str(item)
                for item in area
            )

        return None

    def _detect_remote_type(
        self,
        title: str,
        description: str,
    ) -> str | None:
        searchable_text = (
            f"{title} {description}"
        ).lower()

        if any(
            keyword in searchable_text
            for keyword in (
                "fully remote",
                "remote role",
                "work from home",
            )
        ):
            return "remote"

        if "hybrid" in searchable_text:
            return "hybrid"

        return None