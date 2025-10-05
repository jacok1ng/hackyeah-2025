# HackYeah 2025 - Mobile App �📱

Aplikacja mobilna do zarządzania transportem publicznym z funkcjonalnostami zgłaszania zdarzeń, śledzenia podróży i zarządzania profilem użytkownika.

## 🚀 Funkcjonalności

### 🏠 **Strona główna**

- Planowanie tras i połączeń
- Wyszukiwanie przystanków i tras
- Wyświetlanie aktualnych informacji o transporcie

### 💖 **Ulubione**

- Zapisywanie ulubionych tras
- Szybki dostęp do często używanych połączeń

### 🎫 **Bilety**

- Zarządzanie biletami elektronicznymi
- Historia zakupów

### 📊 **Status**

- Aktualny status podróży
- Informacje o opóźnieniach i zakłóceniach

### 👤 **Profil**

- Zarządzanie kontem użytkownika
- System rang i odznak
- Streak podróży
- **Ustawienia** z możliwością konfiguracji:
  - Dane osobowe
  - **Ustawienia powiadomień** (rozbudowane opcje)

### 📝 **Zgłaszanie zdarzeń**

- Zgłaszanie problemów w transporcie
- System kategoryzacji zdarzeń
- Potwierdzenia zgłoszeń

## 🛠️ Stack technologiczny

- **React Native** z **Expo** (~54.0.12)
- **Expo Router** (v6) - file-based routing
- **TypeScript** - type safety
- **NativeWind** (v4) - Tailwind CSS dla React Native
- **React Native SVG** - ikony i grafiki wektorowe
- **React Navigation** - nawigacja

## 📁 Struktura projektu

```
app/
├── _layout.tsx                 # Główny layout aplikacji
├── index.tsx                   # Strona startowa
├── report.tsx                  # Strona zgłoszeń
└── (tabs)/                     # Tab navigator
    ├── _layout.tsx             # Layout dla tabów
    ├── index.tsx               # Start (główna)
    ├── favorites.tsx           # Ulubione
    ├── tickets.tsx             # Bilety
    ├── status.tsx              # Status
    └── profile/                # Profil (zagnieżdżony navigator)
        ├── _layout.tsx         # Layout profilu
        ├── index.tsx           # Główny profil
        ├── settings.tsx        # Ustawienia
        └── notifications.tsx   # Ustawienia powiadomień

assets/
├── icons/                      # Ikony SVG
└── images/                     # Obrazy

components/
├── Header.tsx                  # Komponent nagłówka
├── ReportForm.tsx             # Formularz zgłoszeń
├── ReportConfirmationModal.tsx # Modal potwierdzenia
└── ...                        # Inne komponenty

types/
└── report.ts                  # Typy TypeScript
```

## 🚀 Uruchomienie projektu

### Wymagania

- Node.js (≥18)
- pnpm lub npm
- Expo CLI

### Instalacja

1. **Zainstaluj zależności**

   ```bash
   pnpm install
   # lub
   npm install
   ```

2. **Uruchom aplikację**

   ```bash
   pnpm start
   # lub
   npm start
   ```

3. **Opcje uruchomienia:**
   - **Android**: `pnpm android` (wymaga Android Studio/emulatora)
   - **iOS**: `pnpm ios` (wymaga Xcode/symulatora)
   - **Web**: `pnpm web`
   - **Expo Go**: Zeskanuj QR kod w aplikacji Expo Go

### Dodatkowe komendy

```bash
# Linting
pnpm lint

# Reset projektu
pnpm reset-project
```

## 🎨 Stylowanie

Projekt używa **NativeWind** (Tailwind CSS dla React Native):

```tsx
// Przykład użycia
<View className="flex-1 bg-white p-4">
  <Text className="text-lg font-semibold text-gray-800">Tytuł</Text>
</View>
```

## 🧭 Nawigacja

### File-based routing

- `app/(tabs)/index.tsx` → `/(tabs)/`
- `app/(tabs)/profile/settings.tsx` → `/(tabs)/profile/settings`

### Komponenty nawigacji

```tsx
// Link component (preferowany)
import { Link } from "expo-router";

<Link href="./settings" asChild>
  <Pressable>
    <Text>Ustawienia</Text>
  </Pressable>
</Link>;

// Programowa nawigacja
import { useRouter } from "expo-router";

const router = useRouter();
router.push("./settings");
```

## 📱 Główne komponenty UI

### Header

```tsx
import Header from "@/components/Header";

<Header title="Tytuł strony" />;
```

### Ikony

```tsx
import { BackArrowIcon, BusIcon } from "@/assets/icons";

<BackArrowIcon color="#FBC535" />;
```

## 🔧 Konfiguracja

### TypeScript

Projekt jest w pełni skonfigurowany z TypeScript z rygorystycznymi typami.

### ESLint

Konfiguracja ESLint z regułami Expo.

### Tailwind CSS

Konfiguracja NativeWind w `tailwind.config.js`.

## 👥 Zespół

Aplikacja mobilna stworzona na HackYeah 2025 przez zespół Skromni.
