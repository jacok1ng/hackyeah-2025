# Transport Validation Classifier

System klasyfikacji ML do walidacji czy użytkownik faktycznie porusza się danym środkiem transportu publicznego na podstawie danych z sensorów.

## 📊 Dane wejściowe

### Źródła danych
- **JourneyData**: dane z sensorów w wysokiej częstotliwości (~100Hz)
- **VehicleTrip**: informacje o kursach pojazdów
- **Vehicle**: typ pojazdu (autobus, tramwaj, pociąg), pojemność

### Agregacja 100Hz → 1Hz

**Surowe dane** z sensorów są agregowane do **1Hz (1 próbka/sekundę)** z obliczeniem statystyk:
- **min**: wartość minimalna w oknie 1s
- **max**: wartość maksymalna w oknie 1s
- **avg**: średnia w oknie 1s
- **median**: mediana w oknie 1s
- **std**: odchylenie standardowe w oknie 1s

### Features (cechy)

#### Agregowane z sensorów (każda ma 5 wersji: _min, _max, _avg, _median, _std):
- **GPS**: 
  - `latitude_[stat]`, `longitude_[stat]`, `altitude_[stat]`
  - `speed_[stat]`, `bearing_[stat]`
  - `accuracy_[stat]`, `vertical_accuracy_[stat]`, `satellite_count_[stat]`
- **Akcelerometr**: 
  - `acceleration_x_[stat]`, `acceleration_y_[stat]`, `acceleration_z_[stat]`
  - `linear_acceleration_x_[stat]`, `linear_acceleration_y_[stat]`, `linear_acceleration_z_[stat]`
- **Żyroskop**: 
  - `gyroscope_x_[stat]`, `gyroscope_y_[stat]`, `gyroscope_z_[stat]`
  - `rotation_vector_x_[stat]`, `rotation_vector_y_[stat]`, `rotation_vector_z_[stat]`, `rotation_vector_w_[stat]`
- **Barometr**: `pressure_[stat]`
- **Magnitude (pochodne)**:
  - `acceleration_magnitude_[stat]`
  - `linear_acceleration_magnitude_[stat]`
  - `gyroscope_magnitude_[stat]`

**Łącznie**: ~24 cechy × 5 statystyk = **~120 cech agregowanych**

#### Rolling statistics (okno 5 próbek = 5 sekund):
- `speed_rolling_std`: odchylenie std prędkości w ostatnich 5s
- `speed_rolling_range`: zakres prędkości (max - min) w oknie
- `acceleration_rolling_std`: odchylenie std przyspieszenia w ostatnich 5s
- `bearing_change_rate`: tempo zmiany kierunku

#### Czasowe:
- `hour_of_day`: godzina (0-23)
- `day_of_week`: dzień tygodnia (0-6)
- `is_weekend`: czy weekend (0/1)

#### Pojazd:
- `is_train`: czy pociąg (0/1)
- `is_tram`: czy tramwaj (0/1)
- `is_bus`: czy autobus (0/1)
- `vehicle_capacity`: pojemność pojazdu

### Label (etykieta)
- `is_valid_trip`: czy użytkownik faktycznie był w tym pojeździe (0/1)

---

## 🚀 Użycie

### 1. Instalacja zależności

```bash
pip install -r ml/requirements.txt
```

### 2. Przygotowanie danych

#### Wariant A: Podstawowy (bez filtrowania GPS)

```bash
python ml/prepare_transport_validation_data.py
```

**Wyjście**: `ml/transport_validation_data.csv`

**Co robi skrypt:**
1. Pobiera wysokoczęstotliwościowe dane z `JourneyData` + `VehicleTrip` + `Vehicle`
2. Oblicza cechy pochodne (magnitude dla xyz)
3. **Agreguje 100Hz → 1Hz** z statystykami (min, max, avg, median, std)
4. Dodaje cechy czasowe (hour, day, weekend)
5. Dodaje rolling statistics (5-sekundowe okna)
6. Koduje typy pojazdów (one-hot encoding)
7. Czyści dane (usuwa brakujące GPS, wypełnia medianami)
8. Zapisuje do CSV

#### Wariant B: Z filtrowaniem GPS (KNN + DBSCAN) ⭐ REKOMENDOWANY

```bash
python ml/prepare_transport_validation_data_filtered.py
```

**Wyjście**: `ml/transport_validation_data_filtered.csv`

**Co robi dodatkowo:**
- **Filtruje po jakości GPS**: usuwa punkty ze słabym sygnałem (accuracy > 50m, satellites < 4)
- **Wykrywa skoki GPS**: usuwa punkty z nierealistycznymi prędkościami (> 200 km/h)
- **DBSCAN clustering**: wykrywa i usuwa outliers GPS (punkty daleko od głównego klastra)
- **KNN outlier detection**: usuwa punkty niespójne z sąsiadami (średnia odległość > 200m)

