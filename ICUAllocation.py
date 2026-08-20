class ICUAllocation:

    patients = set()
    waiting_list = []
    beds = 2

    def __init__(self, patient_id, age, oxygen, heart_rate,
                 blood_pressure, temperature, conditions,
                 emergency=False):

        self.patient_id = patient_id
        self.age = age
        self.oxygen = oxygen
        self.heart_rate = heart_rate
        self.blood_pressure = blood_pressure
        self.temperature = temperature
        self.conditions = conditions
        self.emergency = emergency

    def validate(self):
        if self.patient_id in ICUAllocation.patients:
            return False, "Duplicate patient ID"

        if not 0 <= self.oxygen <= 100:
            return False, "Invalid oxygen level"

        if not 30 <= self.heart_rate <= 220:
            return False, "Invalid heart rate"

        if self.age < 0:
            return False, "Invalid age"

        return True, "Valid"

    def priority_score(self):
        score = 0

        if self.oxygen < 90:
            score += 40
        elif self.oxygen < 95:
            score += 20

        if self.heart_rate < 50 or self.heart_rate > 120:
            score += 25

        if self.blood_pressure < 90 or self.blood_pressure > 140:
            score += 20

        if self.temperature >= 39 or self.temperature < 35:
            score += 15

        if self.conditions:
            score += 10

        if self.age >= 65:
            score += 5

        return score

    def classification(self):
        if self.emergency:
            return "CRITICAL"

        score = self.priority_score()

        if score >= 60:
            return "CRITICAL"
        elif score >= 40:
            return "HIGH"
        elif score >= 20:
            return "MEDIUM"
        else:
            return "LOW"

    def allocate(self):
        valid, message = self.validate()

        if not valid:
            return {"status": "REJECTED", "message": message}

        ICUAllocation.patients.add(self.patient_id)

        priority = self.classification()

        if ICUAllocation.beds > 0:
            ICUAllocation.beds -= 1

            return {
                "status": "ALLOCATED",
                "patient": self.patient_id,
                "priority": priority,
                "score": self.priority_score()
            }

        ICUAllocation.waiting_list.append(self.patient_id)

        return {
            "status": "WAITING",
            "patient": self.patient_id,
            "priority": priority,
            "score": self.priority_score()
        }


if __name__ == "__main__":

    patient = ICUAllocation(
        "P001",
        70,
        85,
        130,
        80,
        39.5,
        ["Diabetes"]
    )

    print(patient.allocate())
