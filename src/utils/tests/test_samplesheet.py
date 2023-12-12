import os
import logging
from unittest import TestCase, mock, main
from utils.samplesheet import SampleSheet, get_years_from_samplesheet, set_metadata_by_library_id, \
    check_samplesheet_header_metadata, check_sample_sheet_for_index_clashes
from utils.errors import GetMetaDataError, LibraryNotFoundError, MultipleLibraryError, ApiCallError


class SamplesheetUnitTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logging.disable(logging.CRITICAL)
        print("\n---Running utils samplesheet unit tests---")

    def setUp(self):
        # Mock sample value
        self.sample_sheet = SampleSheet(os.path.dirname(
            os.path.abspath(__file__)) + "/sample")

    def test_get_years_from_samplesheet(self):
        func_result = get_years_from_samplesheet(self.sample_sheet)
        assert func_result == set(({'2000'})), "Object year of 2000 is expected"

    @mock.patch("utils.samplesheet.Sample.set_metadata_row_for_sample", mock.MagicMock(return_value=""))
    @mock.patch("utils.samplesheet.Sample.set_override_cycles",
                mock.MagicMock(result_value="set_override_cycles function executed"))
    def test_no_error_set_metadata_by_library_id(self):
        result_func = set_metadata_by_library_id(samplesheet=self.sample_sheet)
        assert result_func is None, "No Error is expected"

    @mock.patch("utils.samplesheet.Sample.set_metadata_row_for_sample",
                mock.MagicMock(side_effect=LibraryNotFoundError))
    @mock.patch("utils.samplesheet.Sample.set_override_cycles",
                mock.MagicMock(result_value="set_override_cycles function executed"))
    def test_LibraryNotFoundError_set_metadata_by_library_id(self):
        with self.assertRaises(GetMetaDataError):
            set_metadata_by_library_id(samplesheet=self.sample_sheet)

    @mock.patch("utils.samplesheet.Sample.set_metadata_row_for_sample",
                mock.MagicMock(side_effect=MultipleLibraryError))
    @mock.patch("utils.samplesheet.Sample.set_override_cycles", mock.MagicMock(result_value="set_override_cycles "
                                                                                            "function executed"))
    def test_MultipleLibraryError_set_metadata_by_library_id(self):
        with self.assertRaises(GetMetaDataError):
            set_metadata_by_library_id(samplesheet=self.sample_sheet)

    @mock.patch("utils.samplesheet.Sample.set_metadata_row_for_sample", mock.MagicMock(side_effect=ApiCallError))
    @mock.patch("utils.samplesheet.Sample.set_override_cycles", mock.MagicMock(result_value="set_override_cycles "
                                                                                            "function executed"))
    def test_ApiCallError_set_metadata_by_library_id(self):
        with self.assertRaises(GetMetaDataError):
            set_metadata_by_library_id(samplesheet=self.sample_sheet)

    def test_check_samplesheet_header_metadata(self):
        result_func = check_samplesheet_header_metadata(self.sample_sheet)
        assert result_func is None, "No error in the expected Sample"

    @mock.patch("utils.samplesheet.compare_two_indexes", mock.MagicMock(return_value=""))
    def test_pass_check_sample_sheet_for_index_clashes(self):
        # No Error for expected
        result_func = check_sample_sheet_for_index_clashes(self.sample_sheet)
        assert result_func is None, "No Error is executed"


if __name__ == '__main__':
    main()
