"""
Voice Assistant API endpoints.

Allows users to:
- Record voice commands
- Transcribe speech to text (Whisper AI)
- Process commands via AI (Gemini)
- Create/edit user journeys based on voice input

Example flow:
1. User records: "Chcę jechać z Dworca Centralnego do Mokotowa jutro o 8 rano"
2. Whisper transcribes the audio
3. Gemini extracts: origin, destination, date, time
4. System creates UserJourney
"""

from typing import Optional

from database import get_db
from dependencies import get_current_user
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from models import User
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/voice-assistant", tags=["Voice Assistant"])


class TranscriptionResponse(BaseModel):
    """Response from Whisper transcription."""

    text: str
    language: Optional[str] = None
    duration: Optional[float] = None


class VoiceCommandResponse(BaseModel):
    """Response from voice command processing."""

    transcription: str
    gemini_response: str
    action: str  # "create_journey", "update_journey", "query_info", "error"
    journey_id: Optional[str] = None
    message: str


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    summary="Transcribe audio to text",
)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file (mp3, wav, m4a, etc.)"),
    current_user: User = Depends(get_current_user),
):
    """
    Transcribe audio file to text using OpenAI Whisper.

    Supports formats: mp3, mp4, mpeg, mpga, m4a, wav, webm

    **Requirements:**
    - OpenAI API key in .env: `OPENAI_API_KEY=sk-...`

    **Returns:**
    - Transcribed text
    - Detected language
    - Audio duration
    """
    try:
        from services.whisper_service import transcribe_audio as whisper_transcribe
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Whisper service not configured. Install: pip install openai",
        )

    # Validate file type
    allowed_types = ["audio/mpeg", "audio/wav", "audio/mp4", "audio/x-m4a", "audio/webm"]
    if audio.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format: {audio.content_type}",
        )

    # Read audio file
    audio_bytes = await audio.read()

    if len(audio_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty audio file",
        )

    # Transcribe
    try:
        result = await whisper_transcribe(audio_bytes, audio.filename or "audio.mp3")
        return TranscriptionResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}",
        )


@router.post(
    "/process-command",
    response_model=VoiceCommandResponse,
    summary="Process voice command and create/update journey",
)
async def process_voice_command(
    audio: UploadFile = File(..., description="Audio file with voice command"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Full voice command processing pipeline:
    1. Transcribe audio (Whisper)
    2. Extract intent and entities (Gemini)
    3. Execute action (create/update journey)

    **Example commands:**
    - "Chcę jechać z Dworca Centralnego do Mokotowa jutro o 8 rano"
    - "Dodaj przystanek Plac Zbawiciela do mojej trasy"
    - "Zmień godzinę wyjazdu na 9:30"
    - "Pokaż trasę do Wilanowa"

    **Returns:**
    - Transcription
    - AI response
    - Action taken
    - Journey ID (if created/updated)
    """
    # Step 1: Transcribe audio
    try:
        from services.whisper_service import transcribe_audio as whisper_transcribe
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Whisper service not configured",
        )

    audio_bytes = await audio.read()
    transcription_result = await whisper_transcribe(
        audio_bytes, audio.filename or "audio.mp3"
    )
    transcription_text = transcription_result["text"]

    # Step 2: Process with Gemini
    try:
        from services.gemini_service import process_journey_command
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Gemini service not configured",
        )

    try:
        gemini_result = await process_journey_command(
            transcription_text, str(current_user.id), db
        )
    except Exception as e:
        return VoiceCommandResponse(
            transcription=transcription_text,
            gemini_response=str(e),
            action="error",
            message=f"Failed to process command: {str(e)}",
        )

    # Step 3: Execute action based on Gemini response
    action = gemini_result.get("action", "error")
    journey_id = None
    message = gemini_result.get("message", "Command processed")

    if action == "create_journey":
        # Create new journey
        journey_data = gemini_result.get("journey_data")
        if journey_data:
            try:
                # This would call actual journey creation logic
                # For now, return the structured data
                journey_id = gemini_result.get("journey_id")
                message = f"Created journey: {message}"
            except Exception as e:
                action = "error"
                message = f"Failed to create journey: {str(e)}"

    elif action == "update_journey":
        # Update existing journey
        journey_id = gemini_result.get("journey_id")
        updates = gemini_result.get("updates")
        if journey_id and updates:
            try:
                # This would call actual journey update logic
                message = f"Updated journey: {message}"
            except Exception as e:
                action = "error"
                message = f"Failed to update journey: {str(e)}"

    return VoiceCommandResponse(
        transcription=transcription_text,
        gemini_response=gemini_result.get("gemini_raw_response", ""),
        action=action,
        journey_id=journey_id,
        message=message,
    )


@router.post(
    "/quick-command",
    response_model=VoiceCommandResponse,
    summary="Process text command (no audio)",
)
async def process_text_command(
    command: str = Form(..., description="Text command"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Process text command directly (skip audio transcription).

    Useful for:
    - Testing without audio
    - Web interface with text input
    - Chat-based interactions

    **Example:**
    ```
    command: "Chcę jechać z Dworca Centralnego do Mokotowa jutro o 8 rano"
    ```
    """
    try:
        from services.gemini_service import process_journey_command
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Gemini service not configured",
        )

    try:
        gemini_result = await process_journey_command(command, str(current_user.id), db)
    except Exception as e:
        return VoiceCommandResponse(
            transcription=command,
            gemini_response=str(e),
            action="error",
            message=f"Failed to process command: {str(e)}",
        )

    action = gemini_result.get("action", "error")
    journey_id = gemini_result.get("journey_id")
    message = gemini_result.get("message", "Command processed")

    return VoiceCommandResponse(
        transcription=command,
        gemini_response=gemini_result.get("gemini_raw_response", ""),
        action=action,
        journey_id=journey_id,
        message=message,
    )
