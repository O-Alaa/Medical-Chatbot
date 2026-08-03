import os


API_URL = os.getenv(
    "MEDICAL_API_URL",
    "https://medical-chatbot-ndeq.onrender.com",
).rstrip("/")

UPLOAD_TIMEOUT_SECONDS = 600
ASK_TIMEOUT_SECONDS = 180
