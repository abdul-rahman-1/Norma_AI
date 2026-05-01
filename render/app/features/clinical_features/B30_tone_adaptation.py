from app.core.security import enforce_role
from app.logger import logger

async def execute(params, user_role, user_data=None, sender_phone=None):
    """
    Action B30: Tone Adaptation
    Sentiment analysis to adapt response logic.
    """
    allowed = ["SYSTEM", "STAFF", "ADMIN", "DOCTOR"]
    is_authorized, err_msg = enforce_role(user_role, allowed, action_name="B30_TONE_ADAPTATION")
    if not is_authorized:
        return {"status": "error", "message": err_msg}

    try:
        text = params.get("text")
        if not text:
            return {"status": "error", "message": "Text is required for tone adaptation."}

        # Baseline logic: Simple sentiment scoring or AI analysis
        logger.info(f"B30: Analyzing tone of: {text[:50]}...")
        
        # Mocking Sentiment Analysis
        sentiment = "neutral"
        suggested_tone = "professional"

        angry_words = ["angry", "upset", "horrible", "frustrated", "bad"]
        happy_words = ["thanks", "good", "great", "happy", "helped"]

        if any(word in text.lower() for word in angry_words):
            sentiment = "negative"
            suggested_tone = "empathetic_urgent"
        elif any(word in text.lower() for word in happy_words):
            sentiment = "positive"
            suggested_tone = "friendly_warm"

        return {
            "status": "success",
            "sentiment": sentiment,
            "suggested_tone": suggested_tone,
            "message": f"Tone analyzed as {sentiment}. Suggested response tone: {suggested_tone}."
        }

    except Exception as e:
        logger.error(f"B30_TONE_ADAPTATION_ERROR: {str(e)}")
        return {"status": "error", "message": f"Tone adaptation failed: {str(e)}"}
