class RAGFallbackBuilder:
    def build_no_context_answer(
        self,
        question: str,
    ) -> str:
        if self._looks_turkish(
            question
        ):
            return (
                "Bilgi tabanında bu soruyu "
                "güvenilir biçimde yanıtlamak "
                "için yeterli kaynak bulunamadı."
            )

        return (
            "The knowledge base does not contain "
            "enough relevant information to "
            "answer this question reliably."
        )

    def build_invalid_generation_answer(
        self,
        question: str,
    ) -> str:
        if self._looks_turkish(
            question
        ):
            return (
                "Kaynaklara dayalı güvenilir bir "
                "cevap üretilemedi. Yanlış veya "
                "desteklenmeyen bilgi vermemek "
                "için cevap oluşturulmadı."
            )

        return (
            "A reliable source-grounded answer "
            "could not be generated. No answer "
            "was returned to avoid unsupported "
            "information."
        )

    def _looks_turkish(
        self,
        text: str,
    ) -> bool:
        normalized_text = text.lower()

        turkish_characters = {
            "ç",
            "ğ",
            "ı",
            "ö",
            "ş",
            "ü",
        }

        if any(
            character in normalized_text
            for character in turkish_characters
        ):
            return True

        turkish_words = {
            "nasıl",
            "nedir",
            "neden",
            "hangi",
            "için",
            "mülakat",
            "özgeçmiş",
            "hazırlanmalıyım",
        }

        words = set(
            normalized_text.split()
        )

        return bool(
            words & turkish_words
        )