from datetime import datetime


class RideBooking:
    VEHICLE_RATES = {
        "Bike": {"base": 40, "per_km": 8, "max_passengers": 1},
        "Sedan": {"base": 80, "per_km": 14, "max_passengers": 4},
        "SUV": {"base": 120, "per_km": 18, "max_passengers": 6},
        "Premium": {"base": 200, "per_km": 25, "max_passengers": 4}
    }

    def __init__(self, customer_id, pickup, drop, distance,
                 passengers, vehicle_type, booking_time,
                 driver_available=True, promo_discount=0):

        self.customer_id = customer_id
        self.pickup = pickup
        self.drop = drop
        self.distance = distance
        self.passengers = passengers
        self.vehicle_type = vehicle_type
        self.booking_time = booking_time
        self.driver_available = driver_available
        self.promo_discount = promo_discount

    def validate_booking(self):
        if self.distance <= 0:
            return False, "Invalid distance"

        if self.passengers <= 0:
            return False, "Invalid passenger count"

        if self.vehicle_type not in self.VEHICLE_RATES:
            return False, "Invalid vehicle type"

        max_passengers = self.VEHICLE_RATES[self.vehicle_type]["max_passengers"]

        if self.passengers > max_passengers:
            return False, "Excessive passengers for selected vehicle"

        try:
            datetime.strptime(self.booking_time, "%H:%M")
        except ValueError:
            return False, "Invalid booking time"

        if not self.driver_available:
            return False, "No driver available"

        return True, "Valid booking"

    def calculate_base_fare(self):
        return self.VEHICLE_RATES[self.vehicle_type]["base"]

    def calculate_distance_fare(self):
        return self.distance * self.VEHICLE_RATES[self.vehicle_type]["per_km"]

    def calculate_peak_surcharge(self):
        hour = int(self.booking_time.split(":")[0])

        # Peak hours: 07:00–10:00 and 17:00–20:00
        if (7 <= hour < 10) or (17 <= hour < 20):
            return 0.20

        return 0.0

    def calculate_night_surcharge(self):
        hour = int(self.booking_time.split(":")[0])

        # Night: 22:00–06:00
        if hour >= 22 or hour < 6:
            return 0.15

        return 0.0

    def calculate_passenger_surcharge(self):
        # Additional charge for each passenger after the first
        return max(0, self.passengers - 1) * 20

    def calculate_fare(self):
        valid, message = self.validate_booking()

        if not valid:
            return {
                "status": "REJECTED",
                "message": message
            }

        base_fare = self.calculate_base_fare()
        distance_fare = self.calculate_distance_fare()

        subtotal = base_fare + distance_fare

        peak_rate = self.calculate_peak_surcharge()
        night_rate = self.calculate_night_surcharge()

        peak_surcharge = subtotal * peak_rate
        night_surcharge = subtotal * night_rate

        passenger_surcharge = self.calculate_passenger_surcharge()

        gross_fare = (
            subtotal
            + peak_surcharge
            + night_surcharge
            + passenger_surcharge
        )

        # Maximum promotional discount = 30%
        discount_rate = min(max(self.promo_discount, 0), 30) / 100
        promotional_discount = gross_fare * discount_rate

        final_fare = gross_fare - promotional_discount

        return {
            "status": "CONFIRMED",
            "customer_id": self.customer_id,
            "pickup": self.pickup,
            "drop": self.drop,
            "vehicle": self.vehicle_type,
            "distance": self.distance,
            "passengers": self.passengers,
            "base_fare": round(base_fare, 2),
            "distance_fare": round(distance_fare, 2),
            "peak_surcharge": round(peak_surcharge, 2),
            "night_surcharge": round(night_surcharge, 2),
            "passenger_surcharge": round(passenger_surcharge, 2),
            "promotional_discount": round(promotional_discount, 2),
            "final_fare": round(final_fare, 2)
        }

    def assign_driver(self):
        valid, message = self.validate_booking()

        if not valid:
            return None

        # Simulated driver allocation
        drivers = {
            "Bike": "DR-B001",
            "Sedan": "DR-S001",
            "SUV": "DR-S001",
            "Premium": "DR-P001"
        }

        return drivers.get(self.vehicle_type)


if __name__ == "__main__":

    booking = RideBooking(
        customer_id="C1001",
        pickup="VIT Vellore",
        drop="Katpadi",
        distance=8,
        passengers=2,
        vehicle_type="Sedan",
        booking_time="18:30",
        driver_available=True,
        promo_discount=10
    )

    result = booking.calculate_fare()

    for key, value in result.items():
        print(f"{key}: {value}")

    driver = booking.assign_driver()

    if driver:
        print("Assigned Driver:", driver)
