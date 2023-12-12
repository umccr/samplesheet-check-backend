"""
Unit tests for samplesheet checker

run: python -m unittest samplesheet/tests/test_samplesheet_check.py

"""

import logging
import asyncio
import os

from unittest import TestCase, mock, main

from samplesheet.samplesheet_check import run_sample_sheet_check_with_metadata, run_sample_sheet_content_check
from utils.samplesheet import SampleSheet
from utils.errors import SampleNameFormatError
from utils.errors import GetMetaDataError, SampleSheetHeaderError, SimilarIndexError, \
    MetaDataError, OverrideCyclesError

dirname = os.path.dirname(__file__)
SAMPLE1_PATH = os.path.join(dirname, "./data/sample1.csv")
SAMPLE2_PATH = os.path.join(dirname, "./data/sample2.csv")


class TestSamplesheetCheckUnitTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logging.disable(logging.CRITICAL)
        print("\n---Running samplesheet check unit tests---")

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

    @mock.patch('samplesheet.samplesheet_check.get_years_from_samplesheet',
                mock.MagicMock(return_value={2019, 2020, 2021}))
    @mock.patch('samplesheet.samplesheet_check.check_samplesheet_header_metadata', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_sample_sheet_for_index_clashes', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.set_metadata_by_library_id', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_metadata_correspondence', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_global_override_cycles', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_internal_override_cycles', mock.MagicMock(return_value=""))
    def test_run_check_no_error(self):
        assert asyncio.run(run_sample_sheet_content_check("SampleSheetClass")) is None, "Expected with no error return"

    @mock.patch('samplesheet.samplesheet_check.get_years_from_samplesheet',
                mock.MagicMock(return_value={2019, 2020, 2021}))
    @mock.patch('samplesheet.samplesheet_check.check_samplesheet_header_metadata', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_sample_sheet_for_index_clashes',
                mock.MagicMock(side_effect=SimilarIndexError))
    @mock.patch('samplesheet.samplesheet_check.set_metadata_by_library_id', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_metadata_correspondence', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_global_override_cycles', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_internal_override_cycles', mock.MagicMock(return_value=""))
    def test_run_check_SimilarIndexError(self):
        assert asyncio.run(run_sample_sheet_content_check(
            "SampleSheetClass")) == "Found at least two indexes that were too similar to each other", "Expected error"

    @mock.patch('samplesheet.samplesheet_check.get_years_from_samplesheet',
                mock.MagicMock(return_value={2019, 2020, 2021}))
    @mock.patch('samplesheet.samplesheet_check.check_samplesheet_header_metadata',
                mock.MagicMock(side_effect=SampleSheetHeaderError))
    @mock.patch('samplesheet.samplesheet_check.check_sample_sheet_for_index_clashes', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.set_metadata_by_library_id', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_metadata_correspondence', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_global_override_cycles', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_internal_override_cycles', mock.MagicMock(return_value=""))
    def test_run_check_SampleSheetHeaderError(self):
        assert asyncio.run(run_sample_sheet_content_check(
            "SampleSheetClass")) == "Samplesheet header did not have the appropriate attributes", "Expected error"

    @mock.patch('samplesheet.samplesheet_check.get_years_from_samplesheet',
                mock.MagicMock(return_value={2019, 2020, 2021}))
    @mock.patch('samplesheet.samplesheet_check.check_samplesheet_header_metadata', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_sample_sheet_for_index_clashes', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.set_metadata_by_library_id',
                mock.MagicMock(side_effect=GetMetaDataError))
    @mock.patch('samplesheet.samplesheet_check.check_metadata_correspondence', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_global_override_cycles', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_internal_override_cycles', mock.MagicMock(return_value=""))
    def test_run_check_GetMetaDataError(self):
        assert run_sample_sheet_check_with_metadata("SampleSheetClass") == "Unable to get metadata", "Expected error"

    @mock.patch('samplesheet.samplesheet_check.get_years_from_samplesheet',
                mock.MagicMock(return_value={2019, 2020, 2021}))
    @mock.patch('samplesheet.samplesheet_check.check_samplesheet_header_metadata', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_sample_sheet_for_index_clashes', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.set_metadata_by_library_id', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_metadata_correspondence',
                mock.MagicMock(side_effect=MetaDataError))
    @mock.patch('samplesheet.samplesheet_check.check_global_override_cycles', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_internal_override_cycles', mock.MagicMock(return_value=""))
    def test_run_check_MetaDataError(self):
        assert run_sample_sheet_check_with_metadata(
            "SampleSheetClass") == "Metadata could not be extracted", "Expected error"

    @mock.patch('samplesheet.samplesheet_check.get_years_from_samplesheet',
                mock.MagicMock(return_value={2019, 2020, 2021}))
    @mock.patch('samplesheet.samplesheet_check.check_samplesheet_header_metadata', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_sample_sheet_for_index_clashes', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.set_metadata_by_library_id', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_metadata_correspondence', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_global_override_cycles',
                mock.MagicMock(side_effect=OverrideCyclesError))
    @mock.patch('samplesheet.samplesheet_check.check_internal_override_cycles', mock.MagicMock(return_value=""))
    def test_run_check_globalOverrideCyclesError(self):
        assert run_sample_sheet_check_with_metadata(
            "SampleSheetClass") == "Override cycles check failed", "Expected error"

    @mock.patch('samplesheet.samplesheet_check.get_years_from_samplesheet',
                mock.MagicMock(return_value={2019, 2020, 2021}))
    @mock.patch('samplesheet.samplesheet_check.check_samplesheet_header_metadata', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_sample_sheet_for_index_clashes', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.set_metadata_by_library_id', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_metadata_correspondence', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_global_override_cycles', mock.MagicMock(return_value=""))
    @mock.patch('samplesheet.samplesheet_check.check_internal_override_cycles',
                mock.MagicMock(side_effect=OverrideCyclesError))
    def test_run_check_internalOverrideCyclesError(self):
        assert run_sample_sheet_check_with_metadata(
            "SampleSheetClass") == "Override cycles check failed", "Expected error"


if __name__ == '__main__':
    main()
