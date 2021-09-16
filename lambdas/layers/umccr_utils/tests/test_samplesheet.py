# Add umccr_util directory to python path
import sys
import os

sys.path.append(os.path.join(sys.path[0], '..'))
sys.path.append(os.path.join(sys.path[0], '..', '..'))

from samplesheet import Sample, SampleSheet, get_years_from_samplesheet, set_meta_data_by_library_id, \
                        check_samplesheet_header_metadata, check_metadata_correspondence, check_sample_sheet_for_index_clashes
from umccr_utils.errors import GetMetaDataError, LibraryNotFoundError, MultipleLibraryError, ApiCallError, \
                                SampleSheetHeaderError, SimilarIndexError

from unittest import TestCase, mock, main

class SamplesheetUnitTestCase(TestCase):
    def setUp(self):
        # Mock sample value
        self.sample_sheet = SampleSheet(os.path.dirname(
            os.path.abspath(__file__)) + "/sample-1")

    def test_get_years_from_samplesheet(self):

        func_result = get_years_from_samplesheet(self.sample_sheet)
        assert func_result == set(({'2021'})), "Object year of 2021 is expected"

    @mock.patch("samplesheet.Sample.set_metadata_row_for_sample", mock.MagicMock(result_value=None))
    @mock.patch("samplesheet.Sample.set_override_cycles",  mock.MagicMock(result_value="set_override_cycles function executed"))
    def test_no_error_set_meta_data_by_library_id(self):
        result_func = set_meta_data_by_library_id(samplesheet=self.sample_sheet,auth_header="JWT-TOKEN")
        assert result_func== None, "No Error is expected"
        
    ## Mock for LibraryNotFoundError
    @mock.patch("samplesheet.Sample.set_metadata_row_for_sample", mock.MagicMock(side_effect=LibraryNotFoundError))
    @mock.patch("samplesheet.Sample.set_override_cycles",  mock.MagicMock(result_value="set_override_cycles function executed"))
    def test_LibraryNotFoundError_set_meta_data_by_library_id(self):
        with self.assertRaises(GetMetaDataError):
            set_meta_data_by_library_id(samplesheet=self.sample_sheet,auth_header="JWT-TOKEN")

    ## Mock for MultipleLibraryError
    @mock.patch("samplesheet.Sample.set_metadata_row_for_sample", mock.MagicMock(side_effect=MultipleLibraryError))
    @mock.patch("samplesheet.Sample.set_override_cycles",  mock.MagicMock(result_value="set_override_cycles function executed"))
    def test_MultipleLibraryError_set_meta_data_by_library_id(self):
        with self.assertRaises(GetMetaDataError):
            set_meta_data_by_library_id(samplesheet=self.sample_sheet,auth_header="JWT-TOKEN")

    ## Mock for ApiCallError
    @mock.patch("samplesheet.Sample.set_metadata_row_for_sample", mock.MagicMock(side_effect=ApiCallError))
    @mock.patch("samplesheet.Sample.set_override_cycles",  mock.MagicMock(result_value="set_override_cycles function executed"))
    def test_ApiCallError_set_meta_data_by_library_id(self):
        with self.assertRaises(GetMetaDataError):
            set_meta_data_by_library_id(samplesheet=self.sample_sheet,auth_header="JWT-TOKEN")

    # No error expected
    def test_check_samplesheet_header_metadata(self):
        result_func = check_samplesheet_header_metadata(self.sample_sheet)
        assert result_func == None, "No error in the expected Sample"

    # No error expected
    @mock.patch("samplesheet.compare_two_indexes", mock.MagicMock(return_value=""))
    def test_pass_check_sample_sheet_for_index_clashes(self):
        # No Error for expected
        result_func = check_sample_sheet_for_index_clashes(self.sample_sheet)
        assert result_func == None, "No Error is executed"

    # SimilarIndexError expected
    @mock.patch("samplesheet.compare_two_indexes", mock.MagicMock(side_effect=SimilarIndexError))
    def test_pass_check_sample_sheet_for_index_clashes(self):
        with self.assertRaises(SimilarIndexError):
            check_sample_sheet_for_index_clashes(self.sample_sheet)


if __name__ == '__main__':
    main()