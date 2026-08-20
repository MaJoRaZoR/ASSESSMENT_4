import unittest
from RideBooking import RideBooking


class RideBookingQA(unittest.TestCase):

    def booking(self, **kwargs):
        data = {
            "customer_id": "T001",
            "pickup": "VIT",
            "drop": "Katpadi",
            "distance": 10,
            "passengers": 2,
            "vehicle_type": "Sedan",
            "booking_time": "14:00",
            "driver_available": True,
            "promo_discount": 0
        }
        data.update(kwargs)
        return RideBooking(**data)

    # Normal booking
    def test_normal(self):
        r = self.booking().calculate_fare()
        self.assertEqual(r["status"], "CONFIRMED")

    # Peak hour
    def test_peak(self):
        r = self.booking(booking_time="18:00").calculate_fare()
        self.assertGreater(r["peak_surcharge"], 0)

    # Night
    def test_night(self):
        r = self.booking(booking_time="23:00").calculate_fare()
        self.assertGreater(r["night_surcharge"], 0)

    # Invalid distance
    def test_distance(self):
        r = self.booking(distance=0).calculate_fare()
        self.assertEqual(r["status"], "REJECTED")

    # Invalid passengers
    def test_passengers(self):
        r = self.booking(passengers=0).calculate_fare()
        self.assertEqual(r["status"], "REJECTED")

    # Excessive passengers
    def test_excessive_passengers(self):
        r = self.booking(passengers=5).calculate_fare()
        self.assertEqual(r["status"], "REJECTED")

    # Driver unavailable
    def test_driver(self):
        r = self.booking(driver_available=False).calculate_fare()
        self.assertEqual(r["status"], "REJECTED")

    # Maximum discount
    def test_discount(self):
        r = self.booking(promo_discount=30).calculate_fare()
        self.assertGreater(r["promotional_discount"], 0)

    # Vehicle types
    def test_vehicles(self):
        for v in ["Bike", "Sedan", "SUV", "Premium"]:
            p = 1
            r = self.booking(
                vehicle_type=v,
                passengers=p
            ).calculate_fare()
            self.assertEqual(r["status"], "CONFIRMED")

    # Boundary fare
    def test_boundary_fare(self):
        r = self.booking(
            distance=1,
            passengers=1,
            vehicle_type="Bike"
        ).calculate_fare()

        self.assertEqual(r["final_fare"], 48)

    # Driver allocation
    def test_driver_allocation(self):
        self.assertEqual(
            self.booking(vehicle_type="Bike").assign_driver(),
            "DR-B001"
        )

        self.assertEqual(
            self.booking(vehicle_type="Sedan").assign_driver(),
            "DR-S001"
        )

        self.assertEqual(
            self.booking(vehicle_type="Premium").assign_driver(),
            "DR-P001"
        )


if __name__ == "__main__":
    unittest.main()
