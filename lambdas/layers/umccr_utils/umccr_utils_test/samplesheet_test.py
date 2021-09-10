# Add umccr_util directory to python path
import sys
import os

sys.path.append(os.path.join(sys.path[0], '..'))
sys.path.append(os.path.join(sys.path[0], '..', '..'))

from samplesheet import Sample, SampleSheet, get_years_from_samplesheet, set_meta_data_by_library_id, \
                        check_samplesheet_header_metadata, check_metadata_correspondence, check_sample_sheet_for_index_clashes
from umccr_utils.errors import GetMetaDataError, LibraryNotFoundError, MultipleLibraryError, ApiCallError, \
                                SampleSheetHeaderError, SimilarIndexError

import pytest

def test_get_years_from_samplesheet():

    # Mock sample value
    sample_sheet = SampleSheet(os.path.dirname(
        os.path.abspath(__file__)) + "/sample-1")

    # Run function
    func_result = get_years_from_samplesheet(sample_sheet)

    assert func_result == set(({'2021'})), "Object year of 2021 is expected"

def test_set_meta_data_by_library_id(mocker):

    # Mock sample value
    sample_sheet = SampleSheet(os.path.dirname(
        os.path.abspath(__file__)) + "/sample-1")

    ## Mock for valid Input
    mocker.patch.object(Sample, 'set_metadata_row_for_sample', result_value=None )
    mocker.patch.object(Sample, 'set_override_cycles', result_value="set_override_cycles function executed" )

    result_func = set_meta_data_by_library_id(samplesheet=sample_sheet,auth_header="JWT-TOKEN")
    assert result_func== None, "No Error is expected"
    
    ## Mock for LibraryNotFoundError
    mocker.patch.object(Sample, 'set_metadata_row_for_sample', side_effect=LibraryNotFoundError)
    mocker.patch.object(Sample, 'set_override_cycles', result_value="set_override_cycles function executed" )

    with pytest.raises(GetMetaDataError) as info:
        set_meta_data_by_library_id(samplesheet=sample_sheet,auth_header="JWT-TOKEN")

    ## Mock for MultipleLibraryError
    mocker.patch.object(Sample, 'set_metadata_row_for_sample', side_effect=MultipleLibraryError )
    mocker.patch.object(Sample, 'set_override_cycles', result_value="set_override_cycles function executed" )

    with pytest.raises(GetMetaDataError) as info:
        set_meta_data_by_library_id(samplesheet=sample_sheet,auth_header="JWT-TOKEN")

    ## Mock for ApiCallError
    mocker.patch.object(Sample, 'set_metadata_row_for_sample', side_effect=ApiCallError )
    mocker.patch.object(Sample, 'set_override_cycles', result_value="set_override_cycles function executed" )

    with pytest.raises(GetMetaDataError) as info:
        set_meta_data_by_library_id(samplesheet=sample_sheet,auth_header="JWT-TOKEN")


def test_check_samplesheet_header_metadata(mocker):
    # Mock sample value
    sample_sheet = SampleSheet(os.path.dirname(
        os.path.abspath(__file__)) + "/sample-1")

    result_func = check_samplesheet_header_metadata(sample_sheet)

    assert result_func == None, "No error in the expected Sample"

# def test_check_metadata_correspondence(mocker):
#     # Mock sample value
#     sample_sheet = SampleSheet(os.path.dirname(
#         os.path.abspath(__file__)) + "/sample-1")

#     ## Mock for valid Input
#     mocker.patch("samplesheet.Sample", result_value=None )
#     mocker.patch.object(Sample, 'set_metadata_row_for_sample', result_value="set_metadata_row_for_sample function executed" )

#     result_func = check_metadata_correspondence(sample_sheet,"JWT-TOKEN")

#     assert result_func == None, "No Error is executed"

def test_check_sample_sheet_for_index_clashes(mocker):
    # Mock sample value
    sample_sheet = SampleSheet(os.path.dirname(
        os.path.abspath(__file__)) + "/sample-1")

    # No Error for expected
    mocker.patch('samplesheet.compare_two_indexes', result_value="")
    result_func = check_sample_sheet_for_index_clashes(sample_sheet)
    assert result_func == None, "No Error is executed"

    mocker.patch('samplesheet.compare_two_indexes', side_effect=SimilarIndexError)
    with pytest.raises(SimilarIndexError):
        check_sample_sheet_for_index_clashes(sample_sheet)

# def test_check_internal_override_cycles():
# def test_check_global_override_cycles():
# def test_compare_two_indexes():
# def test_get_grouped_samplesheets():