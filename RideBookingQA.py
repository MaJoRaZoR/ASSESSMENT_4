import unittest


class RideBooking:
    def __init__(self, vehicle_type="Car"):
        self.vehicle_type = vehicle_type
        self.driver_id = None

    def assign_driver(self):
        """
        Assign a driver based on vehicle type.
        """
        drivers = {
            "Bike": "DR-B001",
            "Car": "DR-C001",
            "Auto": "DR-A001"
        }

        self.driver_id = drivers.get(self.vehicle_type)
        return self.driver_id

    def calculate_fare(self, distance):
        """
        Calculate ride fare based on vehicle type and distance.
        """
        if distance <= 0:
            return 0

        rates = {
            "Bike": 10,
            "Auto": 15,
            "Car": 20
        }

        rate = rates.get(self.vehicle_type)

        if rate is None:
            return None

        return distance * rate

    def booking(self):
        """
        Return booking details.
        """
        driver = self.assign_driver()

        return {
            "vehicle_type": self.vehicle_type,
            "driver_id": driver
        }


class RideBookingQA(unittest.TestCase):

    # 1. Test Bike driver allocation
    def test_driver_allocation(self):
        booking = RideBooking(vehicle_type="Bike")

        self.assertEqual(
            booking.assign_driver(),
            "DR-B001"
        )

    # 2. Test Car driver allocation
    def test_car_driver_allocation(self):
        booking = RideBooking(vehicle_type="Car")

        self.assertEqual(
            booking.assign_driver(),
            "DR-C001"
        )

    # 3. Test Auto driver allocation
    def test_auto_driver_allocation(self):
        booking = RideBooking(vehicle_type="Auto")

        self.assertEqual(
            booking.assign_driver(),
            "DR-A001"
        )

    # 4. Test invalid vehicle
    def test_invalid_vehicle(self):
        booking = RideBooking(vehicle_type="Truck")

        self.assertIsNone(
            booking.assign_driver()
        )

    # 5. Test Bike fare
    def test_bike_fare(self):
        booking = RideBooking(vehicle_type="Bike")

        self.assertEqual(
            booking.calculate_fare(10),
            100
        )

    # 6. Test Car fare
    def test_car_fare(self):
        booking = RideBooking(vehicle_type="Car")

        self.assertEqual(
            booking.calculate_fare(10),
            200
        )

    # 7. Test Auto fare
    def test_auto_fare(self):
        booking = RideBooking(vehicle_type="Auto")

        self.assertEqual(
            booking.calculate_fare(10),
            150
        )

    # 8. Test zero distance
    def test_zero_distance(self):
        booking = RideBooking(vehicle_type="Car")

        self.assertEqual(
            booking.calculate_fare(0),
            0
        )

    # 9. Test negative distance
    def test_negative_distance(self):
        booking = RideBooking(vehicle_type="Car")

        self.assertEqual(
            booking.calculate_fare(-5),
            0
        )

    # 10. Test invalid vehicle fare
    def test_invalid_vehicle_fare(self):
        booking = RideBooking(vehicle_type="Truck")

        self.assertIsNone(
            booking.calculate_fare(10)
        )

    # 11. Test complete booking
    def test_complete_booking(self):
        booking = RideBooking(vehicle_type="Bike")

        result = booking.booking()

        self.assertEqual(
            result["vehicle_type"],
            "Bike"
        )

        self.assertEqual(
            result["driver_id"],
            "DR-B001"
        )


if __name__ == "__main__":
    unittest.main()
