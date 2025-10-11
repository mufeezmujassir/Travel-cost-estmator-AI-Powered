# Accommodation Cost Calculation Fix

## Issue
The system was multiplying hotel costs by the **number of travelers**, assuming each traveler needs a separate room. This resulted in **unrealistic accommodation costs** that were often **double** the actual price for couples or groups sharing rooms.

### Example Problem:
**Your Search (Galle → Paris, 2 travelers, 5 nights)**:
- Hotel: Tiny Gallery Paris Gare Montparnasse at $178/night
- **Old calculation**: $178 × 5 nights × 2 travelers = **$1,780**
- **Reality**: Most couples share 1 room = $178 × 5 nights = **$890**
- **Overcharge**: $890 (100% more than needed!)

## Root Cause

### Old Formula (Line 82):
```python
accommodation_cost = price_per_night * trip_duration * request.travelers
```

This assumed:
- 1 traveler = 1 room
- 2 travelers = 2 rooms ❌
- 3 travelers = 3 rooms ❌
- 4 travelers = 4 rooms ❌

**Problem**: Most travelers share rooms!

## Solution

### New Formula (Lines 82-85):
```python
# Calculate rooms needed - assume 2 travelers share 1 room
# 1 traveler = 1 room, 2 travelers = 1 room, 3 travelers = 2 rooms, etc.
rooms_needed = (request.travelers + 1) // 2
accommodation_cost = price_per_night * trip_duration * rooms_needed
```

### How It Works:
```python
rooms_needed = (travelers + 1) // 2  # Integer division, rounds up
```

**Examples**:
- 1 traveler: (1+1)//2 = 1 room ✓
- 2 travelers: (2+1)//2 = 1 room ✓ (sharing)
- 3 travelers: (3+1)//2 = 2 rooms ✓
- 4 travelers: (4+1)//2 = 2 rooms ✓ (2 per room)
- 5 travelers: (5+1)//2 = 3 rooms ✓

**Assumption**: 2 people per room (standard double occupancy)

## Impact

### Before Fix:
```
Travelers | Rooms Calculated | Hotel $178/night × 5 nights
----------|------------------|---------------------------
    1     |        1         |  $890
    2     |        2         |  $1,780  ❌ Too much!
    3     |        3         |  $2,670  ❌ Too much!
    4     |        4         |  $3,560  ❌ Too much!
```

### After Fix:
```
Travelers | Rooms Needed | Hotel $178/night × 5 nights
----------|--------------|---------------------------
    1     |      1       |  $890   ✓
    2     |      1       |  $890   ✓ Shared room
    3     |      2       |  $1,780 ✓ 1 room + 1 single
    4     |      2       |  $1,780 ✓ 2 shared rooms
```

### Your Specific Case (2 travelers):
- **Before**: $178 × 5 × 2 = **$1,780**
- **After**: $178 × 5 × 1 = **$890**
- **Savings**: **$890** (50% reduction!)

### Total Trip Cost Impact:
**Before Fix**:
```
Flights:        $2,862
Accommodation:  $1,780  ← Inflated
Transportation: $559
Activities:     $350
Food:           $600
Miscellaneous:  $100
─────────────────────
Total:          $6,251
```

**After Fix**:
```
Flights:        $2,862
Accommodation:  $890    ← Realistic!
Transportation: $559
Activities:     $350
Food:           $600
Miscellaneous:  $100
─────────────────────
Total:          $5,361
```

**Total Savings**: **$890** (14% cheaper!)

## Benefits

### User Experience:
✅ **Realistic costs** - Matches how people actually travel  
✅ **Better budget accuracy** - No surprise overcharges  
✅ **Fairer pricing** - Couples/families don't pay double  
✅ **Transparent** - Shows actual expected accommodation costs  

### Business Logic:
✅ **Standard hotel practice** - Most hotels charge per room, not per person  
✅ **Industry standard** - 2 people per room is typical  
✅ **Flexible** - Scales correctly for 1-10+ travelers  
✅ **Simple formula** - Easy to understand and maintain  

## Technical Details

### File Modified:
**`backend/agents/cost_estimation_agent.py`**, Lines 75-85

