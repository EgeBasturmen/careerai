from pathlib import Path

import fitz


class PDFTextExtractor:
    def extract_text(
        self,
        file_path: str,
    ) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Resume file not found: {file_path}"
            )

        document = fitz.open(file_path)

        pages_text: list[str] = []

        for page in document:
            text = page.get_text("text")

            if text:
                pages_text.append(text)

        document.close()

        return "\n\n".join(pages_text).strip()