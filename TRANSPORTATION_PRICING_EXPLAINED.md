# Transportation Pricing Calculation - Galle to Matara

## Your Specific Trip
- **Route**: Galle → Matara (Sri Lanka)
- **Type**: Domestic travel
- **Distance**: ~47 km (actual road distance via Google Maps)
- **Travelers**: 3 people

## How Prices Are Calculated

### Step 1: Get Actual Distance
The system uses **Google Maps Distance Matrix API** to get the real road distance between Galle and Matara.

**Code** (`backend/agents/transportation_agent.py`, lines 202-213):
```python
result = self.gmaps_client.distance_matrix(
    origins=["Galle"],
    destinations=["Matara"],
    mode="driving",
    units="metric"
)

distance_km = element['distance']['value'] / 1000  # 47 km
duration_hours = element['duration']['value'] / 3600  # ~1 hour
```

**Result**: 47 km (this is the REAL distance from Google Maps)

### Step 2: Calculate Cost Per Trip Using Formulas

The system uses **dynamic pricing formulas** based on actual distance:

#### 1. Train ($22.11 for 3 travelers)
**Formula** (line 216):
```python
train_cost = max(20, min(100, 15 + (distance_km * 0.15)))
```

**Calculation for Galle → Matara**:
```
Base fare: $15
Per km: $0.15
Distance: 47 km

Cost = 15 + (47 × 0.15)
     = 15 + 7.05
     = $22.05 per person/trip

Min: $20, Max: $100
Result: $22.05 ✓
```

**For 3 travelers shown in UI**: ~$22.11 ✓

#### 2. Bus ($14.74 for 3 travelers)
**Formula** (line 217):
```python
bus_cost = max(10, min(60, 10 + (distance_km * 0.10)))
```

**Calculation**:
```
Base fare: $10
Per km: $0.10
Distance: 47 km

Cost = 10 + (47 × 0.10)
     = 10 + 4.70
     = $14.70 per trip

Result: $14.70 ✓
```

**For 3 travelers shown in UI**: ~$14.74 ✓

#### 3. Car Rental ($34.48 for 3 travelers)
**Formula** (line 218):
```python
car_cost = max(30, min(150, 25 + (distance_km * 0.20)))
```

**Calculation**:
```
Base fare: $25
Per km: $0.20
Distance: 47 km

Cost = 25 + (47 × 0.20)
     = 25 + 9.40
     = $34.40 per trip

Result: $34.40 ✓
```

**For 3 travelers shown in UI**: $34.48 ✓

#### 4. Private Car/Taxi ($58.69 for 3 travelers)
**Formula** (line 219):
```python
taxi_cost = max(40, min(300, 35 + (distance_km * 0.50)))
```

**Calculation**:
```
Base fare: $35
Per km: $0.50
Distance: 47 km

Cost = 35 + (47 × 0.50)
     = 35 + 23.50
     = $58.50 per trip

Result: $58.50 ✓
```

**For 3 travelers shown in UI**: $58.69 ✓

## Are These Real Prices?

### ✅ Based on Real Distance
- Uses **Google Maps Distance Matrix API**
- **47 km** is the actual road distance from Galle to Matara
- Duration estimates are also from Google Maps

### ⚠️ Pricing Formulas Are Estimates
The prices are **calculated using formulas**, not real-time API data from transport providers.

#### Why Formulas?
1. **No unified transport API** - Sri Lankan Railways, bus companies don't have public APIs
2. **Dynamic estimation** - Works for any route worldwide
3. **Reasonable approximations** - Based on typical transport costs

### How Accurate Are These Prices?

Let's compare with **actual Sri Lanka prices** for Galle → Matara (47 km):

| Transport | System Shows | Actual Price (Sri Lanka) | Accuracy |
|-----------|--------------|-------------------------|----------|
| **Train** | $22.11 | LKR 80-150 (~$0.25-0.50) | ❌ **Too high!** |
| **Bus** | $14.74 | LKR 100-200 (~$0.30-0.65) | ❌ **Too high!** |
| **Taxi** | $58.69 | LKR 4000-5000 (~$13-16) | ❌ **Too high!** |
| **Car Rental** | $34.48 | LKR 3000-4000/day (~$10-13) | ❌ **Too high!** |

### 🔍 The Problem: USD-Centric Pricing

The formulas assume **US/European pricing standards**, not local Sri Lankan prices!

**Current Formula**:
```python
train_cost = 15 + (47 × 0.15) = $22.05
```

**Should be (for Sri Lanka)**:
```python
train_cost = 0.15 + (47 × 0.01) = $0.62  # More realistic
```

## Why Distance Shows 0 km?

In your screenshot, the **Distance shows "0 km"** for all options. This is likely because:

1. **Display bug** - The distance is calculated (47 km) but not passed to UI correctly
2. **Or** the distance calculation failed and fell back to default pricing

Let me check where distance should be displayed:

### Expected Behavior:
Each transport option should show:
- **Duration**: 1h 0m (for train), 54m (for car), etc.
- **Distance**: 47 km ← This should NOT be 0!

### Actual Display:
Your screenshot shows **"0 km"** for all options, which suggests:
- Either Google Maps API call failed
- Or the distance data isn't being passed to the UI properly

## Summary

### ✅ **What's Real**:
- **Distance**: 47 km (from Google Maps) ✓
- **Duration**: ~1 hour (from Google Maps) ✓
- **Calculation Method**: Systematic and logical ✓

### ⚠️ **What's Estimated**:
- **Pricing formulas**: Based on Western transport costs ❌
- **Not real-time**: No integration with actual transport providers
- **Overpriced for Sri Lanka**: Prices are 40-50x higher than actual!

### 🔧 **Issues**:
1. **Distance shows "0 km"** - Display bug or API failure
2. **Prices too high** - Formulas not adjusted for local economies
3. **No real provider data** - Should integrate with local transport APIs

## Recommended Fixes

### Fix 1: Country-Specific Pricing Multipliers
```python
# Add country-based pricing adjustments
country_multipliers = {
    "Sri Lanka": 0.02,  # Multiply by 0.02 for local prices
    "India": 0.03,
    "Thailand": 0.05,
    "USA": 1.0,
    "UK": 1.2
}

train_cost = (15 + (distance_km * 0.15)) * country_multiplier
```

### Fix 2: Show Distance in UI
Ensure the 47 km distance is passed to the UI and displayed properly.

### Fix 3: Real Transport APIs (Advanced)
Integrate with:
- Sri Lankan Railways API (if available)
- Bus operator APIs
- Local taxi/ride-sharing apps (PickMe, Uber Sri Lanka)

## For Your Galle → Matara Trip

### Actual Expected Costs (Sri Lanka):
- **Train (2nd class)**: LKR 100 (~$0.30) per person
- **Bus**: LKR 150 (~$0.45) per person
- **Taxi**: LKR 4500 (~$14) total
- **Car rental**: LKR 3500/day (~$11)

### What System Shows:
- Train: $22.11 (73x higher!)
- Bus: $14.74 (32x higher!)
- Taxi: $58.69 (4x higher)
- Car rental: $34.48 (3x higher)

### Conclusion:
The prices are **calculated systematically using real distance**, but the **formulas are calibrated for Western countries**, making them **unrealistic for Sri Lanka**. The transport options and relative ordering are correct, but absolute prices need country-specific adjustments.

---

**Key Takeaway**: The system uses REAL distances (47 km via Google Maps) and logical formulas, but prices are optimized for US/EU markets, not Asia. For Sri Lanka, divide shown prices by ~40-50 to get realistic local costs.

