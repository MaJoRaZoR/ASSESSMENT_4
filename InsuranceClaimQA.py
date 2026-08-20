import unittest
from InsuranceClaim import InsuranceClaim


class InsuranceClaimQA(unittest.TestCase):

    def claim(self, **kwargs):

        data = {
            "policy_no": "POL1001",
            "customer_id": "C001",
            "policy_type": "Health",
            "claim_amount": 100000,
            "start_date": "2025-01-01",
            "incident_date": "2025-06-10",
            "previous_claims": 1,
            "age": 35,
            "incident_type": "Hospitalization",
            "documents": True
        }

        data.update(kwargs)

        return InsuranceClaim(**data)

    # Valid claim
    def test_valid_claim(self):
        r = self.claim().process_claim()
        self.assertEqual(r["status"], "APPROVED")

    # Expired/invalid policy
    def test_expired_policy(self):
        r = self.claim(
            incident_date="2026-06-10",
            start_date="2025-01-01"
        ).process_claim()

        self.assertEqual(r["status"], "APPROVED")

    # Claim before policy start
    def test_before_start(self):
        r = self.claim(
            incident_date="2024-12-01"
        ).process_claim()

        self.assertEqual(r["status"], "REJECTED")

    # Excessive claim amount
    def test_excessive_amount(self):
        r = self.claim(
            claim_amount=600000
        ).process_claim()

        self.assertGreaterEqual(
            r["fraud_score"], 30
        )

    # Missing documents
    def test_missing_documents(self):
        r = self.claim(
            documents=False
        ).process_claim()

        self.assertEqual(
            r["status"], "MANUAL REVIEW"
        )

    # Multiple previous claims
    def test_multiple_claims(self):
        r = self.claim(
            previous_claims=5
        ).process_claim()

        self.assertGreaterEqual(
            r["fraud_score"], 30
        )

    # Fraud scenario
    def test_fraud(self):
        r = self.claim(
            claim_amount=600000,
            previous_claims=5,
            documents=False,
            incident_date="2025-01-05"
        ).process_claim()

        self.assertEqual(
            r["status"], "FRAUD SUSPECTED"
        )

    # Boundary claim amount
    def test_boundary_amount(self):
        r = self.claim(
            claim_amount=500000
        ).process_claim()

        self.assertEqual(
            r["maximum_payable"],
            500000
        )

    # Invalid policy number
    def test_invalid_policy(self):
        r = self.claim(
            policy_no="ABC1001"
        ).process_claim()

        self.assertEqual(
            r["status"], "REJECTED"
        )

    # Invalid incident date
    def test_invalid_date(self):
        r = self.claim(
            incident_date="invalid"
        ).process_claim()

        self.assertEqual(
            r["status"], "REJECTED"
        )


if __name__ == "__main__":
    unittest.main()
