from datetime import datetime


class InsuranceClaim:

    COVERAGE = {
        "Health": 500000,
        "Life": 1000000,
        "Vehicle": 300000,
        "Travel": 200000
    }

    def __init__(self, policy_no, customer_id, policy_type,
                 claim_amount, start_date, incident_date,
                 previous_claims, age, incident_type, documents):

        self.policy_no = policy_no
        self.customer_id = customer_id
        self.policy_type = policy_type
        self.claim_amount = claim_amount
        self.start_date = start_date
        self.incident_date = incident_date
        self.previous_claims = previous_claims
        self.age = age
        self.incident_type = incident_type
        self.documents = documents

    def validate(self):
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            incident = datetime.strptime(self.incident_date, "%Y-%m-%d")
        except ValueError:
            return False, "Invalid incident date"

        if not self.policy_no.startswith("POL"):
            return False, "Invalid policy number"

        if incident < start:
            return False, "Claim before policy start"

        return True, "Valid"

    def fraud_score(self):

        score = 0

        if self.previous_claims >= 3:
            score += 30

        if self.claim_amount > self.COVERAGE.get(
                self.policy_type, 0):
            score += 30

        start = datetime.strptime(
            self.start_date, "%Y-%m-%d"
        )
        incident = datetime.strptime(
            self.incident_date, "%Y-%m-%d"
        )

        if (incident - start).days <= 7:
            score += 20

        if not self.documents:
            score += 20

        return score

    def process_claim(self):

        valid, message = self.validate()

        if not valid:
            return {
                "status": "REJECTED",
                "message": message
            }

        coverage = self.COVERAGE.get(
            self.policy_type, 0
        )

        deductible = min(
            self.claim_amount * 0.10,
            50000
        )

        payable = min(
            self.claim_amount,
            coverage
        )

        contribution = deductible
        payout = max(0, payable - contribution)

        fraud = self.fraud_score()

        if fraud >= 60:
            status = "FRAUD SUSPECTED"
        elif fraud >= 30 or not self.documents:
            status = "MANUAL REVIEW"
        else:
            status = "APPROVED"

        return {
            "status": status,
            "eligibility": True,
            "maximum_payable": coverage,
            "deductible": round(deductible, 2),
            "customer_contribution": round(
                contribution, 2
            ),
            "insurance_payout": round(
                payout, 2
            ),
            "fraud_score": fraud
        }


if __name__ == "__main__":

    claim = InsuranceClaim(
        "POL1001",
        "C001",
        "Health",
        100000,
        "2025-01-01",
        "2025-06-10",
        1,
        35,
        "Hospitalization",
        True
    )

    print(claim.process_claim())