**Parametry filtrowania:**
```python
# GPS quality
min_accuracy = 50  # meters
min_satellites = 4

# GPS jumps
max_speed_kmh = 200
time_threshold_seconds = 1

# DBSCAN
eps_meters = 100  # max distance in cluster
min_samples = 3   # min points for cluster

# KNN
n_neighbors = 5
distance_threshold_meters = 200
```

**Efekt**: Usuwa ~10-30% danych, ale znacząco poprawia jakość (mniej szumu GPS)

#### Porównanie wariantów (wizualizacja)

```bash
python ml/visualize_gps_filtering.py
```

**Wyjście**: Wykresy porównujące dane przed i po filtrowaniu:
- `gps_accuracy_comparison.png` - rozkład dokładności GPS
- `satellite_count_comparison.png` - liczba satelitów
- `speed_distribution_comparison.png` - rozkład prędkości (wykrycie skoków GPS)
- `data_statistics_comparison.png` - ogólne statystyki

### 3. Trening modeli

```bash
python ml/train_transport_classifier.py
```

**Modele:**
- **XGBoost Classifier**
- **LightGBM Classifier**

**Wyjścia:**
- `ml/xgboost_transport_validator.json` - model XGBoost
- `ml/lightgbm_transport_validator.txt` - model LightGBM
- `ml/xgboost_feature_importance.png` - ważność cech (XGBoost)
- `ml/lightgbm_feature_importance.png` - ważność cech (LightGBM)
- `ml/xgboost_confusion_matrix.png` - macierz pomyłek (XGBoost)
- `ml/lightgbm_confusion_matrix.png` - macierz pomyłek (LightGBM)
- `ml/roc_curves_comparison.png` - porównanie krzywych ROC

**Metryki:**
- Accuracy (dokładność)
- Precision, Recall, F1-Score
- ROC-AUC
- Confusion Matrix

---

## 📈 Przykładowe wyniki

```
=== XGBoost Performance ===
Accuracy: 0.9245

Classification Report:
              precision    recall  f1-score   support
     Invalid       0.91      0.94      0.92       150
       Valid       0.94      0.91      0.93       170
    accuracy                           0.92       320

ROC-AUC Score: 0.9653

=== LightGBM Performance ===
Accuracy: 0.9281

Classification Report:
              precision    recall  f1-score   support
     Invalid       0.92      0.95      0.93       150
       Valid       0.95      0.92      0.93       170
    accuracy                           0.93       320

ROC-AUC Score: 0.9681
```

---

## 🔧 Parametry modeli

### XGBoost
```python
max_depth: 6
learning_rate: 0.1
n_estimators: 100
subsample: 0.8
colsample_bytree: 0.8
```

### LightGBM
```python
max_depth: 6
learning_rate: 0.1
n_estimators: 100
subsample: 0.8
colsample_bytree: 0.8
```

Parametry można dostosować w pliku `train_transport_classifier.py`.

---

## 📝 Uwagi

1. **Wymagana ilość danych**: Minimum 1000 próbek dla wiarygodnych wyników
2. **Balance klas**: Staraj się mieć zbilansowane klasy (50/50 valid/invalid)
3. **Feature engineering**: Możesz dodać więcej cech pochodnych w `prepare_transport_validation_data.py`
4. **Hyperparameter tuning**: Użyj GridSearch lub Optuna do optymalizacji parametrów
5. **Cross-validation**: Rozważ k-fold CV dla lepszej oceny modelu

---

## 🎯 Status integracji z systemem

### ✅ Model wdrożony (faza testowa)

Model ML jest już zintegrowany z systemem weryfikacji streak w `crud/user_streak.py`.

**Status:** EXPERIMENTAL - Zbieranie danych do walidacji

**Działanie:**
1. Przy każdej weryfikacji podróży uruchamiane są OBA algorytmy:
   - Rule-based (GPS proximity) → wynik używany
   - ML model (XGBoost/LightGBM) → wynik logowany
2. Wyniki zapisywane do `ml/validation_comparison.jsonl`
3. Analiza zgodności po zebraniu >1000 próbek

**Sprawdź logi:**
```bash
# Zobacz porównanie ML vs rule-based
cat ml/validation_comparison.jsonl | jq '.'

# Policz zgodność
cat ml/validation_comparison.jsonl | jq '.agreement' | grep true | wc -l
```

**Po zebraniu danych:**
```python
# Analiza wyników
import pandas as pd
logs = pd.read_json('ml/validation_comparison.jsonl', lines=True)

print(f"Agreement rate: {logs['agreement'].mean()*100:.1f}%")
print(f"ML accuracy: {logs['ml_prediction'].mean()*100:.1f}%")
print(f"Avg confidence: {logs['ml_confidence'].mean():.3f}")
```

---

## 🚀 PRZYSZŁOŚĆ: Model Transformer (REKOMENDOWANY)

### Dlaczego Transformer?

**Obecne ograniczenia (XGBoost/LightGBM):**
- ❌ Wymaga agregacji 100Hz → 1Hz (utrata informacji)
- ❌ Manual feature engineering
- ❌ Nie rozumie pełnego kontekstu czasowego
- ❌ Trudna rozbudowa o nowe tryby transportu

