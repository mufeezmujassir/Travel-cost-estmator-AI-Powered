# Pricing Inconsistency Analysis & Fixes

## Issue Summary

Multiple pricing inconsistencies exist across the UI:

| Location | Price Shown | Expected | Issue |
|----------|-------------|----------|-------|
| **Overview "Best Flight"** | $2066/person (SriLankan) | $1497/person (China Eastern) | Wrong flight selected |
| **Flights Tab** | $1497/person (China Eastern) | ✓ Correct | Shows cheapest |
| **Price Calendar** | $716/person | $1497/person | Different data source |
| **Cost Breakdown** | $8264 total (2 travelers) | $5988 expected | Using wrong flight |

---

## Problem 1: Overview Shows Wrong Flight

### Issue:
Overview displays `results.flights[0]` (first flight), but the array order from backend may not match cheapest-first.

### Root Cause:
The backend `_select_best_flights()` method DOES sort by score (cheapest first), but:
1. The flights might be re-ordered somewhere in the pipeline
2. Or the scoring algorithm isn't working correctly

### Example from Screenshots:
```javascript
results.flights = [
  { airline: "SriLankan", price: 4132 },    // [0] - shown in overview ($2066/person)
  { airline: "China Eastern", price: 2994 }, // [1] - actually cheapest ($1497/person)
  { airline: "Etihad", price: 2996 }        // [2]
]
```

### Fix:
The UI should find the minimum price flight, not just use `[0]`:

```javascript
// In OverviewTab, replace:
${results?.flights?.[0]?.price ? Math.round(results.flights[0].price / formData.travelers) : 'N/A'}

// With:
${(() => {
  if (!results?.flights || results.flights.length === 0) return 'N/A';
  const cheapestFlight = results.flights.reduce((min, flight) => 
    flight.price < min.price ? flight : min
  );
  return Math.round(cheapestFlight.price / formData.travelers);
})()}
```

---

## Problem 2: Price Calendar vs Available Flights

### Issue:
- **Price Calendar**: $716/person (cheapest)
- **Available Flights**: $1497/person (cheapest)

### Root Causes:

#### Possibility 1: Date Mismatch
The price calendar shows prices for a **different date range** than the actual search:
- User selected: **October 22, 2025**
- Price calendar showing: **October 15-24, 2025**
- Cheapest date: **October 22 at $716**

But the available flights for October 22 show **$1497** as cheapest.

#### Possibility 2: One-Way vs Round-Trip
- **Price Calendar**: Showing **one-way** prices ($716)
- **Available Flights**: Showing **round-trip** prices ($1497 × 2 = $2994 total)

This would explain the ~2x difference:
- $716 one-way × 2 = $1432 round-trip ≈ $1497 round-trip ✓

#### Possibility 3: Different Routes/Airlines
Price calendar might include budget airlines or routes not shown in "Available Flights" list.

### Investigation Needed:
Check the SERP API response for price calendar vs flight search to see:
1. Are price calendar prices one-way or round-trip?
2. Do they include the same airlines?
3. Are they for the exact same route?

---

## Problem 3: Cost Breakdown Mismatch

### Issue:
**Cost Breakdown shows**: $8264 for flights (2 travelers)
**Expected from cheapest flight**: $1497 × 2 travelers = $2994 total

### Calculation:
$8264 ÷ 2 travelers = **$4132 per traveler**

This matches the **SriLankan flight price** ($2066 × 2 = $4132)!

### Root Cause:
The **CostEstimationAgent** is using `flights[0]` which is SriLankan, not the cheapest China Eastern.

### Backend Issue:
```python
# In cost_estimation_agent.py
flights = context["flight_search_agent"]["data"]["flights"]
if flights:
    flight_cost_per_person = flights[0]["price"]  # ❌ Using first flight
    total_flight_cost = flight_cost_per_person * request.travelers
```

Should be:
```python
# Find cheapest flight
cheapest_flight = min(flights, key=lambda x: x["price"])
flight_cost_per_person = cheapest_flight["price"]
```

---

## Problem 4: Backend Flight Sorting

