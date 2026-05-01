import httpx
import base64
from app.logger import logger

from app.config import get_settings

settings = get_settings()

class AudioService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # Basic Auth for Twilio Media
        self.auth = (settings.twilio_account_sid, settings.twilio_auth_token)

    async def process_voice_note(self, media_url: str, media_type: str):
        """Downloads voice note from Twilio using authentication."""
        try:
            logger.info(f"[AUDIO] Authenticating download: {media_url}")
            async with httpx.AsyncClient() as client:
                # Add auth to the request
                resp = await client.get(
                    media_url, 
                    follow_redirects=True, 
                    timeout=25.0, 
                    headers=self.headers,
                    auth=self.auth
                )
                
                if resp.status_code == 200:
                    audio_bytes = resp.content
                    audio_b64 = base64.b64encode(audio_bytes).decode()
                    logger.info(f"[AUDIO] Success! Downloaded {len(audio_bytes)} bytes.")
                    
                    return {
                        "mime_type": media_type,
                        "data": audio_b64
                    }
                else:
                    logger.error(f"[AUDIO] Auth failed or URL expired. Status: {resp.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"[AUDIO] Critical error: {str(e)}")
            return None

audio_service = AudioService()
