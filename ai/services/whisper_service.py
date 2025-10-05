"""
Local Whisper service for speech-to-text transcription.

Converts audio files to text using locally-running Whisper model.

Requirements:
- pip install openai-whisper
- Optional: pip install faster-whisper (faster implementation)

No API key needed - runs 100% locally!
"""

import io
import tempfile
from typing import Dict

try:
    import whisper
except ImportError:
    whisper = None  # type: ignore

# Try faster-whisper as alternative
try:
    from faster_whisper import WhisperModel

    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    WhisperModel = None  # type: ignore
    FASTER_WHISPER_AVAILABLE = False


# Global model cache (load once, reuse)
_whisper_model = None
_faster_whisper_model = None


def _get_whisper_model(model_size: str = "base"):
    """
    Get or load Whisper model (cached).

    Model sizes:
    - tiny: Fastest, least accurate (~1GB RAM)
    - base: Good balance (~1GB RAM) - DEFAULT
    - small: Better accuracy (~2GB RAM)
    - medium: Very good (~5GB RAM)
    - large: Best accuracy (~10GB RAM)
    """
    global _whisper_model

    if _whisper_model is None:
        if whisper is None:
            raise ImportError(
                "Whisper not installed. Install: pip install openai-whisper"
            )
        print(f"Loading Whisper model '{model_size}' (one-time, cached)...")
        _whisper_model = whisper.load_model(model_size)
        print(f"✓ Whisper model '{model_size}' loaded")

    return _whisper_model


def _get_faster_whisper_model(model_size: str = "base"):
    """
    Get or load faster-whisper model (cached).

    Faster-whisper is 4x faster than standard whisper!
    """
    global _faster_whisper_model

    if _faster_whisper_model is None:
        if not FASTER_WHISPER_AVAILABLE:
            raise ImportError(
                "faster-whisper not installed. Install: pip install faster-whisper"
            )
        print(f"Loading faster-whisper model '{model_size}' (one-time, cached)...")
        _faster_whisper_model = WhisperModel(
            model_size, device="cpu", compute_type="int8"
        )
        print(f"✓ faster-whisper model '{model_size}' loaded")

    return _faster_whisper_model


async def transcribe_audio(
    audio_bytes: bytes,
    filename: str,
    use_faster_whisper: bool = True,
    model_size: str = "base",
) -> Dict:
    """
    Transcribe audio to text using local Whisper model.

    Args:
        audio_bytes: Raw audio file bytes
        filename: Original filename (for format detection)
        use_faster_whisper: Use faster-whisper if available (4x faster!)
        model_size: Model size (tiny/base/small/medium/large)

    Returns:
        {
            "text": "Transcribed text",
            "language": "pl",
            "duration": None  # Not available in local mode
        }
    """
    # Try faster-whisper first (if requested and available)
    if use_faster_whisper and FASTER_WHISPER_AVAILABLE:
        return await _transcribe_with_faster_whisper(audio_bytes, filename, model_size)

    # Fallback to standard whisper
    return await _transcribe_with_standard_whisper(audio_bytes, filename, model_size)


async def _transcribe_with_standard_whisper(
    audio_bytes: bytes, filename: str, model_size: str
) -> Dict:
    """Transcribe using standard openai-whisper."""
    model = _get_whisper_model(model_size)

    # Save audio to temp file (whisper needs file path)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(audio_bytes)
        temp_path = temp_file.name

    try:
        # Transcribe
        result = model.transcribe(
            temp_path,
            language="pl",  # Force Polish
            fp16=False,  # Disable FP16 for CPU
        )

        return {
            "text": result["text"],
            "language": result.get("language", "pl"),
            "duration": None,  # Not available in local mode
        }

    finally:
        # Clean up temp file
        import os

        try:
            os.unlink(temp_path)
        except Exception:
            pass


async def _transcribe_with_faster_whisper(
    audio_bytes: bytes, filename: str, model_size: str
) -> Dict:
    """Transcribe using faster-whisper (4x faster!)."""
    model = _get_faster_whisper_model(model_size)

    # Save audio to temp file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(audio_bytes)
        temp_path = temp_file.name

    try:
        # Transcribe
        segments, info = model.transcribe(
            temp_path,
            language="pl",
            beam_size=5,
        )

        # Concatenate all segments
        text = " ".join([segment.text for segment in segments])

        return {
            "text": text,
            "language": info.language,
            "duration": info.duration,
        }

    finally:
        # Clean up temp file
        import os

        try:
            os.unlink(temp_path)
        except Exception:
            pass