### Changes:
1. Added comment explaining room sharing logic
2. Added `rooms_needed` calculation: `(travelers + 1) // 2`
3. Changed multiplication from `travelers` to `rooms_needed`

### Formula Breakdown:
```python
rooms_needed = (request.travelers + 1) // 2

# Why (travelers + 1)?
# - Rounds up: 3 travelers need 2 rooms, not 1.5
# - Integer division (//): No decimals

# Examples:
# (1 + 1) // 2 = 2 // 2 = 1 room  ✓
# (2 + 1) // 2 = 3 // 2 = 1 room  ✓
# (3 + 1) // 2 = 4 // 2 = 2 rooms ✓
# (4 + 1) // 2 = 5 // 2 = 2 rooms ✓
# (5 + 1) // 2 = 6 // 2 = 3 rooms ✓
```

## Edge Cases Handled

### Single Traveler:
- Needs 1 room: (1+1)//2 = 1 ✓
- Cost: $178 × 5 × 1 = $890

### Odd Number of Travelers:
- 3 travelers: (3+1)//2 = 2 rooms ✓
- Typically: 1 double room + 1 single room
- Cost: $178 × 5 × 2 = $1,780

### Even Number of Travelers:
- 4 travelers: (4+1)//2 = 2 rooms ✓
- Typically: 2 double rooms
- Cost: $178 × 5 × 2 = $1,780

### Large Groups:
- 10 travelers: (10+1)//2 = 5 rooms ✓
- Cost: $178 × 5 × 5 = $4,450

## Alternative Approaches Considered

### Option 1: Fixed 1 Room (Too Simple)
```python
accommodation_cost = price_per_night * trip_duration  # Always 1 room
```
❌ Doesn't work for 3+ travelers

### Option 2: User Input (Complex)
```python
rooms = request.num_rooms  # Let user specify
accommodation_cost = price_per_night * trip_duration * rooms
```
❌ Adds complexity to user input
❌ Most users don't know how many rooms they need

### Option 3: Current Solution (Best Balance) ✓
```python
rooms_needed = (request.travelers + 1) // 2  # Smart calculation
accommodation_cost = price_per_night * trip_duration * rooms_needed
```
✅ Automatic and accurate
✅ Works for all group sizes
✅ Matches real-world hotel booking

## Testing

### Test Cases:

| Travelers | Rooms | Calculation ($178/night × 5 nights) | Expected |
|-----------|-------|-------------------------------------|----------|
| 1 | 1 | $178 × 5 × 1 = $890 | ✓ |
| 2 | 1 | $178 × 5 × 1 = $890 | ✓ |
| 3 | 2 | $178 × 5 × 2 = $1,780 | ✓ |
| 4 | 2 | $178 × 5 × 2 = $1,780 | ✓ |
| 5 | 3 | $178 × 5 × 3 = $2,670 | ✓ |
| 6 | 3 | $178 × 5 × 3 = $2,670 | ✓ |

### Verification:
Run a new search and check:
- 2 travelers should show **$890** accommodation (was $1,780)
- Total cost should be **~$890 cheaper**

## Related Fixes

This is part of the comprehensive pricing improvements:

1. ✅ **UI Overview** - Shows cheapest flight
2. ✅ **UI Flights Tab** - Shows per-person prices  
3. ✅ **Backend Cost Estimation** - Uses cheapest flight
4. ✅ **Backend Flight Selection** - Prioritizes cheapest
5. ✅ **Backend Accommodation** - Realistic room sharing (THIS FIX)

## Deployment

- **Status**: ✅ Ready for deployment
- **Testing**: Run searches with 1-6 travelers to verify
- **Rollback**: Safe (single file, single calculation)
- **Impact**: HIGH - Reduces accommodation costs by up to 50%

### To Test:
1. Restart backend server
2. Search for any trip with 2 travelers
3. Check accommodation cost - should be ~50% lower than before
4. Try with 3 travelers - should show 2 rooms cost

---

**Fixed**: October 10, 2025  
**Version**: 1.0.5  
**Impact**: Accommodation costs now realistic with room sharing  
**Savings**: Up to 50% reduction for couples/groups  
**Files Modified**: `backend/agents/cost_estimation_agent.py` (1 formula)

