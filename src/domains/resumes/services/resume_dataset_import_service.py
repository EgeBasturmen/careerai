import hashlib
import shutil
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from src.domains.resumes.repositories.resume_repository import (
    ResumeRepository,
)
from src.domains.resumes.schemas.resume_dataset_import_schema import (
    ResumeDatasetImportResult,
)
from src.infrastructure.queue.resume_tasks import (
    process_resume,
)


class ResumeDatasetImportService:
    SUPPORTED_EXTENSIONS = {
        ".pdf",
    }

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.repository = ResumeRepository(
            db,
        )

    def import_directory(
        self,
        *,
        dataset_directory: str,
        dataset_name: str,
        user_id: int,
        source: str = "kaggle",
        output_directory: str = (
            "uploads/resumes/datasets"
        ),
    ) -> ResumeDatasetImportResult:
        source_directory = Path(
            dataset_directory,
        )

        if not source_directory.exists():
            raise FileNotFoundError(
                "Resume dataset directory "
                f"not found: {source_directory}"
            )

        if not source_directory.is_dir():
            raise ValueError(
                "Resume dataset path must "
                "be a directory"
            )

        normalized_dataset_name = (
            dataset_name.strip()
        )

        if not normalized_dataset_name:
            raise ValueError(
                "Dataset name cannot be empty"
            )

        files = self._discover_files(
            source_directory,
        )

        destination_root = (
            Path(output_directory)
            / normalized_dataset_name
        )

        destination_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        imported_count = 0
        skipped_count = 0
        failed_count = 0

        resume_ids: list[int] = []
        errors: list[str] = []

        for source_file in files:
            try:
                file_hash = (
                    self._calculate_file_hash(
                        source_file,
                    )
                )

                existing_resume = (
                    self.repository
                    .get_by_file_hash(
                        file_hash=file_hash,
                        dataset_name=(
                            normalized_dataset_name
                        ),
                    )
                )

                if existing_resume is not None:
                    skipped_count += 1
                    continue

                dataset_category = (
                    self._resolve_category(
                        source_directory=(
                            source_directory
                        ),
                        source_file=source_file,
                    )
                )

                destination_path = (
                    self._copy_file(
                        source_file=source_file,
                        destination_root=(
                            destination_root
                        ),
                    )
                )

                resume = self.repository.create(
                    user_id=user_id,
                    original_filename=(
                        source_file.name
                    ),
                    storage_path=str(
                        destination_path
                    ),
                    file_hash=file_hash,
                    source=source,
                    dataset_name=(
                        normalized_dataset_name
                    ),
                    dataset_category=(
                        dataset_category
                    ),
                )

                process_resume.delay(
                    resume.id,
                )

                imported_count += 1
                resume_ids.append(
                    resume.id
                )

            except Exception as exc:
                failed_count += 1

                errors.append(
                    (
                        f"{source_file}: "
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    )
                )

        return ResumeDatasetImportResult(
            dataset_name=(
                normalized_dataset_name
            ),
            source=source,
            user_id=user_id,
            discovered_count=len(files),
            imported_count=imported_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            resume_ids=resume_ids,
            errors=errors,
        )

    def _discover_files(
        self,
        source_directory: Path,
    ) -> list[Path]:
        return sorted(
            file_path
            for file_path
            in source_directory.rglob("*")
            if (
                file_path.is_file()
                and file_path.suffix.lower()
                in self.SUPPORTED_EXTENSIONS
            )
        )

    def _resolve_category(
        self,
        *,
        source_directory: Path,
        source_file: Path,
    ) -> str | None:
        relative_parent = (
            source_file.parent.relative_to(
                source_directory
            )
        )

        if str(relative_parent) == ".":
            return None

        return relative_parent.parts[0]

    def _copy_file(
        self,
        *,
        source_file: Path,
        destination_root: Path,
    ) -> Path:
        safe_filename = (
            source_file.name
        )

        destination_path = (
            destination_root
            / (
                f"{uuid4().hex}_"
                f"{safe_filename}"
            )
        )

        shutil.copy2(
            source_file,
            destination_path,
        )

        return destination_path

    @staticmethod
    def _calculate_file_hash(
        file_path: Path,
    ) -> str:
        hash_calculator = (
            hashlib.sha256()
        )

        with file_path.open("rb") as file:
            for chunk in iter(
                lambda: file.read(
                    1024 * 1024
                ),
                b"",
            ):
                hash_calculator.update(
                    chunk
                )

        return (
            hash_calculator.hexdigest()
        )