# Weather & Meteorological Telemetry Intelligence Skill
### Multi-Sensor Environmental Telemetry, Atmospheric Acoustic Propagation, Tactical Flight Envelopes, and Monsoon Disaster Early Warning
*An Operations Research & Field Telemetry Protocol Under the Yin-Yang-Chaos-Harmony Paradigm*

## Trigger
Activated when collecting, parsing, analyzing, or ingesting environmental data, weather station telemetry (temperature, relative humidity, barometric pressure, precipitation rate, anemometer wind velocity, solar irradiance, PM2.5/PM10 air quality), acoustic atmospheric propagation modeling, tactical flight viability assessments (SAC CAS jets vs. EAO/PDF drone swarms), and monsoon flood/landslide early warning in Myanmar.

---

## ☯️ The Four Forces (Yin-Yang-Chaos-Harmony)

| Force | Role | Meteorological & Weather Telemetry Expression |
| :--- | :--- | :--- |
| **🔵 Yin (Perception / State)** | In-situ physical atmospheric sensing | Temperature (°C), relative humidity (%), barometric pressure (hPa), rain gauge intensity (mm/hr), wind speed (m/s) & direction, solar irradiance (W/m²), PM2.5/PM10 particulate matter from scorched-earth fires. |
| **🔴 Yang (Action / Intelligence)** | Tactical forecasting & operational viability | Drone flight viability index (GO / NO-GO), SAC aerial strike threat probability, acoustic sensor detection range correction factors, flood runoff forecasting. |
| **⚡ Chaos (Entropic / Hazard)** | Extreme weather events & physical destruction | Flash floods, monsoon mudslides, tropical cyclone storm surges (Bay of Bengal), lightning-strike sensor damage, thermal inversion smoke trapping from scorched-earth village fires. |
| **🟢 Harmony (The Bridge)** | Disaster early-warning & privacy preservation | Automated SMS/mesh flood sirens, GPS spatial coarsening (~1.1 km hash), zero-trust Merkle ledger sealing (`domain="meteorological_telemetry"`). |

---

## 🌦️ 1. Myanmar Climate Zones & Seasonal Conflict Dynamics

### A. The Seasonal Conflict Dichotomy:
1. **Southwest Monsoon (May – October):**
   - **Precipitation:** 2,500–5,000 mm in coastal belts (Rakhine, Ayeyarwady, Mon, Tanintharyi); 1,200–2,500 mm in highland mountain states (Kachin, Chin, Shan, Karenni); 600–1,000 mm in the Central Dry Zone.
   - **Tactical Impact on SAC Air Operations:** Low cloud ceilings (<300–600m), torrential squalls, and severe turbulence ground or drastically restrict fixed-wing CAS sorties (Yak-130, K-8) and laser-guided munitions. Strike frequency drops by 60–75% compared to peak dry season.
   - **Tactical Impact on Resistance Drones:** Heavy rain short-circuits exposed drone electronics, blinds FPV camera lenses, and high wind shear drains batteries rapidly.
   - **Ground Logistics:** Dirt roads, mountain tracks, and unpaved jungle supply lines dissolve into deep mud, paralyzing junta heavy armor (tanks, BTR-3U, supply convoys).
   - **Environmental Hazards:** Catastrophic monsoon landslides in open-pit mining districts (e.g. Hpakant jade waste dumps); flash flooding along the Chindwin, Irrawaddy, Sittaung, and Salween river valleys.

2. **Northeast Monsoon / Dry Season (November – April):**
   - **Meteorology:** Clear skies, arid conditions, minimal precipitation (<50 mm total). Extreme heat season (March–April) with temperatures exceeding 40–44°C in the Central Dry Zone.
   - **Surge in SAC Air Warfare:** Total visual bombing freedom; daily combat sorties increase to 10–25 strike packages per theater. Thermobaric and cluster munitions achieve maximum lethal radii in dry, open air.
   - **Ground Mobility:** Mechanized infantry offensives become viable; unpaved roads harden.
   - **Hotspot False Positives:** Massive seasonal agricultural slash-and-burn and forest fires cause dense thermal pixel anomalies across NASA FIRMS (VIIRS/MODIS), requiring AI cross-validation with acoustic sensors to distinguish brush fires from bomb detonation craters.

3. **Bay of Bengal Tropical Cyclones (Peak Seasons: April–May & October–November):**
   - Severe cyclonic storms generate winds of 150–250 km/h, storm surges >3–5 meters, and localized rainfall exceeding 400 mm in 24 hours (e.g., Cyclone Mocha in May 2023, Cyclone Nargis in 2008).
   - Obliterates temporary bamboo IDP shelters, cuts cellular towers, and blocks cross-border humanitarian relief corridors.

---

## 🔬 2. Atmospheric Acoustic Propagation Physics

