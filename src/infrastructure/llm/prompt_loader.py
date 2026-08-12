from dataclasses import dataclass
from pathlib import Path


@dataclass
class PromptTemplate:
    name: str
    version: str
    content: str


class PromptLoader:
    def load(
        self,
        prompt_path: str,
    ) -> PromptTemplate:
        path = Path(prompt_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_path}"
            )

        raw_content = path.read_text(
            encoding="utf-8",
        )

        name = "unknown"
        version = "unknown"

        content_lines: list[str] = []

        for line in raw_content.splitlines():
            if line.startswith("# prompt_name:"):
                name = line.replace(
                    "# prompt_name:",
                    "",
                ).strip()
                continue

            if line.startswith("# prompt_version:"):
                version = line.replace(
                    "# prompt_version:",
                    "",
                ).strip()
                continue

            content_lines.append(line)

        return PromptTemplate(
            name=name,
            version=version,
            content="\n".join(content_lines).strip(),
        )