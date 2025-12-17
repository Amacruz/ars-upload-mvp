import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./ars.db")
PORT = int(os.getenv("PORT", "8080"))
ARS_MIN_SCORE = int(os.getenv("ARS_MIN_SCORE", "75"))
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
ARS_API_KEY = os.getenv("ARS_API_KEY")  # optional protection