Atmospheric conditions fundamentally govern the speed of sound and frequency-dependent absorption, directly impacting the detection range of Parla's passive acoustic IoT edge sensor nodes:

### A. Temperature-Dependent Speed of Sound:
$$c(T) = 331.3 \sqrt{1 + \frac{T}{273.15}} \approx 331.3 + 0.606 \cdot T \quad (\text{m/s})$$
- At $T = 20^\circ\text{C}$: $c \approx 343.4\text{ m/s}$ (Standard benchmark).
- At $T = 40^\circ\text{C}$ (Dry Zone heatwave): $c \approx 355.2\text{ m/s}$ ($+3.4\%$ velocity increase, compressing Doppler curves).
- At $T = 5^\circ\text{C}$ (Kachin mountain winter): $c \approx 334.3\text{ m/s}$.

### B. Atmospheric Frequency Absorption ($\alpha$ in dB/km):
Atmospheric molecular absorption of sound energy (due to vibrational relaxation of nitrogen and oxygen molecules) depends heavily on frequency $f$ and relative humidity $RH$:
- **High-Frequency Attenuation ($f > 2\text{ kHz}$ - Jet Compressor Whine):**
  - High humidity ($RH > 80\%$) and rain cause extreme acoustic dampening: $\alpha \approx 25–65\text{ dB/km}$.
  - Detection range for incoming supersonic jets by high-frequency acoustic classifiers drops from 12 km down to 4–6 km.
- **Low-Frequency Penetration ($f < 150\text{ Hz}$ - Helicopter Blade Slap & Heavy Mortars):**
  - Atmospheric absorption is negligible: $\alpha < 0.5–1.5\text{ dB/km}$.
  - Low-frequency rotor blade slap from Mi-35/Mi-17 gunships (18.5–23.0 Hz) and 120mm mortar launches (25–45 Hz) penetrates dense rain and travels up to 10–14 km across valleys.

---

## 🛸 3. Tactical Flight & Drone Operational Envelopes

| Platform Category | Max Wind Speed Threshold | Max Rain Intensity | Min Cloud Ceiling | Critical Failure Risk Factor |
| :--- | :--- | :--- | :--- | :--- |
| **FPV Kamikaze Drones** *(7-10 inch racing builds)* | 10.0 m/s (36 km/h) | 0.5 mm/hr (Light mist) | 100 m | ESC short-circuiting, propeller motor desynchronization, camera lens water blinding. |
| **Agricultural Hexacopter Bombers** *(DJI Agras / EFT)* | 12.0 m/s (43 km/h) | 2.5 mm/hr (Light rain) | 150 m | High payload drag, motor overheating under crosswinds, battery voltage sag. |
| **Fixed-Wing CAS Jets** *(Yak-130, K-8W)* | 22.0 m/s (Crosswind >15 m/s) | 15.0 mm/hr (Moderate rain) | 600 m | Inability to visually acquire ground targets; risk of CFIT (Controlled Flight into Terrain) in valleys. |
| **Heavy Fighters** *(Su-30SME, MiG-29)* | 25.0 m/s | 25.0 mm/hr | 300 m (IFR / Radar) | Laser guidance beam scattering through clouds; reliance on unguided area bombing. |
| **Heavy Gunships** *(Mil Mi-35 Hind)* | 16.0 m/s | 10.0 mm/hr | 250 m | Severe downdraft turbulence over mountain ridges; tail rotor authority loss. |

---

## 🌊 4. Environmental Hazard Risk Indices

### A. Flash Flood & Riverine Inundation:
- **Accumulated Rainfall Thresholds:**
  - $>50\text{ mm}$ in 3 hours: `WARNING_FLASH_FLOOD_SUSCEPTIBILITY`
  - $>100\text{ mm}$ in 6 hours: `CRITICAL_FLASH_FLOOD_IMMINENT` -> Activate community siren & broadcast evacuation corridor.

### B. Landslide Susceptibility Index ($LSI$):
$$LSI = \text{Rainfall\_24h (mm)} \times \sin(\text{Slope\_Angle}) \times \text{Soil\_Saturation\_Factor}$$
- In Hpakant jade mining tracts and Chin mountain roads, $LSI > 75$ triggers automated pit-wall evacuation warnings.

---

## 🔐 5. Zero-Trust Ingress & Ledgering Schema

When ingesting meteorological telemetry into Parla's `OfflineLedger`:
1. **Domain:** `domain="meteorological_telemetry"`.
2. **GPS Coarsening:** Station coordinates coarsened to 2 decimal places (~1.1 km hash) to shield civilian weather observers and community edge nodes.
3. **PII Masking:** Operator names, cellular station IDs, and contact phone numbers scrubbed via `PIIScrubber`.
4. **Integrity Sealing:** Cryptographic HMAC-SHA256 signature committed into `Data/parla_ledger.db`.
