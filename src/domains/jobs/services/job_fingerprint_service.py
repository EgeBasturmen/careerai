import hashlib

from src.domains.jobs.services.job_normalizer import (
    JobNormalizer,
)


class JobFingerprintService:
    def __init__(
        self,
    ):
        self.normalizer = JobNormalizer()

    def generate(
        self,
        title: str,
        company_name: str,
        location: str | None,
        description: str,
    ) -> str:
        normalized_title = (
            self.normalizer.normalize_title(title)
        )

        normalized_company = (
            self.normalizer.normalize_company_name(
                company_name,
            )
        )

        normalized_location = (
            self.normalizer.normalize_location(location)
        )

        normalized_description = (
            self.normalizer.normalize_text(description)
        )

        description_sample = normalized_description[:1000]

        raw_fingerprint = "|".join(
            [
                normalized_title,
                normalized_company,
                normalized_location,
                description_sample,
            ]
        )

        return hashlib.sha256(
            raw_fingerprint.encode("utf-8")
        ).hexdigest()