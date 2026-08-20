import unittest
from ICUAllocation import ICUAllocation


class ICUAllocationQA(unittest.TestCase):

    def setUp(self):
        ICUAllocation.patients.clear()
        ICUAllocation.waiting_list.clear()
        ICUAllocation.beds = 2

    def patient(self, **kwargs):
        data = {
            "patient_id": "P001",
            "age": 40,
            "oxygen": 98,
            "heart_rate": 80,
            "blood_pressure": 120,
            "temperature": 37,
            "conditions": []
        }
        data.update(kwargs)
        return ICUAllocation(**data)

    # Critical patient
    def test_critical(self):
        p = self.patient(oxygen=85, heart_rate=130)
        self.assertEqual(p.classification(), "CRITICAL")

    # Normal patient
    def test_normal(self):
        p = self.patient()
        self.assertEqual(p.classification(), "LOW")

    # Emergency case
    def test_emergency(self):
        p = self.patient(emergency=True)
        self.assertEqual(p.classification(), "CRITICAL")

    # No ICU beds
    def test_no_bed(self):
        ICUAllocation.beds = 0
        r = self.patient().allocate()
        self.assertEqual(r["status"], "WAITING")

    # Duplicate patient
    def test_duplicate(self):
        self.patient().allocate()
        r = self.patient().allocate()
        self.assertEqual(r["status"], "REJECTED")

    # Invalid oxygen
    def test_invalid_oxygen(self):
        r = self.patient(oxygen=110).allocate()
        self.assertEqual(r["status"], "REJECTED")

    # Invalid heart rate
    def test_invalid_heart_rate(self):
        r = self.patient(heart_rate=250).allocate()
        self.assertEqual(r["status"], "REJECTED")

    # Priority boundary
    def test_priority_boundary(self):
        p = self.patient(oxygen=94)
        self.assertEqual(p.priority_score(), 20)
        self.assertEqual(p.classification(), "MEDIUM")

    # Multiple patients competing for beds
    def test_multiple_patients(self):
        p1 = self.patient(patient_id="P1", oxygen=80)
        p2 = self.patient(patient_id="P2", oxygen=85)
        p3 = self.patient(patient_id="P3", oxygen=98)

        self.assertEqual(p1.allocate()["status"], "ALLOCATED")
        self.assertEqual(p2.allocate()["status"], "ALLOCATED")
        self.assertEqual(p3.allocate()["status"], "WAITING")


if __name__ == "__main__":
    unittest.main()
