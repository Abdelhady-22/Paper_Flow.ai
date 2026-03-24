"""
Voice Service — SpeechT5 Offline TTS Provider

Local text-to-speech using Microsoft SpeechT5 model.
Offline fallback when no cloud TTS is available (Section 12.3).
"""

import tempfile
import os
import torch
import numpy as np
from services.voice_service.utils.provider_interface import TTSProvider
from shared.logger.logger import get_logger
from shared.error_handler.exceptions import TTSException

logger = get_logger(__name__)

_speecht5_model = None
_speecht5_processor = None
_speecht5_vocoder = None
_speaker_embeddings = None


def _load_speecht5():
    """Lazy-load SpeechT5 model, processor, vocoder, and speaker embeddings."""
    global _speecht5_model, _speecht5_processor, _speecht5_vocoder, _speaker_embeddings

    if _speecht5_model is None:
        logger.info("loading_speecht5_model")
        from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
        from datasets import load_dataset

        _speecht5_processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        _speecht5_model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        _speecht5_vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

        # Load speaker embeddings from CMU Arctic dataset
        embeddings_dataset = load_dataset(
            "Matthijs/cmu-arctic-xvectors", split="validation"
        )
        _speaker_embeddings = torch.tensor(
            embeddings_dataset[7306]["xvector"]
        ).unsqueeze(0)

        logger.info("speecht5_model_loaded")


class SpeechT5Provider(TTSProvider):
    """Offline TTS using Microsoft SpeechT5 — English only."""

    async def synthesize(self, text: str, language: str = "en") -> bytes:
        if language != "en":
            logger.warning("speecht5_only_english", requested=language)
            # Fallback to Edge-TTS for non-English
            from services.voice_service.utils.edge_tts_provider import EdgeTTSProvider
            return await EdgeTTSProvider().synthesize(text, language)

        try:
            _load_speecht5()

            inputs = _speecht5_processor(text=text, return_tensors="pt")
            speech = _speecht5_model.generate_speech(
                inputs["input_ids"],
                _speaker_embeddings,
                vocoder=_speecht5_vocoder,
            )

            # Convert to WAV bytes
            import scipy.io.wavfile as wavfile
            from io import BytesIO

            audio_np = speech.numpy()
            buffer = BytesIO()
            wavfile.write(buffer, rate=16000, data=(audio_np * 32767).astype(np.int16))
            audio_bytes = buffer.getvalue()

            logger.info("speecht5_tts_complete", bytes=len(audio_bytes))
            return audio_bytes

        except Exception as e:
            logger.error("speecht5_tts_error", error=str(e))
            raise TTSException("Offline TTS failed. Please try a cloud provider.")
