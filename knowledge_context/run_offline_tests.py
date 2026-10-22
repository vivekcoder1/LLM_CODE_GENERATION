"""Run the focused offline suite and save auditable per-test outcomes.

No live clients are created: the suite uses injected/mocked database and LLM
adapters. Use --output-dir for a NEW folder; existing folders are never reused.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
import csv
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def startTest(self, test):
        self.started = time.perf_counter()
        self.current = {"name": test.id(), "status": "passed", "tests": 1,
                        "failures": 0, "errors": 0, "skipped": 0, "details": ""}
        super().startTest(test)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.current.update(status="failed", failures=1, details=self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self.current.update(status="error", errors=1, details=self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.current.update(status="skipped", skipped=1, details=reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.current.update(status="expected_failure", details=self._exc_info_to_string(err, test))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.current.update(status="unexpected_success", failures=1)

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            is_failure = issubclass(err[0], test.failureException)
            key = "failures" if is_failure else "errors"
            self.current[key] += 1
            self.current["status"] = "failed" if is_failure else "error"
            self.current["details"] += str(subtest) + "\n" + self._exc_info_to_string(err, test)

    def stopTest(self, test):
        self.current["duration_s"] = round(time.perf_counter() - self.started, 6)
        self.records.append(self.current)
        super().stopTest(test)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    output = args.output_dir or ROOT / "integration_runs" / ("validation_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ"))
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(ROOT))
    started = time.perf_counter()
    with (output / "unittest.log").open("w", encoding="utf-8") as log, redirect_stdout(log), redirect_stderr(log):
        suite = unittest.defaultTestLoader.discover(str(ROOT / "knowledge_context"), pattern="test_*.py")
        result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=RecordedResult).run(suite)
    (output / "test_outcomes.json").write_text(json.dumps(result.records, indent=2) + "\n", encoding="utf-8")
    with (output / "test_outcomes.csv").open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "status", "tests", "failures", "errors", "skipped", "duration_s", "details"])
        writer.writeheader()
        writer.writerows(result.records)
    summary = {"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
               "skipped": len(result.skipped), "expected_failures": len(result.expectedFailures),
               "unexpected_successes": len(result.unexpectedSuccesses), "successful": result.wasSuccessful(),
               "duration_s": round(time.perf_counter() - started, 3), "scope": "focused_offline_knowledge_context_suite",
               "created_utc": datetime.now(timezone.utc).isoformat()}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    print(f"Test results: {output / 'test_outcomes.json'}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
