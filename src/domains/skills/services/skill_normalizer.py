class SkillNormalizer:
    SYNONYMS = {
        "ai": "artificial intelligence",
        "yapayzeka": "artificial intelligence",
        "yapay zeka": "artificial intelligence",

        "hr": "human resources",
        "insankaynaklari": "human resources",
        "insan kaynakları": "human resources",
        "insan kaynaklari": "human resources",

        "postgres": "postgresql",
        "postgresql": "postgresql",
        "sql": "sql",

        "sklearn": "scikit learn",
        "scikit-learn": "scikit learn",
        "scikit learn": "scikit learn",

        "fast api": "fastapi",
        "fast-api": "fastapi",
        "fastapi": "fastapi",
    }

    def normalize(
        self,
        skill: str,
    ) -> str:
        normalized = (
            skill.strip()
            .lower()
            .replace("ı", "i")
            .replace("ğ", "g")
            .replace("ü", "u")
            .replace("ş", "s")
            .replace("ö", "o")
            .replace("ç", "c")
            .replace("-", " ")
            .replace("_", " ")
        )

        normalized = " ".join(
            normalized.split()
        )

        compact = normalized.replace(
            " ",
            "",
        )

        if normalized in self.SYNONYMS:
            return self.SYNONYMS[normalized]

        if compact in self.SYNONYMS:
            return self.SYNONYMS[compact]

        return compact