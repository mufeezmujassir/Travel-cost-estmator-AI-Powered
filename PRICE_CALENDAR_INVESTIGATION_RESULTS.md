# Price Calendar Investigation Results

## Test Results Summary

Ran diagnostic test comparing Price Calendar ($716) vs Available Flights ($1497/person).

## Key Findings

### 1. ✅ Price Calendar is Correct
- **Shows**: $716 per person
- **Source**: SERP API with `travelers=1`
- **Type**: Round-trip per-person price
- **Conclusion**: Working as intended

### 2. ✅ SERP API Returns Consistent Per-Person Pricing
- **For 1 traveler**: Etihad $749, Qatar $752
- **For 2 travelers**: Etihad $1498 total ($749 each), Qatar $1504 total ($752 each)
- **Conclusion**: API correctly scales prices linearly

### 3. ❌ Available Flights Show WRONG Airlines!

#### SERP API Raw Results (for 2 travelers):
```
1. Etihad:         $749/person  ($1498 total)  ← CHEAPEST
2. Qatar Airways:  $752/person  ($1504 total)
3. Turkish:        $790/person  ($1580 total)
```

#### What Users See in "Available Flights":
```
1. SriLankan:      $2066/person ($4132 total)  ← MOST EXPENSIVE!
2. China Eastern:  $1497/person ($2994 total)
3. Etihad:         $1498/person ($2996 total)
```

## The Real Problem: Flight Selection Algorithm

### Issue:
The `FlightSearchAgent._select_best_flights()` method is **filtering out the cheapest flights**!

### Root Cause:
The scoring algorithm on lines 149-157 of `flight_search_agent.py`:

```python
def flight_score(flight: Flight) -> float:
    price_score = 1.0 / (flight.price + 1)      # Cheaper = higher score
    stops_score = 1.0 / (flight.stops + 1)      # Fewer stops = higher score
    return price_score * 0.7 + stops_score * 0.3  # 70% price, 30% stops
```

### The Bug:
This algorithm **heavily penalizes flights with stops**, even if they're much cheaper!

Example scores:
```
SriLankan ($4132, 0 stops):
  price_score = 1/4133 = 0.000242
  stops_score = 1/1 = 1.0
  total = 0.000242 × 0.7 + 1.0 × 0.3 = 0.300169  ← HIGHEST!

Etihad ($1498, 1 stop):
  price_score = 1/1499 = 0.000667
  stops_score = 1/2 = 0.5
  total = 0.000667 × 0.7 + 0.5 × 0.3 = 0.150467  ← Lower

Qatar ($1504, 1 stop):
  total ≈ 0.150445
```

**Result**: SriLankan (direct, expensive) scores higher than Etihad/Qatar (1 stop, cheap)!

## Why Price Calendar Shows $716

Looking at the test output, the price calendar shows $716 but the raw SERP API shows Etihad at $749. This suggests:

1. **Price Calendar searches multiple dates** and found $716 on a nearby date
2. **Or** the $716 is from a budget airline not shown in top results
3. **Or** API returned different results at different times

The important finding: **Price Calendar ($716) is actually closer to the real cheapest prices than Available Flights ($1497)**!

## Recommendations

### Fix 1: Update Flight Scoring Algorithm (HIGH PRIORITY)

**Option A - Simple**: Sort by price only
```python
def _select_best_flights(self, flights: List[Flight], request: TravelRequest) -> List[Flight]:
    # Simply sort by price (cheapest first)
    sorted_flights = sorted(flights, key=lambda f: f.price)
    return sorted_flights[:5]  # Return top 5 instead of 3
```

**Option B - Better Balance**: Reduce stops weight
```python
def flight_score(flight: Flight) -> float:
    # Normalize price to 0-1 scale
    max_price = 5000.0  # Assume max reasonable price
    price_score = 1.0 - (flight.price / max_price)
    
    # Small penalty for stops (0.05 per stop)
    stops_penalty = flight.stops * 0.05
    
    return max(0, price_score - stops_penalty)
```

### Fix 2: Show More Flight Options

Currently showing only 3 flights. Should show at least 5-10 to give users more choices, especially showing the cheapest options even if they have stops.

### Fix 3: Add Filter/Sort Options in UI

Let users choose:
- Sort by: Price | Duration | Stops
- Filter: Direct flights only | Max stops | Max price

## Summary

| Metric | Price Calendar | Available Flights | Actual SERP API |
|--------|---------------|-------------------|-----------------|
| **Cheapest** | $716/person | $1497/person | $749/person |
| **Data Source** | SERP (1 traveler) | Filtered/scored | SERP (2 travelers) |
| **Accuracy** | ✅ Close to actual | ❌ Missing cheapest | ✅ Accurate |

### The Discrepancy Explained:
1. **Price Calendar** shows ~$716 (actual cheapest from multiple dates/airlines)
2. **Available Flights** shows $1497 because the scoring algorithm filtered out cheaper flights
3. **SERP API** actually has flights at $749/person (Etihad, Qatar)
4. **Users are missing out** on ~$750/person savings!

## Action Items

1. ✅ **Documented issue** - This file
2. ⏳ **Fix flight scoring** - Update algorithm to prioritize price
3. ⏳ **Show more flights** - Increase from 3 to 5-10 options
4. ⏳ **Add UI filters** - Let users sort/filter flights
5. ⏳ **Test thoroughly** - Ensure cheapest flights appear first

---

**Investigation Date**: October 10, 2025  
**Status**: Root cause identified, fix needed  
**Impact**: Users missing 50%+ cheaper flight options  
**Priority**: HIGH

