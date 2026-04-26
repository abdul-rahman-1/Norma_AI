# import uvicorn
# import os
# import sys
# from app.logger import logger

# # Add the current directory (render/) to sys.path
# # This allows 'import app' to work correctly
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))
#     logger.info(f"NORMA AI: Starting WhatsApp Orchestrator on port {port}")
#     uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
import logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
print("Your log message here", flush=True)
logging.info("Service started successfully")