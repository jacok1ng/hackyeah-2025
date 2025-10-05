"""
Google Gemini service for natural language understanding.

Processes user commands and extracts structured data for journey planning.

Requirements:
- pip install google-generativeai
- GEMINI_API_KEY in .env
"""

import json
from datetime import datetime
from typing import Dict

try:
    import google.generativeai as genai  # type: ignore
except ImportError:
    genai = None  # type: ignore

from config import settings
from crud import stop as crud_stop
from sqlalchemy.orm import Session


async def process_journey_command(command: str, user_id: str, db: Session) -> Dict:
    """
    Process natural language journey command using Gemini.

    Args:
        command: User's voice/text command
        user_id: Current user ID
        db: Database session

    Returns:
        {
            "action": "create_journey" | "update_journey" | "query_info" | "error",
            "message": "Human-readable response",
            "journey_data": {...},  # If creating journey
            "journey_id": "...",  # If updating journey
            "updates": {...},  # If updating journey
            "gemini_raw_response": "..."
        }
    """
    if genai is None:
        raise ImportError(
            "Google Generative AI package not installed. "
            "Install: pip install google-generativeai"
        )

    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set in environment")

    # Configure Gemini
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro")

    # Get available stops for context
    stops = crud_stop.get_stops(db, skip=0, limit=100)
    stop_names = [f"{s.name} (ID: {s.id})" for s in stops[:20]]  # type: ignore

    # Construct prompt
    prompt = f"""
Jesteś asystentem planowania podróży komunikacją miejską.

DOSTĘPNE PRZYSTANKI (przykłady):
{chr(10).join(stop_names)}

KOMENDA UŻYTKOWNIKA:
"{command}"

ZADANIE:
Przeanalizuj komendę i zwróć JSON z następującą strukturą:

{{
    "action": "create_journey" | "update_journey" | "query_info" | "unclear",
    "intent": "Opis intencji użytkownika",
    "origin_stop": "Nazwa przystanku początkowego (lub null)",
    "destination_stop": "Nazwa przystanku końcowego (lub null)",
    "intermediate_stops": ["Lista przystanków pośrednich (lub [])"],
    "planned_date": "Data w formacie ISO (YYYY-MM-DD) lub null",
    "planned_time": "Godzina w formacie HH:MM lub null",
    "message": "Przyjazna odpowiedź dla użytkownika"
}}

REGUŁY:
1. Jeśli komenda zawiera "jutro", ustaw planned_date na jutrzejszą datę
2. Jeśli komenda zawiera "za X dni", oblicz odpowiednią datę
3. Rozpoznaj przystanki nawet jeśli są wpisane nieprecyzyjnie
4. Jeśli brakuje informacji, zaznacz to w "message"
5. Odpowiedz TYLKO w formacie JSON, bez dodatkowego tekstu

DZISIEJSZA DATA: {datetime.now().strftime('%Y-%m-%d')}
"""

    try:
        response = model.generate_content(prompt)
        gemini_text = response.text.strip() if response.text else ""

        # Remove markdown code blocks if present
        if gemini_text.startswith("```"):
            gemini_text = gemini_text.split("```")[1]
            if gemini_text.startswith("json"):
                gemini_text = gemini_text[4:].strip()

        # Parse JSON
        parsed = json.loads(gemini_text)

        # Process action
        action = parsed.get("action", "unclear")

        if action == "create_journey":
            # Validate we have minimum required data
            if not parsed.get("origin_stop") or not parsed.get("destination_stop"):
                return {
                    "action": "error",
                    "message": (
                        "Nie mogę utworzyć trasy - brakuje przystanku początkowego "
                        "lub końcowego. " + parsed.get("message", "")
                    ),
                    "gemini_raw_response": gemini_text,
                }

            # Find stop IDs
            origin_stop = _find_stop_by_name(db, parsed["origin_stop"])
            destination_stop = _find_stop_by_name(db, parsed["destination_stop"])

            if not origin_stop or not destination_stop:
                return {
                    "action": "error",
                    "message": (
                        f"Nie mogę znaleźć przystanków: "
                        f"{parsed['origin_stop']} -> {parsed['destination_stop']}"
                    ),
                    "gemini_raw_response": gemini_text,
                }

            # Build journey data
            journey_data = {
                "user_id": user_id,
                "name": f"Trasa: {origin_stop.name} → {destination_stop.name}",  # type: ignore
                "stops": [
                    {"stop_id": str(origin_stop.id), "order": 0},  # type: ignore
                    {"stop_id": str(destination_stop.id), "order": 1},  # type: ignore
                ],
            }

            # Add intermediate stops if any
            intermediate_stops = parsed.get("intermediate_stops", [])
            if intermediate_stops:
                for idx, stop_name in enumerate(intermediate_stops):
                    stop = _find_stop_by_name(db, stop_name)
                    if stop:
                        journey_data["stops"].insert(  # type: ignore
                            idx + 1,
                            {"stop_id": str(stop.id), "order": idx + 1},  # type: ignore
                        )

            # Add planned date/time if provided
            if parsed.get("planned_date"):
                planned_datetime = _parse_datetime(
                    parsed["planned_date"], parsed.get("planned_time")
                )
                journey_data["planned_date"] = planned_datetime.isoformat()  # type: ignore

            return {
                "action": "create_journey",
                "message": parsed.get("message", "Utworzono trasę"),
                "journey_data": journey_data,
                "gemini_raw_response": gemini_text,
            }

        elif action == "update_journey":
            # For now, return structured update data
            # In real implementation, would update existing journey
            return {
                "action": "update_journey",
                "message": parsed.get(
                    "message", "Aktualizacja trasy (funkcja w przygotowaniu)"
                ),
                "updates": parsed,
                "gemini_raw_response": gemini_text,
            }

        elif action == "query_info":
            return {
                "action": "query_info",
                "message": parsed.get("message", "Zapytanie informacyjne"),
                "gemini_raw_response": gemini_text,
            }

        else:
            return {
                "action": "unclear",
                "message": parsed.get(
                    "message",
                    "Nie rozumiem komendy. Spróbuj powiedzieć coś w stylu: "
                    "'Chcę jechać z Dworca Centralnego do Mokotowa jutro o 8 rano'",
                ),
                "gemini_raw_response": gemini_text,
            }

    except json.JSONDecodeError as e:
        gemini_text_safe = locals().get("gemini_text", "")
        return {
            "action": "error",
            "message": f"Błąd parsowania odpowiedzi AI: {str(e)}",
            "gemini_raw_response": gemini_text_safe,
        }
    except Exception as e:
        return {
            "action": "error",
            "message": f"Błąd przetwarzania komendy: {str(e)}",
            "gemini_raw_response": "",
        }


def _find_stop_by_name(db: Session, stop_name: str):
    """Find stop by name (fuzzy match)."""
    from db_models import Stop

    # Try exact match first
    stop = db.query(Stop).filter(Stop.name.ilike(stop_name)).first()  # type: ignore
    if stop:
        return stop

    # Try partial match
    stop = db.query(Stop).filter(Stop.name.ilike(f"%{stop_name}%")).first()  # type: ignore
    return stop


def _parse_datetime(date_str: str, time_str: str = None) -> datetime:
    """Parse date and optional time into datetime."""
    try:
        date_obj = datetime.fromisoformat(date_str)
    except ValueError:
        # Try other formats
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    if time_str:
        try:
            time_parts = time_str.split(":")
            date_obj = date_obj.replace(
                hour=int(time_parts[0]), minute=int(time_parts[1])
            )
        except (ValueError, IndexError):
            pass  # Use date only

    return date_obj
