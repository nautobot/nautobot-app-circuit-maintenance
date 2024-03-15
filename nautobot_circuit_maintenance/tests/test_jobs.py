"""Tests for Overlap Jobs being included."""

# pylint: disable=missing-class-docstring,no-name-in-module
from datetime import datetime
from typing import NamedTuple

from django.test import TestCase

from nautobot_circuit_maintenance.jobs.site_search import check_for_overlap

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class MockCircuitMaintenance(NamedTuple):
    start_time: datetime
    end_time: datetime


class TestOverlap(TestCase):
    def test_check_for_overlap_false(self):
        record1 = MockCircuitMaintenance(
            start_time=datetime.strptime("2020-10-04 10:00:00", DATE_FORMAT),
            end_time=datetime.strptime("2020-10-04 12:00:00", DATE_FORMAT),
        )
        record2 = MockCircuitMaintenance(
            start_time=datetime.strptime("2020-10-05 10:00:00", DATE_FORMAT),
            end_time=datetime.strptime("2020-10-05 12:00:00", DATE_FORMAT),
        )

        result = check_for_overlap(record1, record2)
        self.assertFalse(result)

    def test_check_for_overlap_true(self):
        record1 = MockCircuitMaintenance(
            start_time=datetime.strptime("2020-10-04 10:00:00", DATE_FORMAT),
            end_time=datetime.strptime("2020-10-04 12:00:00", DATE_FORMAT),
        )
        record2 = MockCircuitMaintenance(
            start_time=datetime.strptime("2020-10-04 11:00:00", DATE_FORMAT),
            end_time=datetime.strptime("2020-10-05 12:00:00", DATE_FORMAT),
        )

        result = check_for_overlap(record1, record2)
        self.assertTrue(result)

    def test_check_for_overlap_same_day_true(self):
        record1 = MockCircuitMaintenance(
            start_time=datetime.strptime("2020-10-04 10:00:00", DATE_FORMAT),
            end_time=datetime.strptime("2020-10-04 12:00:00", DATE_FORMAT),
        )
        record2 = MockCircuitMaintenance(
            start_time=datetime.strptime("2020-10-04 11:00:00", DATE_FORMAT),
            end_time=datetime.strptime("2020-10-04 11:30:00", DATE_FORMAT),
        )

        result = check_for_overlap(record1, record2)
        self.assertTrue(result)

    def test_check_for_overlap_same_day_false(self):
        record1 = MockCircuitMaintenance(
            start_time=datetime.strptime("2020-10-04 10:00:00", DATE_FORMAT),
            end_time=datetime.strptime("2020-10-04 12:00:00", DATE_FORMAT),
        )
        record2 = MockCircuitMaintenance(
            start_time=datetime.strptime("2020-10-04 09:00:00", DATE_FORMAT),
            end_time=datetime.strptime("2020-10-04 09:30:00", DATE_FORMAT),
        )

        result = check_for_overlap(record1, record2)
        self.assertFalse(result)
