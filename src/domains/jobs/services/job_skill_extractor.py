class JobSkillExtractor:
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
        "Human Resources",
        "Performance Management",
        "Recruitment",
        "Corporate Communication",
        "KVKK",
        "Sales",
    ]

    def extract(
        self,
        description: str,
    ) -> list[str]:
        found_skills: list[str] = []

        lower_description = description.lower()

        for skill in self.KNOWN_SKILLS:
            if skill.lower() in lower_description:
                found_skills.append(skill)

        return sorted(set(found_skills))