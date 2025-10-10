# How Hotel Costs Become Accommodation Costs

## Overview
The system calculates accommodation costs by taking the hotel's **price per night** and multiplying it by **trip duration** and **number of travelers**.

## Step-by-Step Process

### 1. Hotel Search Agent Finds Hotels
**File**: `backend/agents/hotel_search_agent.py`

```python
# Line 110-134: Process raw hotel data
hotel = Hotel(
    name=hotel_data.get("name", "Unknown Hotel"),
    price_per_night=hotel_data.get("price_per_night", 0.0),  # ← Key field
    rating=hotel_data.get("rating", 0.0),
    amenities=hotel_data.get("amenities", []),
    # ... other fields
)
```

**Example from your search**:
- Hotel: "Tiny Gallery Paris Gare Montparnasse"
- **Price per night**: $178

### 2. Cost Estimation Agent Calculates Total
**File**: `backend/agents/cost_estimation_agent.py`, Lines 75-82

```python
# Accommodation costs
accommodation_cost = 0
if "hotel_search_agent" in agent_data:
    hotels_data = agent_data["hotel_search_agent"].get("data", {})
    hotels = hotels_data.get("hotels", [])
    if hotels:
        price_per_night = hotels[0].get("price_per_night", 0)  # ← Uses first hotel
        accommodation_cost = price_per_night * trip_duration * request.travelers
```

### 3. Calculation Formula

```
Accommodation Cost = Price Per Night × Trip Duration × Number of Travelers
```

### 4. Example from Your Search

**Your Trip Details**:
- **Hotel**: Tiny Gallery Paris Gare Montparnasse
- **Price per night**: $178
- **Trip duration**: October 22 to October 27 = 5 nights
- **Travelers**: 2 people

**Calculation**:
```
Accommodation Cost = $178 × 5 nights × 2 travelers
                   = $178 × 10
                   = $1,780
```

**Result**: Matches your screenshot showing **$1780.00** ✓

## Important Details

### Which Hotel is Used?
```python
price_per_night = hotels[0].get("price_per_night", 0)  # Uses hotels[0]
```

The system uses **the first hotel** in the list (`hotels[0]`), which is:
- The "best" hotel selected by the `HotelSearchAgent`
- Sorted by a scoring algorithm (60% rating, 40% price)
- Usually the highest-rated hotel that's reasonably priced

### Why Multiply by Travelers?
```python
accommodation_cost = price_per_night * trip_duration * request.travelers
```

**Assumption**: Each traveler needs their own room or the cost scales linearly.

**Your case**:
- 2 travelers
- Hotel shows $178/night (per room)
- System calculates: $178 × 5 nights × 2 = $1,780

**This might not always be accurate** because:
- 2 people can share 1 room → Should be $178 × 5 = $890
- Or need 2 rooms → Should be $178 × 2 rooms × 5 nights = $1,780 ✓

### Current Behavior:
The system assumes **1 room per traveler**, so:
- 1 traveler = 1 room
- 2 travelers = 2 rooms (or 2x the cost)
- 3 travelers = 3 rooms (or 3x the cost)

## Potential Issue

### The Problem:
Looking at your costs breakdown:
- **Flights**: $2862 for 2 travelers = $1431/person
- **Accommodation**: $1780 for 2 travelers = $890/person

But if 2 travelers share 1 room:
- **Actual accommodation**: $178 × 5 nights = $890 total
- **System shows**: $1780 (double!)

### Why This Happens:
```python
accommodation_cost = price_per_night * trip_duration * request.travelers
#                                                       ↑ This multiplies by 2!
```

The formula assumes each traveler needs a separate room.

## Possible Fix

### Option 1: Assume Room Sharing (Recommended)
```python
# Accommodation costs - don't multiply by travelers (they share rooms)
accommodation_cost = 0
if "hotel_search_agent" in agent_data:
    hotels_data = agent_data["hotel_search_agent"].get("data", {})
    hotels = hotels_data.get("hotels", [])
    if hotels:
        price_per_night = hotels[0].get("price_per_night", 0)
        # Calculate rooms needed (e.g., 2 people = 1 room, 3 people = 2 rooms)
        rooms_needed = (request.travelers + 1) // 2  # Round up, 2 per room
        accommodation_cost = price_per_night * trip_duration * rooms_needed
```

**Example**:
- 1 traveler → 1 room → $178 × 5 = $890
- 2 travelers → 1 room → $178 × 5 = $890
- 3 travelers → 2 rooms → $178 × 5 × 2 = $1,780
- 4 travelers → 2 rooms → $178 × 5 × 2 = $1,780

### Option 2: Add Room Configuration
Allow users to specify:
- "Shared room" (2 travelers share)
- "Separate rooms" (1 room per traveler)

### Option 3: Use Total Trip Cost Per Room
```python
# For most travel scenarios, assume room sharing
accommodation_cost = price_per_night * trip_duration
# Don't multiply by travelers - the price is for the room, not per person
```

## Summary

| Step | What Happens | Your Example |
|------|--------------|--------------|
| 1. Hotel selected | System picks best hotel | Tiny Gallery Paris |
| 2. Get price/night | Extract price_per_night | $178 |
| 3. Calculate duration | return_date - start_date | 5 nights |
| 4. Multiply by travelers | price × nights × travelers | $178 × 5 × 2 = $1,780 |
| 5. Show in UI | Display as "Accommodation" | **$1780.00** |

### Current Formula:
```
$178/night × 5 nights × 2 travelers = $1,780
```

### More Realistic Formula:
```
$178/night × 5 nights × 1 room = $890  (if sharing)
```

## Recommendation

**Should the system multiply by travelers for accommodation?**

❌ **Probably not** - Most couples/families share rooms  
✅ **Better approach**: Calculate based on rooms needed (travelers ÷ 2)

Would you like me to fix this so the accommodation cost is more realistic for travelers sharing rooms?

---

**Current Behavior**: Multiplies hotel price by number of travelers  
**Your Case**: $178 × 5 × 2 = $1,780  
**More Realistic**: $178 × 5 × 1 = $890 (shared room)  
**Potential Overcharge**: ~$890 (100%!)

