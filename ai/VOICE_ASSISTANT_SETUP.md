# Voice Assistant - Setup Guide

System asystenta głosowego dla planowania podróży.

---

## 🎯 Funkcjonalność

**Voice-to-Action Pipeline:**
1. 🎤 Użytkownik nagrywa komendę głosową
2. 🔊 **Whisper AI** transkrybuje audio na tekst
3. 🤖 **Gemini AI** analizuje komendę i ekstrahuje dane
4. 🚍 System tworzy/edytuje `UserJourney`

**Przykładowe komendy:**
- "Chcę jechać z Dworca Centralnego do Mokotowa jutro o 8 rano"
- "Dodaj przystanek Plac Zbawiciela do mojej trasy"
- "Pokaż trasę do Wilanowa"
- "Zmień godzinę wyjazdu na 9:30"

---

## 📦 Instalacja

### 1. Zainstaluj zależności

```bash
pip install openai google-generativeai
```

### 2. Skonfiguruj API Keys

Dodaj do `.env`:

```env
# OpenAI (Whisper)
OPENAI_API_KEY=sk-proj-...

# Google Gemini
GEMINI_API_KEY=AIza...
```

**Gdzie zdobyć klucze:**

#### OpenAI API Key
1. Idź do https://platform.openai.com/api-keys
2. Zaloguj się / Zarejestruj
3. Kliknij "Create new secret key"
4. Skopiuj klucz (sk-proj-...)
5. Dodaj do `.env`

**Cennik:** ~$0.006/min audio (Whisper)

#### Google Gemini API Key
1. Idź do https://makersuite.google.com/app/apikey
2. Zaloguj się kontem Google
3. Kliknij "Create API key"
4. Skopiuj klucz (AIza...)
5. Dodaj do `.env`

**Cennik:** Free tier (60 requests/min)

---

## 🚀 Użycie

### API Endpoints

#### 1. **Transkrypcja audio** (tylko Whisper)

```bash
POST /voice-assistant/transcribe

# Body: multipart/form-data
audio: [plik audio]
```

**Response:**
```json
{
  "text": "Chcę jechać z Dworca Centralnego do Mokotowa jutro o 8 rano",
  "language": "pl",
  "duration": 5.2
}
```

#### 2. **Pełna komenda głosowa** (Whisper + Gemini + Action)

```bash
POST /voice-assistant/process-command

# Body: multipart/form-data
audio: [plik audio]
```

**Response:**
```json
{
  "transcription": "Chcę jechać z Dworca Centralnego do Mokotowa jutro o 8 rano",
  "gemini_response": "{\"action\": \"create_journey\", ...}",
  "action": "create_journey",
  "journey_id": "abc123...",
  "message": "Utworzono trasę: Dworzec Centralny → Mokotów na jutro 08:00"
}
```

#### 3. **Komenda tekstowa** (bez audio, tylko Gemini)

```bash
POST /voice-assistant/quick-command

# Body: form data
command: "Chcę jechać z Dworca Centralnego do Mokotowa jutro o 8 rano"
```

**Response:** Jak w punkcie 2 (bez transcription)

---

## 📝 Przykłady użycia

### Python (requests)

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "user1@test.com", "password": "user"}
)
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Voice command
with open("command.mp3", "rb") as f:
    files = {"audio": f}
    response = requests.post(
        "http://localhost:8000/voice-assistant/process-command",
        headers=headers,
        files=files
    )
    print(response.json())
```

### cURL

```bash
# Get token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1@test.com","password":"user"}' \
  | jq -r '.access_token')

# Send voice command
curl -X POST http://localhost:8000/voice-assistant/process-command \
  -H "Authorization: Bearer $TOKEN" \
  -F "audio=@command.mp3"
```

### JavaScript (Fetch API)

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'user1@test.com', password: 'user' })
});
const { access_token } = await loginResponse.json();

// Record audio (browser)
const mediaRecorder = new MediaRecorder(stream);
const audioChunks = [];

mediaRecorder.ondataavailable = (event) => {
  audioChunks.push(event.data);
};

mediaRecorder.onstop = async () => {
  const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
  const formData = new FormData();
  formData.append('audio', audioBlob, 'command.webm');

  const response = await fetch('http://localhost:8000/voice-assistant/process-command', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${access_token}` },
    body: formData
  });

  const result = await response.json();
  console.log(result);
};

