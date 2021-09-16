# Add umccr_util directory to python path
import sys, os
sys.path.append(os.path.join(sys.path[0],'..'))
sys.path.append(os.path.join(sys.path[0],'..','..'))
sys.path.append(os.path.join(sys.path[0],'..','..', 'layers'))

from unittest import TestCase, mock, main
from functions.samplesheet_check import run_check

# Import Errors
from umccr_utils.errors import GetMetaDataError, SampleSheetHeaderError, SimilarIndexError, \
                               SampleNameFormatError, MetaDataError, OverrideCyclesError


class TestSamplesheetCheckUnitTestCase(TestCase):

  @mock.patch('functions.samplesheet_check.get_years_from_samplesheet',  mock.MagicMock(return_value=set((2019,2020,2021))))
  @mock.patch('functions.samplesheet_check.check_samplesheet_header_metadata',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.set_meta_data_by_library_id',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_metadata_correspondence',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_global_override_cycles',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_internal_override_cycles',  mock.MagicMock(return_value=""))
  def test_run_check_no_error(self):
    assert run_check("SampleSheetClass","JWT-TOKEN") == None, "Expected with no error return"

  @mock.patch('functions.samplesheet_check.get_years_from_samplesheet',  mock.MagicMock(return_value=set((2019,2020,2021))))
  @mock.patch('functions.samplesheet_check.check_samplesheet_header_metadata',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes',  mock.MagicMock(side_effect=SimilarIndexError))
  @mock.patch('functions.samplesheet_check.set_meta_data_by_library_id',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_metadata_correspondence',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_global_override_cycles',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_internal_override_cycles',  mock.MagicMock(return_value=""))
  def test_run_check_SimilarIndexError(self):
    assert run_check("SampleSheetClass","JWT-TOKEN") == "Found at least two indexes that were too similar to each other", "Expected error"

  @mock.patch('functions.samplesheet_check.get_years_from_samplesheet',  mock.MagicMock(return_value=set((2019,2020,2021))))
  @mock.patch('functions.samplesheet_check.check_samplesheet_header_metadata',  mock.MagicMock(side_effect=SampleSheetHeaderError))
  @mock.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.set_meta_data_by_library_id',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_metadata_correspondence',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_global_override_cycles',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_internal_override_cycles',  mock.MagicMock(return_value=""))
  def test_run_check_SampleSheetHeaderError(self):
    assert run_check("SampleSheetClass","JWT-TOKEN") == "Samplesheet header did not have the appropriate attributes", "Expected error"
  
  @mock.patch('functions.samplesheet_check.get_years_from_samplesheet',  mock.MagicMock(return_value=set((2019,2020,2021))))
  @mock.patch('functions.samplesheet_check.check_samplesheet_header_metadata',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.set_meta_data_by_library_id',  mock.MagicMock(side_effect=GetMetaDataError))
  @mock.patch('functions.samplesheet_check.check_metadata_correspondence',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_global_override_cycles',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_internal_override_cycles',  mock.MagicMock(return_value=""))
  def test_run_check_GetMetaDataError(self):

    assert run_check("SampleSheetClass","JWT-TOKEN") == "Unable to get metadata", "Expected error"

  @mock.patch('functions.samplesheet_check.get_years_from_samplesheet',  mock.MagicMock(return_value=set((2019,2020,2021))))
  @mock.patch('functions.samplesheet_check.check_samplesheet_header_metadata',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.set_meta_data_by_library_id',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_metadata_correspondence',  mock.MagicMock(side_effect=MetaDataError))
  @mock.patch('functions.samplesheet_check.check_global_override_cycles',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_internal_override_cycles',  mock.MagicMock(return_value=""))
  def test_run_check_MetaDataError(self):

    assert run_check("SampleSheetClass","JWT-TOKEN") == "Metadata could not be extracted", "Expected error"
  
  @mock.patch('functions.samplesheet_check.get_years_from_samplesheet',  mock.MagicMock(return_value=set((2019,2020,2021))))
  @mock.patch('functions.samplesheet_check.check_samplesheet_header_metadata',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.set_meta_data_by_library_id',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_metadata_correspondence',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_global_override_cycles',  mock.MagicMock(side_effect=OverrideCyclesError))
  @mock.patch('functions.samplesheet_check.check_internal_override_cycles',  mock.MagicMock(return_value=""))
  def test_run_check_globalOverrideCyclesError(self):

    assert run_check("SampleSheetClass","JWT-TOKEN") == "Override cycles check failed", "Expected error"
  
  @mock.patch('functions.samplesheet_check.get_years_from_samplesheet',  mock.MagicMock(return_value=set((2019,2020,2021))))
  @mock.patch('functions.samplesheet_check.check_samplesheet_header_metadata',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.set_meta_data_by_library_id',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_metadata_correspondence',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_global_override_cycles',  mock.MagicMock(return_value=""))
  @mock.patch('functions.samplesheet_check.check_internal_override_cycles',  mock.MagicMock(side_effect=OverrideCyclesError))
  def test_run_check_internalOverrideCyclesError(self):

    assert run_check("SampleSheetClass","JWT-TOKEN") == "Override cycles check failed", "Expected error"

if __name__ == '__main__':
    main()
