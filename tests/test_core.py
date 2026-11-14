import unittest

from email_assistant.core import triage_email


class TriageTests(unittest.TestCase):
    def test_job_is_flagged_for_review(self):
        result = triage_email({
            "subject": "Job opening: Python developer",
            "body": "Apply at https://example.org/jobs",
        })
        self.assertEqual(result.category, "job")
        self.assertEqual(result.labels, ["Lowongan/Review"])
        self.assertIsNotNone(result.job_analysis)
        self.assertFalse(result.cleanup_candidate)

    def test_subscription_only_suggests_review(self):
        result = triage_email({"subject": "Newsletter", "body": "Unsubscribe"})
        self.assertEqual(result.category, "subscription_review")
        self.assertTrue(result.cleanup_candidate)

    def test_job_is_never_cleanup_candidate(self):
        result = triage_email({"subject": "Career opportunity", "body": "Unsubscribe"})
        self.assertEqual(result.category, "job")
        self.assertFalse(result.cleanup_candidate)

    def test_spam_is_review_only(self):
        result = triage_email({"subject": "Claim your prize", "body": ""})
        self.assertEqual(result.category, "spam_review")


if __name__ == "__main__":
    unittest.main()
