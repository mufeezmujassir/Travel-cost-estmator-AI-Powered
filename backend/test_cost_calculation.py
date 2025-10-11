"""
Test Full Cost Calculation
Verify that all costs are calculated correctly
"""

# Simple calculation verification
print("="*70)
print("COST CALCULATION VERIFICATION")
print("="*70)

# Given data from your screenshots
print("\n📊 Transportation Prices (from LLM Agent):")
print("-"*70)
train_price_total = 1.29  # Already for 3 travelers
bus_price_total = 1.71    # Already for 3 travelers
private_car_total = 10.00  # Already for 3 travelers
car_rental = 20.00        # Per day

travelers = 3
trip_days = 2  # Oct 22-24 = 2 nights

print(f"Train (one-way, total for {travelers} travelers): ${train_price_total}")
print(f"Bus (one-way, total for {travelers} travelers): ${bus_price_total}")
print(f"Private car (one-way, total): ${private_car_total}")
print(f"Car rental (daily): ${car_rental}")

print("\n💰 INTER-CITY TRANSPORTATION COST:")
print("-"*70)

# The system uses the cheapest option
cheapest = min(train_price_total, bus_price_total, private_car_total, car_rental)
cheapest_name = "Train" if cheapest == train_price_total else (
    "Bus" if cheapest == bus_price_total else (
    "Private Car" if cheapest == private_car_total else "Car Rental"
))

print(f"Cheapest option: {cheapest_name} = ${cheapest}")
print(f"Round trip (× 2): ${cheapest} × 2 = ${cheapest * 2:.2f}")

inter_city_cost = cheapest * 2
print(f"\n✅ Inter-City Transportation Cost: ${inter_city_cost:.2f}")

print("\n📍 LOCAL TRANSPORTATION (at destination):")
print("-"*70)
local_daily = 12.00  # From your screenshot
local_total = local_daily * trip_days * travelers
print(f"Daily cost: ${local_daily}/person/day")
print(f"Total: ${local_daily} × {trip_days} days × {travelers} travelers = ${local_total:.2f}")

print("\n🏨 ACCOMMODATION:")
print("-"*70)
accommodation_per_night = 50.00  # Example
rooms_needed = (travelers + 1) // 2  # 3 travelers = 2 rooms
accommodation_total = accommodation_per_night * trip_days * rooms_needed
print(f"Price per night: ${accommodation_per_night}")
print(f"Rooms needed: {rooms_needed} (assuming 2 people per room)")
print(f"Total: ${accommodation_per_night} × {trip_days} nights × {rooms_needed} rooms = ${accommodation_total:.2f}")

print("\n🍽️ FOOD & DINING:")
print("-"*70)
food_per_day = 35.00  # Example
food_total = food_per_day * trip_days * travelers
print(f"Estimated: ${food_per_day}/person/day")
print(f"Total: ${food_per_day} × {trip_days} days × {travelers} travelers = ${food_total:.2f}")

print("\n🎭 ACTIVITIES:")
print("-"*70)
activities_per_day = 30.00  # Example
activities_total = activities_per_day * trip_days
print(f"Estimated: ${activities_per_day}/day for group")
print(f"Total: ${activities_per_day} × {trip_days} days = ${activities_total:.2f}")

print("\n💵 MISCELLANEOUS:")
print("-"*70)
misc_per_person = 10.00  # Example
misc_total = misc_per_person * trip_days * travelers
print(f"Estimated: ${misc_per_person}/person/day")
print(f"Total: ${misc_per_person} × {trip_days} days × {travelers} travelers = ${misc_total:.2f}")

print("\n" + "="*70)
print("TOTAL COST BREAKDOWN:")
print("="*70)

total_cost = (
    inter_city_cost +
    local_total +
    accommodation_total +
    food_total +
    activities_total +
    misc_total
)

print(f"Inter-City Transportation:  ${inter_city_cost:>7.2f}")
print(f"Local Transportation:       ${local_total:>7.2f}")
print(f"Accommodation:              ${accommodation_total:>7.2f}")
print(f"Food & Dining:              ${food_total:>7.2f}")
print(f"Activities:                 ${activities_total:>7.2f}")
print(f"Miscellaneous:              ${misc_total:>7.2f}")
print("-"*70)
print(f"TOTAL:                      ${total_cost:>7.2f}")
print(f"Per Person:                 ${total_cost/travelers:>7.2f}")

print("\n" + "="*70)
print("COMPARISON WITH YOUR SCREENSHOT:")
print("="*70)
your_total = 659.74
your_inter_city = 79.74

print(f"Your Inter-City Cost:     ${your_inter_city}")
print(f"Expected (Train × 2):     ${inter_city_cost:.2f}")
print(f"Difference:               ${your_inter_city - inter_city_cost:.2f}")

if abs(your_inter_city - inter_city_cost) > 0.01:
    print(f"\n❌ ISSUE DETECTED!")
    print(f"   The cost ${your_inter_city} suggests it's calculating:")
    print(f"   ${train_price_total} × 2 (round trip) × {travelers} (travelers) = ${train_price_total * 2 * travelers:.2f}")
    print(f"\n   But train price is ALREADY for all {travelers} travelers!")
    print(f"   Correct calculation: ${train_price_total} × 2 = ${train_price_total * 2:.2f}")
    print(f"\n   💡 This was the bug we just fixed!")
else:
    print(f"\n✅ Calculation is correct!")

print("\n" + "="*70)