### Issue:
The flight scoring algorithm should select cheapest flight first, but it's not working correctly.

### Current Algorithm:
```python
def flight_score(flight: Flight) -> float:
    price_score = 1.0 / (flight.price + 1)      # Lower price = higher score ✓
    stops_score = 1.0 / (flight.stops + 1)      # Fewer stops = higher score ✓
    return price_score * 0.7 + stops_score * 0.3

sorted_flights = sorted(flights, key=flight_score, reverse=True)  # Highest score first
```

### Test with Real Data:
```
SriLankan: $4132, 0 stops
  price_score = 1/(4132+1) = 0.000242
  stops_score = 1/(0+1) = 1.0
  total = 0.000242 × 0.7 + 1.0 × 0.3 = 0.300169

China Eastern: $2994, 1 stop
  price_score = 1/(2994+1) = 0.000334
  stops_score = 1/(1+1) = 0.5
  total = 0.000334 × 0.7 + 0.5 × 0.3 = 0.150234

Etihad: $2996, 1 stop
  total ≈ 0.150233
```

**Result**: SriLankan scores **0.300169** (highest) due to 0 stops, despite being most expensive!

### The Bug:
The algorithm weights **stops too heavily** (30%) compared to price (70%). A direct flight that costs **$1000 more** can still score higher!

---

## Recommended Fixes

### Fix 1: Update Flight Scoring Algorithm (Backend)

**Priority**: HIGH

```python
# backend/agents/flight_search_agent.py

def flight_score(flight: Flight) -> float:
    # Normalize price to 0-1 scale (assuming max price ~$5000)
    price_score = 1.0 - (flight.price / 5000.0)
    
    # Stops penalty (each stop reduces score)
    stops_penalty = 0.1 * flight.stops
    
    # Price is 90% of score, stops is 10%
    return max(0, price_score - stops_penalty)

# Or simply: sort by price only!
sorted_flights = sorted(flights, key=lambda f: f.price)
```

### Fix 2: UI - Always Show Cheapest Flight

**Priority**: HIGH

Update `OverviewTab` to find and display the actually cheapest flight:

```javascript
const OverviewTab = ({ results, formData, selectedVibe }) => {
  // Find cheapest flight
  const cheapestFlight = results?.flights?.length > 0
    ? results.flights.reduce((min, flight) => flight.price < min.price ? flight : min)
    : null;
  
  const cheapestPrice = cheapestFlight 
    ? Math.round(cheapestFlight.price / formData.travelers)
    : 'N/A';

  return (
    // ... rest of component
    <p className="text-2xl font-bold text-blue-600">${cheapestPrice}</p>
    <p className="text-sm text-gray-600">{cheapestFlight?.airline || 'Multiple options'}</p>
  );
}
```

### Fix 3: Backend - Use Cheapest Flight in Cost Calculation

**Priority**: HIGH

```python
# backend/agents/cost_estimation_agent.py

flights = context["flight_search_agent"]["data"]["flights"]
if flights:
    # Find cheapest flight
    cheapest_flight = min(flights, key=lambda x: x.get("price", float('inf')))
    flight_cost_per_person = cheapest_flight["price"]
    total_flight_cost = flight_cost_per_person * request.travelers
```

### Fix 4: Price Calendar Clarification

**Priority**: MEDIUM

Add clarification text to price calendar:

```javascript
<p className="text-xs text-gray-500">
  * Prices shown are approximate and may vary based on availability
</p>
```

Or better: fetch actual prices for the same route/airline shown in available flights.

---

## Summary

| Problem | Location | Priority | Fix |
|---------|----------|----------|-----|
| Wrong flight in overview | UI (Overview) | HIGH | Find min price flight |
| Wrong flight in costs | Backend (CostEstimationAgent) | HIGH | Use cheapest flight |
| Flight scoring broken | Backend (FlightSearchAgent) | HIGH | Fix scoring algorithm |
| Price calendar mismatch | API/Display | MEDIUM | Add clarification |

---

**Created**: October 10, 2025  
**Status**: Analysis Complete, Fixes Needed