**Zalety Transformera:**
- ✅ **Attention mechanism**: Automatycznie skupia się na ważnych momentach (przystanki, zakręty)
- ✅ **Surowe sekwencje**: Przetwarza 100Hz bez agregacji
- ✅ **Lepsze rozumienie czasowe**: Widzi całą podróż naraz
- ✅ **Brak feature engineering**: Sam uczy się optymalnych cech

### Rozbudowa: Klasyfikacja Multi-Modal + Gratyfikacja Eko-Mobilności

**CEL:** Rozpoznawanie WSZYSTKICH środków transportu użytkownika

```
Input: Surowe dane sensorowe (GPS, akcelerometr, żyroskop)
Output: Typ transportu + pewność

Klasy:
- 🚌 Autobus        (eco_points: 75)
- 🚊 Tramwaj        (eco_points: 80)
- 🚆 Pociąg         (eco_points: 75)
- 🚇 Metro          (eco_points: 70)
- 🚗 Samochód (k)   (eco_points: 10)
- 🚙 Samochód (p)   (eco_points: 30)
- 🚴 Rower          (eco_points: 90)
- 🛴 Hulajnoga e.   (eco_points: 60)
- 🚶 Pieszo         (eco_points: 100)
- 🏍️ Motocykl      (eco_points: 5)
- 🚕 Taxi/Uber      (eco_points: 15)
```

### Zastosowania dla eko-mobilności:

#### 1. System nagród
```python
# Automatyczne punkty za transport
if mode == "public_transport":
    award_points(user, eco_points)
    check_badges(user)  # "Eco Warrior", "Public Transport Champion"

# Wyzwania
"Zero Carbon Week": 7 dni bez samochodu → 500 bonus points
"Bike Month": 50km rowerem → badge + zniżka na bilety
```

#### 2. Tracking śladu węglowego
```python
carbon_footprint = {
    "car": 120g CO2/km,
    "bus": 25g CO2/km,
    "tram": 15g CO2/km,
    "bike": 0g CO2/km,
    "walking": 0g CO2/km
}

# Miesięczny raport
monthly_savings = calculate_carbon_saved(user_trips)
city_ranking = get_eco_ranking(user)
```

#### 3. Gamifikacja
- **Rankingi**: Najlepsi eko-użytkownicy miasta
- **Wyzwania grupowe**: "Zielony dzielnica" competition
- **Nagrody**: Zniżki, darmowe przejazdy, merchandise

#### 4. Analityka miejska
```python
# Agregowane dane
city_transport_mode_split = aggregate_all_users()
# "40% public transport, 25% car, 20% bike, 15% walking"

# Identyfikacja potrzeb
areas_needing_better_transit = analyze_patterns()
# "Dzielnica X: wysokie użycie aut → potrzeba lepszego MPK"
```

### Architektura Transformera

```python
Input: [batch, seq_len=6000, features=15]  # 60s @ 100Hz
       ↓
Embedding Layer (project to d_model=128)
       ↓
Positional Encoding (temporal information)
       ↓
Transformer Encoder (6 layers, 8 heads)
  - Self-attention: Które momenty są ważne?
  - Feed-forward: Feature transformation
  - Layer norm + residual connections
       ↓
Global Average Pooling (seq → single vector)
       ↓
Classification Head (11 classes)
       ↓
Output: [batch, 11] probability distribution

Metrics:
- Accuracy: >95% (vs ~85% XGBoost)
- F1-score: >0.93 per class
- Inference: <100ms
```

### Ścieżka implementacji

1. **[OBECNIE]** Zbieranie danych z rule-based + ML validation
2. **[Q2]** Implementacja Transformer (PyTorch)
   - Zbiór danych: 10k+ podróży per klasa
   - Training: 4-8 GPU hours
   - Validation: Cross-validation + test set
3. **[Q3]** A/B testing
   - 10% ruchu → Transformer
   - 90% ruchu → XGBoost
   - Metryka: Accuracy + user feedback
4. **[Q3]** Produkcja
   - Deploy Transformer jeśli lepszy o >5%
   - Monitoring + continuous learning
5. **[Q4]** Rozszerzenie multi-modal
   - Dodanie nowych klas transportu
   - Fine-tuning na nowych danych
6. **[Q1 next]** Gamifikacja
   - System punktów eco-mobility
   - Badges, rankingi, wyzwania
   - Integracja z reward system

---

## 📊 Dalsze kroki (krótkoterminowe)

1. **Zbieranie danych**: Cel 1000+ walidacji (sprawdź logi regularnie)
2. **Analiza zgodności**: Porównaj ML vs rule-based accuracy
3. **Feature importance**: Które sensory są najważniejsze?
4. **Hyperparameter tuning**: Optymalizacja modelu XGBoost
5. **A/B test decision**: Czy wdrożyć ML? (jeśli accuracy >95%)
