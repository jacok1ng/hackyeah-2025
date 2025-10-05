# Traffic Heatmap Analytics

System do generowania heatmap z danych GPS dla analizy ruchu i optymalizacji infrastruktury transportowej.

---

## 🎯 Cel

Identyfikacja obszarów wymagających:
- **Nowych przystanków** (high traffic areas without stops)
- **Częstszych przejazdów** (high demand routes)
- **Infrastruktury transportowej** (popular corridors)

---

## 📊 Rodzaje heatmap

### 1. **Weekly Heatmaps** (tygodniowe)
- `weekly_sum.png` - Suma wszystkich punktów GPS z tygodnia
- `weekly_average.png` - Średnia punktów na trip
- `weekly_interactive.html` - Interaktywna mapa (zoom, click)

**Interpretacja:**
- Czerwone obszary = highest traffic = potential for new stops
- Korytarze wysokiego ruchu = potential for new routes

### 2. **Daily Heatmaps** (dla każdego dnia tygodnia)
```
day_monday_sum.png
day_monday_average.png
day_tuesday_sum.png
...
day_sunday_average.png
```

**Interpretacja:**
- Pokazuje wzorce weekday vs weekend
- Identyfikuje dni wymagające więcej przejazdów

### 3. **Hourly Heatmaps** (dla każdej godziny)
```
hour_00_sum.png
hour_00_average.png
hour_01_sum.png
...
hour_23_average.png
```

**Interpretacja:**
- Pokazuje rush hours
- Optymalizacja rozkładu jazdy
- Identyfikacja godzin szczytowych

### 4. **Detailed Heatmaps** (dzień x godzina)
```
detailed/monday_08_sum.png
detailed/monday_09_sum.png
...
detailed/friday_17_sum.png
```

**Interpretacja:**
- Ultra-detailed analysis
- Specific time-of-week patterns
- Planning new schedules

---

## 📈 Metryki

### **SUM (Suma)**
- Total number of GPS points in area
- **Higher = More traffic = More demand**
- Use for: Identifying high-traffic corridors

### **AVERAGE (Średnia)**
- Average points per trip in area
- **Higher = Vehicles spend more time here**
- Use for: Identifying slow zones, frequent stops, congestion

---

## 🚀 Użycie

### Quick Start
```bash
cd ai
python analytics/generate_heatmaps.py
```

### Output
```
analytics/heatmaps/
├── weekly_sum.png
├── weekly_average.png
├── weekly_interactive.html
├── day_monday_sum.png
├── day_monday_average.png
├── ...
├── hour_08_sum.png
├── hour_08_average.png
├── ...
├── hotspots_report.csv
└── detailed/
    ├── monday_08_sum.png
    └── ...
```

---

## 📋 Hotspot Report

CSV file with top 20 highest-traffic areas:

| rank | center_lat | center_lon | total_points | unique_trips |
|------|------------|------------|--------------|--------------|
| 1    | 52.2297    | 21.0122    | 1245         | 87           |
| 2    | 52.2315    | 21.0058    | 1123         | 76           |
| ...  | ...        | ...        | ...          | ...          |

**Columns:**
- `rank` - Ranking by traffic
- `center_lat/lon` - Center coordinates of hotspot
- `total_points` - Total GPS points in area
- `unique_trips` - Number of different trips passing through

**Use for:**
1. Copy coordinates to Google Maps
2. Identify if area already has a stop
3. If not → proposal for new stop
4. If yes → proposal for more frequent service

---

## 🎨 Customization

### Change Grid Size
```python
# In generate_heatmaps.py, line ~250
grid_info = create_grid(df, grid_size=0.001)  # ~111m

# Options:
grid_size=0.0005  # ~55m (more detailed, slower)
grid_size=0.002   # ~222m (less detailed, faster)
```

### Change Time Window
```python
# In generate_heatmaps.py, line ~235
df = load_journey_data(db, start_date=datetime.now() - timedelta(days=7))

# Options:
timedelta(days=30)  # Last month
timedelta(days=1)   # Last day only
```

### Change Hotspot Count
```python
# In generate_heatmaps.py, line ~320
hotspots = generate_hotspot_report(df, grid_info, top_n=20)

# Options:
top_n=50   # More hotspots
top_n=10   # Fewer hotspots
```

---

## 🔧 Requirements

```bash
pip install pandas numpy matplotlib seaborn scipy folium
```

