import json
import tempfile
import unittest
from pathlib import Path

from src.pulselake.generator import generate

class GeneratorTests(unittest.TestCase):
    def test_generates_requested_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            generate(250, 42, path)
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(len(rows), 250)

    def test_is_deterministic_for_same_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.jsonl"
            b = Path(tmp) / "b.jsonl"
            generate(100, 123, a)
            generate(100, 123, b)
            self.assertEqual(a.read_text(), b.read_text())

    def test_required_envelope_fields_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            generate(20, 42, path)
            event = json.loads(path.read_text().splitlines()[0])
            required = {
                "event_id",
                "event_type",
                "event_version",
                "event_time",
                "producer",
                "session_id",
                "country",
                "channel",
                "payload",
            }
            self.assertTrue(required.issubset(event))

if __name__ == "__main__":
    unittest.main()
