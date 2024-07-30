# app/__init__.py

import logging
from .config import Config

# Set up logging for the application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Initializing Telebox Bot application")

# Initialize Telebox API client
try:
    from .telebox import Telebox
    telebox_client = Telebox(Config.TELEBOX_API, Config.TELEBOX_BASEFOLDER)
    logger.info("Telebox client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Telebox client: {e}")

# Initialize Telegram Bot components
try:
    from telegram.ext import ApplicationBuilder

    application = ApplicationBuilder().token(Config.TELEGRAM_API_TOKEN).build()
    logger.info("Telegram bot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Telegram bot: {e}")

# Expose key components for package users
__all__ = ['Config', 'telebox_client', 'application']