### Optional (for interactive maps)
```bash
pip install folium
```

If folium is not installed, interactive HTML maps will be skipped.

---

## 📊 Example Output

### Console Output
```
============================================================
HEATMAP GENERATION - Traffic Analysis
============================================================

📊 Loading GPS data...
✓ Loaded 45,234 GPS points from 2025-09-28 to 2025-10-05
  - Unique trips: 234
  - Unique users: 12

🗺️  Creating spatial grid...
✓ Grid created: 150 x 180 cells

📅 Generating weekly heatmaps...
✓ Saved: analytics/heatmaps/weekly_sum.png
✓ Saved: analytics/heatmaps/weekly_average.png
✓ Saved interactive map: analytics/heatmaps/weekly_interactive.html

📆 Generating per-day heatmaps...
✓ Saved: analytics/heatmaps/day_monday_sum.png
...

⏰ Generating per-hour heatmaps...
✓ Saved: analytics/heatmaps/hour_08_sum.png
...

🔥 Generating hotspot report...
✓ Saved hotspot report: analytics/heatmaps/hotspots_report.csv

============================================================
TOP 10 HOTSPOTS (Areas Needing Attention)
============================================================
rank  center_lat  center_lon  total_points  unique_trips
1     52.2297     21.0122     1245          87
2     52.2315     21.0058     1123          76
...

============================================================
SUMMARY STATISTICS
============================================================
Total GPS points: 45,234
Date range: 2025-09-28 08:15:23 to 2025-10-05 18:45:12
Unique trips: 234
Unique users: 12

Busiest day: Monday
Busiest hour: 8:00

Heatmaps saved to: C:\...\ai\analytics\heatmaps
============================================================
```

---

## 🧠 Analysis Workflow

1. **Generate all heatmaps**
   ```bash
   python analytics/generate_heatmaps.py
   ```

2. **Review weekly sum heatmap**
   - Identify red/orange hotspots
   - Compare with existing stop locations

3. **Check hotspot report CSV**
   - Top 20 areas with coordinates
   - Cross-reference with map

4. **Analyze time patterns**
   - Per-day: Weekend vs weekday demand
   - Per-hour: Rush hour identification

5. **Make decisions**
   - **New stop needed:** High traffic area without nearby stop
   - **More frequent service:** High traffic on existing route
   - **Route optimization:** Traffic corridor not well served

6. **Validation**
   - Check detailed day-hour maps for specific patterns
   - Verify with interactive map (zoom in, explore)

---

## 🎯 Business Use Cases

### 1. New Stop Proposal
```
1. Find hotspot from weekly_sum.png
2. Check coordinates from hotspots_report.csv
3. Verify in Google Maps: is there a stop nearby?
4. If NO → proposal for new stop
5. Check per-hour maps: when is demand highest?
6. → Recommendation: Add stop at (lat, lon) for peak hours
```

### 2. Route Frequency Optimization
```
1. Find high-traffic corridor from weekly heatmap
2. Check which route serves that corridor
3. Review per-hour demand: hour_08_sum.png, hour_17_sum.png
4. → Recommendation: Increase frequency during rush hours
```

### 3. New Route Planning
```
1. Find traffic corridor NOT well-served by existing routes
2. Check per-day patterns: demand on weekdays vs weekends
3. → Recommendation: Plan new route connecting hotspots
```

---

## 🚨 Common Issues

### No data
```
❌ No GPS data found in the last 7 days
```
**Solution:** Run seed_database.py or wait for real GPS data

### Grid too small/large
- Too small → slow processing, overly detailed
- Too large → loss of detail
**Solution:** Adjust `grid_size` parameter

### Memory error
- Too many points for large time windows
**Solution:** Reduce time window or increase grid size

---

## 🔮 Future Enhancements

1. **Real-time heatmaps** - Update every hour automatically
2. **Comparison mode** - Before/after adding new stops
3. **Predictive heatmaps** - ML model to forecast future demand
4. **Multi-layer maps** - Overlay stops, routes, incidents
5. **Demand forecasting** - Predict next week's hotspots
6. **Route optimization** - Suggest optimal routes connecting hotspots

---

## 📞 Support

For issues or questions:
1. Check console output for errors
2. Verify database has JourneyData entries
3. Check that timestamps are within analysis window
4. Ensure all dependencies are installed
