import re
import unicodedata


class JobNormalizer:
    def normalize_text(
        self,
        value: str | None,
    ) -> str:
        if not value:
            return ""

        normalized = unicodedata.normalize(
            "NFKD",
            value,
        )

        normalized = "".join(
            character
            for character in normalized
            if not unicodedata.combining(character)
        )

        normalized = normalized.lower().strip()

        normalized = re.sub(
            r"[^a-z0-9\s]",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        return normalized.strip()

    def normalize_title(
        self,
        title: str,
    ) -> str:
        normalized = self.normalize_text(title)

        replacements = {
            "artificial intelligence": "ai",
            "machine learning": "ml",
            "software developer": "software engineer",
        }

        for source, target in replacements.items():
            normalized = normalized.replace(
                source,
                target,
            )

        return normalized

    def normalize_company_name(
        self,
        company_name: str,
    ) -> str:
        normalized = self.normalize_text(
            company_name,
        )

        company_suffixes = {
            "ltd",
            "limited",
            "inc",
            "incorporated",
            "a s",
            "as",
            "anonim sirketi",
            "llc",
        }

        words = [
            word
            for word in normalized.split()
            if word not in company_suffixes
        ]

        return " ".join(words)

    def normalize_location(
        self,
        location: str | None,
    ) -> str:
        return self.normalize_text(location)