# 🎭 Vibe-Based Food Cost Adjustments

## Available Vibes

The system supports these travel vibes (from `models/travel_models.py`):

1. **ROMANTIC** - Couples, nice dinners, upscale restaurants
2. **ADVENTURE** - Active travelers, practical meals, quick eats
3. **BEACH** - Casual dining, seafood, beach bars
4. **NATURE** - Local food, eco-friendly, sustainable
5. **CULTURAL** - Try local specialties, traditional cuisine
6. **CULINARY** - Food-focused, fine dining, food tours
7. **WELLNESS** - Healthy options, organic, fresh

---

## Food Cost Multipliers

| Vibe | Budget Style | Multiplier | Example (Base $15/day) |
|------|--------------|------------|------------------------|
| **CULINARY** | Upscale (food-focused) | ×1.5 | $15 → $22.50/day |
| **ROMANTIC** | Balanced (leaning upscale) | ×1.3 | $15 → $19.50/day |
| **WELLNESS** | Balanced (healthy options) | ×1.2 | $15 → $18.00/day |
| **CULTURAL** | Balanced (local specialties) | ×1.0 | $15 → $15.00/day |
| **ADVENTURE** | Balanced (practical meals) | ×1.0 | $15 → $15.00/day |
| **BEACH** | Balanced (casual dining) | ×1.0 | $15 → $15.00/day |
| **NATURE** | Balanced (local food) | ×1.0 | $15 → $15.00/day |

---

## Examples: Matara, Sri Lanka (3 travelers, 2 days)

Base Cost: $12/day/person = $72 total

| Vibe | Daily/Person | Total (3 travelers, 2 days) |
|------|--------------|------------------------------|
| **CULINARY** | $18.00 | $108 |
| **ROMANTIC** | $15.60 | $93.60 |
| **WELLNESS** | $14.40 | $86.40 |
| **CULTURAL** | $12.00 | **$72** ✅ |
| **ADVENTURE** | $12.00 | **$72** ✅ |
| **BEACH** | $12.00 | **$72** ✅ |
| **NATURE** | $12.00 | **$72** ✅ |

---

## LLM Prompt Adjustments

The system sends vibe-specific instructions to the LLM:

### CULINARY (×1.5)
```
Travel Style: Upscale (food-focused)

You're estimating for culinary travelers who:
- Prioritize food experiences
- Visit nicer restaurants and food tours
- Try special local dishes
- Budget more for dining
```

### ROMANTIC (×1.3)
```
Travel Style: Balanced (leaning upscale)

You're estimating for romantic travelers who:
- Prefer nice dinners at upscale restaurants
- Occasional special dining experiences
- Mix of local and tourist restaurants
```

### WELLNESS (×1.2)
```
Travel Style: Balanced (healthy options)

You're estimating for wellness travelers who:
- Seek healthy, organic options
- Visit health-conscious cafes
- Fresh juices and smoothies
- May pay more for quality ingredients
```

### CULTURAL (×1.0)
```
Travel Style: Balanced (try local specialties)

You're estimating for cultural travelers who:
- Try authentic local cuisine
- Visit traditional restaurants
- Experience street food
- Prioritize authenticity over luxury
```

---

## Implementation Details

### In `food_cost_estimator.py`:

```python
def _vibe_to_budget_style(self, vibe: VibeType) -> str:
    """Map vibe to budget style"""
    mapping = {
        VibeType.ROMANTIC: "Balanced (leaning upscale)",
        VibeType.ADVENTURE: "Balanced (practical meals)",
        VibeType.BEACH: "Balanced (casual dining)",
        VibeType.NATURE: "Balanced (local food)",
        VibeType.CULTURAL: "Balanced (try local specialties)",
        VibeType.CULINARY: "Upscale (food-focused)",
        VibeType.WELLNESS: "Balanced (healthy options)"
    }
    return mapping.get(vibe, "Balanced")
```

### Fallback Multipliers:

```python
if vibe == VibeType.CULINARY:
    daily_per_person = base_daily * 1.5
elif vibe == VibeType.ROMANTIC:
    daily_per_person = base_daily * 1.3
elif vibe == VibeType.WELLNESS:
    daily_per_person = base_daily * 1.2
else:
    daily_per_person = base_daily
```

---

## Real-World Examples

### Tokyo, Japan (Base: $45/day)

| Vibe | Daily Cost | 3 Day Trip (2 people) |
|------|------------|------------------------|
| CULINARY | $67.50 | $405 |
| ROMANTIC | $58.50 | $351 |
| CULTURAL | $45.00 | $270 |

### Bangkok, Thailand (Base: $18/day)

| Vibe | Daily Cost | 5 Day Trip (3 people) |
|------|------------|------------------------|
| CULINARY | $27.00 | $405 |
| ROMANTIC | $23.40 | $351 |
| CULTURAL | $18.00 | $270 |

---

## Conclusion

The vibe-based adjustments ensure that food costs reflect travelers' actual spending patterns:

- **Food enthusiasts** (CULINARY) → +50% for fine dining
- **Romantic couples** (ROMANTIC) → +30% for nice dinners
- **Health-conscious** (WELLNESS) → +20% for organic options
- **Experience seekers** (CULTURAL, ADVENTURE, BEACH, NATURE) → Standard rates

This provides accurate, personalized cost estimates! 🎉