// Start/stop recording
mediaRecorder.start();
setTimeout(() => mediaRecorder.stop(), 5000); // 5s recording
```

---

## 🎤 Formaty audio

**Wspierane formaty:**
- MP3 (`.mp3`)
- WAV (`.wav`)
- M4A (`.m4a`)
- MP4 audio (`.mp4`)
- WebM (`.webm`)

**Maksymalny rozmiar:** 25 MB (Whisper limit)

**Zalecane ustawienia:**
- Sample rate: 16kHz lub wyższy
- Bitrate: 128 kbps
- Mono (1 kanał)

---

## 🤖 Gemini Prompt Engineering

### Co Gemini rozumie?

**✅ Dobrze rozpoznawane:**
- Przystanki (nawet z literówkami)
- Daty względne ("jutro", "za 3 dni", "w piątek")
- Godziny ("o 8 rano", "17:30", "wieczorem")
- Akcje ("chcę jechać", "dodaj", "zmień", "pokaż")

**⚠️ Wymaga doprecyzowania:**
- Niejasne lokalizacje ("stamtąd", "jak wczoraj")
- Brak kontekstu ("zmień godzinę" - którą trasę?)

### Rozszerzanie Gemini

Edytuj `services/gemini_service.py`:

```python
prompt = f"""
Jesteś asystentem planowania podróży.

DOSTĘPNE PRZYSTANKI:
{chr(10).join(stop_names)}

# Dodaj własne instrukcje:
NOWE FUNKCJE:
- Rozpoznawaj ulubionetrasy
- Sugeruj najszybsze połączenia
- Ostrzegaj o opóźnieniach

KOMENDA: "{command}"
"""
```

---

## 🔧 Customization

### Zmień język transkrypcji

W `services/whisper_service.py`:

```python
response = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="en",  # Zmień na "en", "de", "fr", etc.
    response_format="verbose_json",
)
```

### Zmień model Gemini

W `services/gemini_service.py`:

```python
model = genai.GenerativeModel("gemini-1.5-pro")  # Lepszy model
# lub
model = genai.GenerativeModel("gemini-pro")  # Standardowy (szybszy)
```

### Dodaj więcej akcji

W `services/gemini_service.py`, rozszerz `process_journey_command`:

```python
elif action == "cancel_journey":
    # Nowa akcja: anulowanie trasy
    journey_id = parsed.get("journey_id")
    crud_user_journey.delete_user_journey(db, journey_id)
    return {
        "action": "cancel_journey",
        "message": "Anulowano trasę",
        ...
    }
```

---

## 📊 Przykładowy Flow

### Mobilna aplikacja (React Native)

```javascript
// 1. Nagrywanie
import { Audio } from 'expo-av';

const recording = new Audio.Recording();
await recording.prepareToRecordAsync(Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY);
await recording.startAsync();

// ... użytkownik mówi ...

await recording.stopAndUnloadAsync();
const uri = recording.getURI();

// 2. Wysyłanie do API
const formData = new FormData();
formData.append('audio', {
  uri,
  type: 'audio/m4a',
  name: 'command.m4a',
});

const response = await fetch('http://api/voice-assistant/process-command', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData,
});

const result = await response.json();

// 3. Wyświetlenie rezultatu
if (result.action === 'create_journey') {
  navigation.navigate('JourneyDetails', { id: result.journey_id });
  showToast(result.message);
}
```

---

## 🐛 Troubleshooting

### Problem: `ModuleNotFoundError: No module named 'openai'`

**Rozwiązanie:**
```bash
pip install openai
```

### Problem: `ModuleNotFoundError: No module named 'google.generativeai'`

**Rozwiązanie:**
```bash
pip install google-generativeai
```

### Problem: `OPENAI_API_KEY not set in environment`

**Rozwiązanie:**
1. Utwórz plik `.env` w folderze `ai/`
2. Dodaj: `OPENAI_API_KEY=sk-proj-...`
3. Restart aplikacji

### Problem: Gemini nie rozpoznaje przystanków

**Rozwiązanie:**
- Zwiększ liczbę przystanków w promptcie (linia 54 w `gemini_service.py`)
- Dodaj aliasy dla popularnych przystanków
- Użyj fuzzy matching

### Problem: Whisper transkrybuje niepoprawnie

**Rozwiązanie:**
- Użyj lepszej jakości audio (16kHz+, 128kbps+)
- Nagraj w cichym otoczeniu
- Mów wyraźnie i wolniej

---

## 💰 Koszty

### OpenAI Whisper
- **$0.006 / minuta audio**
- Przykład: 1000 min/mies = $6

### Google Gemini
- **Free tier:** 60 requests/min, 1500/day
- **Paid:** $0.00025/request (Gemini Pro)

### Szacunkowe koszty miesięczne:
- **1000 użytkowników, 10 komend/miesiąc:**
  - Audio (avg 10s): $1
  - Gemini (10k requests): $2.50
  - **TOTAL: ~$3.50/miesiąc**

---

## 🔮 Przyszłe ulepszenia

1. **Kontekst konwersacji**
   - Pamiętaj poprzednie komendy
   - "Dodaj przystanek do tej trasy" (bez powtarzania nazwy)

2. **Wielojęzyczność**
   - Auto-detekcja języka
   - Tłumaczenie on-the-fly

3. **Personalizacja**
   - Ulubione trasy
   - Częste przystanki
   - Preferencje użytkownika

4. **Proaktywne sugestie**
   - "Czy chcesz powtórzyć wczorajszą trasę?"
   - "Zauważyłem opóźnienie, zmienić trasę?"

5. **Integracja z kalendarzem**
   - "Dodaj podróż do mojego wydarzenia"

---

## 📞 Support

Jeśli masz problemy:
1. Sprawdź czy masz API keys w `.env`
2. Sprawdź logi FastAPI (console)
3. Test z `/voice-assistant/quick-command` (bez audio)
4. Sprawdź format audio (mp3, wav, m4a)
