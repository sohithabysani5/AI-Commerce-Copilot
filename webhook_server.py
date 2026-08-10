import uvicorn
import logging
from fastapi import FastAPI
from dotenv import load_dotenv

from config.settings import WEBHOOK_HOST, WEBHOOK_PORT
from api.voice_routes import router as voice_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Commerce Copilot Webhook Server",
    description="Handles Twilio incoming voice webhooks.",
    version="1.0.0",
)

# Include routes
app.include_router(voice_router)


@app.get("/")
async def root():
    """
    Health check endpoint.
    """
    return {
        "status": "online",
        "service": "AI Commerce Copilot Webhook Server"
    }


if __name__ == "__main__":
    
    logger.info(
        "Starting webhook server on %s:%s",
        WEBHOOK_HOST,
        WEBHOOK_PORT
    )

    uvicorn.run(
        "webhook_server:app",
        host=WEBHOOK_HOST,
        port=WEBHOOK_PORT,
        reload=True,
    )
