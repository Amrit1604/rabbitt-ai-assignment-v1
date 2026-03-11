"""
Stress test for the Sales Insight Automator API.

Uses Locust to simulate concurrent users hammering the endpoints.
The LLM and email are real here — if you want to avoid charges,
point this at a staging environment and mock those services externally.

Run locally (server must already be running on localhost:8000):

    locust -f locustfile.py --host http://localhost:8000

Then open http://localhost:8089 and set:
  - Number of users: 20
  - Spawn rate: 5 per second

Or run headless (no browser UI):

    locust -f locustfile.py --host http://localhost:8000 \\
           --headless -u 20 -r 5 --run-time 60s --html report.html
"""

import os

from locust import HttpUser, between, task

# We use a real (tiny) CSV so the parser doesn't bail early.
# In a proper staging setup, mock the LLM + email to avoid costs.
SAMPLE_CSV = b"""Date,Product_Category,Region,Units_Sold,Unit_Price,Revenue,Status
2026-01-05,Electronics,North,150,1200,180000,Shipped
2026-01-12,Home Appliances,South,45,450,20250,Shipped
2026-01-20,Electronics,East,80,1100,88000,Delivered
"""

# Use a real email only if you want actual emails during stress testing
TEST_EMAIL = os.getenv("STRESS_TEST_EMAIL", "loadtest@example.com")


class SalesAnalystUser(HttpUser):
    """
    Simulates a sales team member using the tool during a busy day.
    Mix of reads (health checks) and writes (file uploads) — realistic ratio.
    """

    # Wait 1–3 seconds between tasks, like a real human clicking around
    wait_time = between(1, 3)

    @task(1)
    def check_health(self):
        """Quick ping to make sure the server is alive."""
        with self.client.get("/health", catch_response=True) as resp:
            if resp.json().get("status") != "ok":
                resp.failure("Health check returned unexpected status")

    @task(3)
    def upload_csv_file(self):
        """
        The main user action: upload a CSV and trigger the AI pipeline.
        Weight 3 = happens 3x more often than the health check.
        """
        with self.client.post(
            "/api/analyze",
            files={"file": ("sales_q1_2026.csv", SAMPLE_CSV, "text/plain")},
            data={"email": TEST_EMAIL},
            catch_response=True,
            name="/api/analyze [CSV upload]",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 429:
                # Rate limiting is expected under load — not a failure
                resp.success()
            elif resp.status_code in (502, 503):
                resp.failure(f"Backend error: {resp.text[:200]}")
            else:
                resp.failure(f"Unexpected status {resp.status_code}: {resp.text[:200]}")

    @task(1)
    def check_swagger_docs(self):
        """Devs checking the docs during a sprint — occasional traffic."""
        self.client.get("/docs", name="/docs [swagger]")

    @task(2)
    def upload_bad_file(self):
        """
        Simulates a user uploading a wrong file type.
        Should always get a 422, never a 500.
        Weight 2 — this happens fairly often in real usage.
        """
        with self.client.post(
            "/api/analyze",
            files={"file": ("report.pdf", b"%PDF-1.4 fake content", "application/pdf")},
            data={"email": TEST_EMAIL},
            catch_response=True,
            name="/api/analyze [invalid file]",
        ) as resp:
            if resp.status_code == 422:
                resp.success()
            else:
                resp.failure(f"Expected 422 for bad file, got {resp.status_code}")


class SpikeTester(HttpUser):
    """
    A second user class that fires requests as fast as possible
    to test how the rate limiter holds up under a burst.

    Activate by running:
        locust -f locustfile.py --host http://localhost:8000 \\
               --headless -u 5 -r 5 --run-time 30s
    """

    wait_time = between(0.1, 0.5)  # almost no delay — pure spike

    @task
    def rapid_fire_upload(self):
        with self.client.post(
            "/api/analyze",
            files={"file": ("sales.csv", SAMPLE_CSV, "text/plain")},
            data={"email": TEST_EMAIL},
            catch_response=True,
            name="/api/analyze [rate limit spike]",
        ) as resp:
            # Under a spike we expect either 200 (processed) or 429 (rate limited)
            if resp.status_code in (200, 429):
                resp.success()
            else:
                resp.failure(f"Unexpected response during spike: {resp.status_code}")
