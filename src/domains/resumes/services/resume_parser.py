import re


class ResumeParser:
    KNOWN_SKILLS = [
        "Python",
        "FastAPI",
        "Flask",
        "Django",
        "PostgreSQL",
        "MySQL",
        "SQL",
        "Docker",
        "Git",
        "GitHub",
        "Redis",
        "Celery",
        "Machine Learning",
        "Deep Learning",
        "NLP",
        "RAG",
        "LangGraph",
        "PyTorch",
        "TensorFlow",
        "Scikit-learn",
        "Pandas",
        "NumPy",
        "React",
        "Flutter",
        "Firebase",
        "Kurumsal İletişim",
        "iş ve KVKK Hukuku",
        "Performans Yönetimi",
        "insan kaynakları Stratejisi ve işe alım Teknikleri",
        "Yapay Zeka",
        "İnsan Kaynakları",
        "Kurumsal İletişim",
        "Performans Yönetimi",
        "İşe Alım",
        "KVKK",
        "Satış",
    ]

    def parse(
        self,
        raw_text: str,
    ) -> dict:
        skills = self._extract_skills(raw_text)

        return {
            "email": self._extract_email(raw_text),
            "phone": self._extract_phone(raw_text),
            "skills": skills,
            "target_role": self._extract_target_role(raw_text, skills),
            "seniority": self._extract_seniority(raw_text),
        }

    def _extract_email(
        self,
        text: str,
    ) -> str | None:
        match = re.search(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            text,
        )

        if not match:
            return None

        return match.group(0)

    def _extract_phone(
        self,
        text: str,
    ) -> str | None:
        match = re.search(
            r"(\+90\s?)?0?\s?5\d{2}\s?\d{3}\s?\d{2}\s?\d{2}",
            text,
        )

        if not match:
            return None

        return match.group(0)

    def _extract_skills(
        self,
        text: str,
    ) -> list[str]:
        found_skills: list[str] = []

        lower_text = text.lower()

        for skill in self.KNOWN_SKILLS:
            if skill.lower() in lower_text:
                found_skills.append(skill)

        return sorted(set(found_skills))
    

    def _extract_target_role(
        self,
        text: str,
        skills: list[str],
    ) -> str | None:
        lower_text = text.lower()

        hr_signals = [
            "insan kaynakları",
            "işe alım",
            "performans yönetimi",
            "human resources",
            "recruitment",
        ]

        ai_signals = [
            "yapay zeka geliştirme",
            "machine learning",
            "deep learning",
            "rag",
            "langgraph",
            "pytorch",
            "tensorflow",
        ]

        backend_signals = [
            "backend",
            "fastapi",
            "django",
            "flask",
        ]

        sales_signals = [
            "satış",
            "sales",
        ]

        hr_score = sum(
            1
            for signal in hr_signals
            if signal in lower_text
        )

        ai_score = sum(
            1
            for signal in ai_signals
            if signal in lower_text
        )

        backend_score = sum(
            1
            for signal in backend_signals
            if signal in lower_text
        )

        sales_score = sum(
            1
            for signal in sales_signals
            if signal in lower_text
        )

        scores = {
            "Human Resources": hr_score,
            "AI": ai_score,
            "Backend Developer": backend_score,
            "Sales": sales_score,
        }

        best_role = max(
            scores,
            key=scores.get,
        )

        if scores[best_role] > 0:
            return best_role

        if skills:
            return skills[0]

        return None


    def _extract_seniority(
        self,
        text: str,
    ) -> str | None:
        lower_text = text.lower()

        if "stajyer" in lower_text or "intern" in lower_text:
            return "intern"

        if "junior" in lower_text:
            return "junior"

        if "senior" in lower_text:
            return "senior"

        if "mid" in lower_text:
            return "mid"

        return None