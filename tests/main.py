"""
To run the testcase

From the main directory, run this python test command:
cmd:  python -m unittest tests.main.SampleSheetTestCase

"""
import asyncio

from unittest import TestCase

# Imports
from lambdas.functions.samplesheet_check import run_sample_sheet_content_check
from umccr_utils.samplesheet import SampleSheet
from umccr_utils.errors import SampleNameFormatError

SAMPLE1_PATH = "tests/data/sample1.csv"
SAMPLE2_PATH = "tests/data/sample2.csv"


class SampleSheetTestCase(TestCase):

    def test_fail_sample_name_check(self):
        with self.assertRaises(SampleNameFormatError):
            SampleSheet(SAMPLE1_PATH)

    def test_success_sample_format(self):
        sample_sheet = SampleSheet(SAMPLE2_PATH)

        loop = asyncio.new_event_loop()
        error = loop.run_until_complete(
            run_sample_sheet_content_check(sample_sheet)
        )
        loop.close()
