"""
Voice Service — Voice Configuration

Centralized voice/language mappings for all TTS providers (Section 12.3).
"""

# ── Edge-TTS Voice Mappings ──────────────────────────────────
EDGE_TTS_VOICES = {
    "ar": "ar-SA-HamedNeural",
    "en": "en-US-ChristopherNeural",
}

# ── ElevenLabs Voice IDs ─────────────────────────────────────
ELEVENLABS_VOICES = {
    "ar": "your_arabic_voice_id",
    "en": "your_english_voice_id",
}

# ── Gemini TTS Config ────────────────────────────────────────
GEMINI_TTS_MODEL = "gemini-2.0-flash-exp"

# ── SpeechT5 Config ──────────────────────────────────────────
SPEECHT5_SAMPLE_RATE = 16000
SPEECHT5_SUPPORTED_LANGUAGES = ["en"]  # English only

# ── Supported Languages ──────────────────────────────────────
SUPPORTED_LANGUAGES = {"en", "ar"}
DEFAULT_LANGUAGE = "en"
