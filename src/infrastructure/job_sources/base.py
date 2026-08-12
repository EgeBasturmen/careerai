from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ExternalJob:
    external_id: str
    title: str
    company_name: str
    description: str

    location: str | None = None
    remote_type: str | None = None
    seniority: str | None = None

    source_url: str | None = None


class JobSourceClient(ABC):
    @property
    @abstractmethod
    def source_name(
        self,
    ) -> str:
        pass

    @abstractmethod
    def fetch_jobs(
        self,
    ) -> list[ExternalJob]:
        pass