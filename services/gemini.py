import google.generativeai as genai
from config import settings
import asyncio
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)

GEMINI_MODEL = "models/gemini-2.0-flash"

AGE_PROMPTS = {
    8: "You are responding to an 8-year-old child. Use simple language and short sentences. Explain concepts with basic examples. Avoid complex topics and keep answers brief. Be encouraging and positive.",
    9: "You are responding to a 9-year-old child. Use clear, straightforward language. Provide simple explanations with familiar examples. Be supportive and encouraging.",
    10: "You are responding to a 10-year-old child. You can use slightly more complex language, but still keep explanations clear. Use examples they can relate to. Be informative but not overwhelming.",
    11: "You are responding to an 11-year-old child. You can introduce more advanced concepts with appropriate explanations. Use examples that connect to their experiences. Be educational and supportive.",
    12: "You are responding to a 12-year-old child. You can discuss more nuanced topics with appropriate depth. Use relatable examples but don't oversimplify. Encourage critical thinking.",
    13: "You are responding to a 13-year-old child. You can discuss more complex topics, but still in an accessible way. Provide balanced viewpoints on sensitive topics. Encourage further learning."
}

SAFETY_INSTRUCTIONS = """
Always prioritize child safety and well-being. Provide educational, accurate information 
that is age-appropriate. Never share harmful, inappropriate, or adult content. If asked 
about sensitive topics, provide balanced, educational responses suitable for the child's age.
Always encourage children to talk to trusted adults about important or complicated topics.
"""


async def get_gemini_response(question: str, age: int, language: str = "en") -> str:
    """Get a response from Gemini API tailored to the child's age and preferred language"""

    age_prompt = AGE_PROMPTS.get(age, AGE_PROMPTS[10])  # Default to age 10 if not specified

    language_instruction = ""
    if language != "en":
        language_instruction = f"Respond in {language} language. "

    # Create the full prompt for Gemini
    prompt = f"""
    {age_prompt}

    {SAFETY_INSTRUCTIONS}

    {language_instruction}The child has asked: "{question}"

    Provide a friendly, educational, and age-appropriate response:
    """

    try:

        model = genai.GenerativeModel(GEMINI_MODEL)

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(prompt).text
        )

        return response
    except Exception as e:
        logger.error(f"Error with Gemini API: {str(e)}")

        if language == "tr":
            return "Üzgünüm, şu anda bu soruyu cevaplayamıyorum. Lütfen başka bir soru sormayı deneyin veya daha sonra tekrar gelin."
        else:
            return "I'm sorry, I can't answer that question right now. Please try asking something else or come back later."


