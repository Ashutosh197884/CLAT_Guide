import logging
from openai import OpenAI
from config import settings

logger = logging.getLogger("lexai.ai")

class NemotronClient:
    def __init__(self):
        self.client = None
        if settings.NVIDIA_API_KEY:
            try:
                self.client = OpenAI(
                    base_url=settings.NVIDIA_API_URL,
                    api_key=settings.NVIDIA_API_KEY
                )
                logger.info("NVIDIA Build API Client successfully initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize NVIDIA API Client: {e}")
        else:
            logger.warning("NVIDIA_API_KEY is not set. AI model runs will fall back to simulation mode.")

    def generate_response(self, prompt: str, context: str = "") -> str:
        """Call NVIDIA Nemotron API with context and prompt."""
        if not self.client:
            mock_explanation = (
                "[LexAI Simulation Mode - No API Key Set]\n\n"
                "I see you are asking about your CLAT studies! Since the NVIDIA API Key is currently empty, "
                "here is a simulated explanation based on your documents.\n\n"
                f"Retrieved Document Context: {context[:200]}...\n\n"
                f"Question Asked: {prompt}\n\n"
                "To get real answers from the 120B Nemotron model, please update your NVIDIA_API_KEY in the .env file."
            )
            return mock_explanation

        system_message = (
            "You are LexAI, a state-of-the-art AI tutor designed specifically to prepare students for the CLAT "
            "(Common Law Admission Test) in India. You specialize in analyzing legal principles, facts, logical arguments, "
            "comprehension passages, and current affairs. Use the provided document context to formulate accurate, "
            "well-structured responses. Always provide step-by-step reasoning behind your legal or logical conclusions."
        )

        user_content = prompt
        if context:
            user_content = f"STUDY CONTEXT:\n{context}\n\nSTUDENT INQUIRY:\n{prompt}"

        try:
            response = self.client.chat.completions.create(
                model=settings.NVIDIA_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.2, # low temperature for high precision legal facts
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"NVIDIA Nemotron call failed: {e}")
            return f"Error communicating with NVIDIA Nemotron: {str(e)}"

nemotron_client = NemotronClient()
