import json
import os
import tempfile
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

import app as cloudsentinel


class CloudSentinelTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = cloudsentinel.EventStore(str(Path(self.temp_dir.name) / "events.sqlite3"))
        self.original_store = cloudsentinel.STORE
        cloudsentinel.STORE = self.store

    def tearDown(self):
        cloudsentinel.STORE = self.original_store
        self.temp_dir.cleanup()

    def test_health_payload_is_small_and_machine_readable(self):
        payload = cloudsentinel.payload()
        self.assertEqual(payload["service"], "CloudSentinel")
        self.assertEqual(payload["status"], "operational")
        self.assertIn("instance_id", payload)

    def test_readiness_payload_reports_ready(self):
        readiness = cloudsentinel.ready_payload()
        self.assertEqual(readiness["status"], "ready")
        self.assertEqual(readiness["service"], "CloudSentinel")

    def test_events_are_persistent_in_the_store(self):
        event = self.store.record("heartbeat", "test event")
        events = self.store.recent()
        self.assertEqual(events[0]["id"], event["id"])
        self.assertEqual(events[0]["event_type"], "heartbeat")
        self.assertEqual(events[0]["message"], "test event")

    def test_api_status_serializes_to_json(self):
        encoded = json.dumps(cloudsentinel.payload()).encode("utf-8")
        decoded = json.loads(encoded)
        self.assertEqual(decoded["service"], "CloudSentinel")


if __name__ == "__main__":
    unittest.main()
