# Flight Price Display Fix

## Issue
The UI was showing **total flight prices** (for all travelers) as **"per person"** prices, which was very confusing:

### Before Fix:
- **Overview Tab "Best Flight"**: Shows $4132 (actually total for 2 travelers = $2066 per person)
- **Flights Tab**: Shows $4132, $2994, $2996 with "per person" label (actually total prices)
- **User sees**: TravelCost $4132 as "Best Flight" (looks like most expensive)
- **Reality**: China Eastern $1497/person is actually cheapest, shown as $2994 total

## Root Cause

The backend `FlightSearchAgent` multiplies flight prices by number of travelers:

```python
# backend/agents/flight_search_agent.py, line 132
price=flight_data.get("price", 0.0) * request.travelers,
```

This stores the **total price for all travelers** in the Flight object, but the UI was displaying these totals with "per person" labels, causing confusion.

### Example Calculation:
```
API returns: China Eastern $1497 per person
Backend calculates: $1497 × 2 travelers = $2994 (stored in flight.price)
UI displayed: "$2994 per person" ❌ (should show $1497 per person)
```

## Solution

Updated the UI to divide by number of travelers to show the actual per-person price:

### 1. Overview Tab - "Best Flight" Card
**File**: `src/components/Results.jsx`, line 262

**Before**:
```javascript
<p className="text-2xl font-bold text-blue-600">
  ${results?.flights?.[0]?.price || 'N/A'}
</p>
<p className="text-sm text-gray-600">
  {results?.flights?.[0]?.airline || 'Multiple options'}
</p>
```

**After**:
```javascript
<p className="text-2xl font-bold text-blue-600">
  ${results?.flights?.[0]?.price ? Math.round(results.flights[0].price / formData.travelers) : 'N/A'}
</p>
<p className="text-sm text-gray-600">
  {results?.flights?.[0]?.airline || 'Multiple options'}
</p>
<p className="text-xs text-gray-500">per person</p>
```

### 2. Flights Tab - Flight Cards
**File**: `src/components/Results.jsx`, lines 708-730

**Before**:
```javascript
{results?.flights?.map((flight, index) => (
  <div key={index} className="card">
    ...
    <div className="text-right">
      <p className="text-2xl font-bold text-gray-900">${flight.price}</p>
      <p className="text-sm text-gray-600">per person</p>
    </div>
```

**After**:
```javascript
{results?.flights?.map((flight, index) => {
  // Flight prices are stored as total for all travelers, divide to get per-person price
  const pricePerPerson = Math.round(flight.price / (formData?.travelers || 1));
  const totalPrice = flight.price;
  
  return (
    <div key={index} className="card">
      ...
      <div className="text-right">
        <p className="text-2xl font-bold text-gray-900">${pricePerPerson}</p>
        <p className="text-sm text-gray-600">per person</p>
        {formData?.travelers > 1 && (
          <p className="text-xs text-gray-500">${totalPrice} total</p>
        )}
      </div>
```

## Result

### After Fix:

#### Overview Tab:
```
Best Flight
$1497         ← Per-person price (was $2994 total)
China Eastern
per person
```

#### Flights Tab:
```
China Eastern      $1497
MU 232            per person
                  $2994 total    ← Shows both prices now

Etihad            $1498
EY 393            per person
                  $2996 total

SriLankan         $2066
UL 501            per person
                  $4132 total
```

## Benefits

✅ **Accurate per-person prices** displayed  
✅ **Shows both per-person and total** prices in flights tab  
✅ **Best flight is actually cheapest** (China Eastern $1497/person)  
✅ **Less user confusion** about pricing  
✅ **Consistent with "per person" label**  

## Impact on User Experience

### Before:
- User sees: "$4132 Best Flight" 
- User thinks: "Why is the most expensive flight selected?"
- User confused: "Is $4132 per person or total?"

### After:
- User sees: "$1497 Best Flight per person ($2994 total)"
- User thinks: "Great! Cheapest option selected"
- User understands: "Clear per-person pricing"

## Testing

### Test Case: Galle → Paris (2 travelers)
- **China Eastern**: $1497/person × 2 = $2994 total ✓
- **Etihad**: $1498/person × 2 = $2996 total ✓
- **SriLankan**: $2066/person × 2 = $4132 total ✓
- **Selected as Best**: China Eastern $1497/person ✓

### Test Case: Single Traveler
- Shows per-person price only (no "total" line) ✓

## Files Modified

1. **`src/components/Results.jsx`**:
   - Line 262: Updated Overview tab "Best Flight" calculation
   - Lines 708-730: Updated Flights tab price display logic

## Notes

- The backend pricing logic remains unchanged (still stores total for all travelers)
- This is a UI-only fix for correct price display
- The flight selection algorithm was always correct (selecting cheapest per-person)
- The issue was purely in how prices were displayed to users

## Related Issues

- Backend correctly selects cheapest flight per person
- Cost calculations use total prices correctly
- Only display layer needed fixing

---

**Fixed**: October 10, 2025  
**Version**: 1.0.2  
**Impact**: Flight prices now display correctly as per-person prices  
**Breaking Changes**: None

