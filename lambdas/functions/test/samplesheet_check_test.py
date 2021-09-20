# Add umccr_util directory to python path
import sys, os
sys.path.append(os.path.join(sys.path[0],'..'))
sys.path.append(os.path.join(sys.path[0],'..','..'))
sys.path.append(os.path.join(sys.path[0],'..','..', 'layers'))

import sys
from functions.samplesheet_check import run_check

# Import Errors
from umccr_utils.errors import GetMetaDataError, SampleSheetHeaderError, SimilarIndexError, \
                               SampleNameFormatError, MetaDataError, OverrideCyclesError
def test_run_check_no_error(mocker):
  mocker.patch('functions.samplesheet_check.get_years_from_samplesheet', return_value=set((2019,2020,2021)))
  mocker.patch('functions.samplesheet_check.check_samplesheet_header_metadata', return_value="")
  mocker.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes', return_value="")
  mocker.patch('functions.samplesheet_check.set_meta_data_by_library_id', return_value="")
  mocker.patch('functions.samplesheet_check.check_metadata_correspondence', return_value="")
  mocker.patch('functions.samplesheet_check.check_global_override_cycles', return_value="")
  mocker.patch('functions.samplesheet_check.check_internal_override_cycles', return_value="")

  assert run_check("SampleSheetClass","JWT-TOKEN") == None, "Expected with no error return"

def test_run_check_SimilarIndexError(mocker):
  mocker.patch('functions.samplesheet_check.get_years_from_samplesheet', return_value=set((2019,2020,2021)))
  mocker.patch('functions.samplesheet_check.check_samplesheet_header_metadata', return_value="")
  mocker.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes', side_effect=SimilarIndexError)
  mocker.patch('functions.samplesheet_check.set_meta_data_by_library_id', return_value="")
  mocker.patch('functions.samplesheet_check.check_metadata_correspondence', return_value="")
  mocker.patch('functions.samplesheet_check.check_global_override_cycles', return_value="")
  mocker.patch('functions.samplesheet_check.check_internal_override_cycles', return_value="")

  assert run_check("SampleSheetClass","JWT-TOKEN") == "Found at least two indexes that were too similar to each other", "Expected error"

def test_run_check_SampleSheetHeaderError(mocker):
  mocker.patch('functions.samplesheet_check.get_years_from_samplesheet', return_value=set((2019,2020,2021)))
  mocker.patch('functions.samplesheet_check.check_samplesheet_header_metadata', side_effect=SampleSheetHeaderError)
  mocker.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes', return_value="")
  mocker.patch('functions.samplesheet_check.set_meta_data_by_library_id', return_value="")
  mocker.patch('functions.samplesheet_check.check_metadata_correspondence', return_value="")
  mocker.patch('functions.samplesheet_check.check_global_override_cycles', return_value="")
  mocker.patch('functions.samplesheet_check.check_internal_override_cycles', return_value="")

  assert run_check("SampleSheetClass","JWT-TOKEN") == "Samplesheet header did not have the appropriate attributes", "Expected error"
def test_run_check_GetMetaDataError(mocker):
  mocker.patch('functions.samplesheet_check.get_years_from_samplesheet', return_value=set((2019,2020,2021)))
  mocker.patch('functions.samplesheet_check.check_samplesheet_header_metadata', return_value="")
  mocker.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes', return_value="")
  mocker.patch('functions.samplesheet_check.set_meta_data_by_library_id', side_effect=GetMetaDataError)
  mocker.patch('functions.samplesheet_check.check_metadata_correspondence', return_value="")
  mocker.patch('functions.samplesheet_check.check_global_override_cycles', return_value="")
  mocker.patch('functions.samplesheet_check.check_internal_override_cycles', return_value="")

  assert run_check("SampleSheetClass","JWT-TOKEN") == "Unable to get metadata", "Expected error"


def test_run_check_MetaDataError(mocker):
  mocker.patch('functions.samplesheet_check.get_years_from_samplesheet', return_value=set((2019,2020,2021)))
  mocker.patch('functions.samplesheet_check.check_samplesheet_header_metadata', return_value="")
  mocker.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes', return_value="")
  mocker.patch('functions.samplesheet_check.set_meta_data_by_library_id', return_value="")
  mocker.patch('functions.samplesheet_check.check_metadata_correspondence', side_effect=MetaDataError)
  mocker.patch('functions.samplesheet_check.check_global_override_cycles', return_value="")
  mocker.patch('functions.samplesheet_check.check_internal_override_cycles', return_value="")

  assert run_check("SampleSheetClass","JWT-TOKEN") == "Metadata could not be extracted", "Expected error"
def test_run_check_globalOverrideCyclesError(mocker):
  mocker.patch('functions.samplesheet_check.get_years_from_samplesheet', return_value=set((2019,2020,2021)))
  mocker.patch('functions.samplesheet_check.check_samplesheet_header_metadata', return_value="")
  mocker.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes', return_value="")
  mocker.patch('functions.samplesheet_check.set_meta_data_by_library_id', return_value="")
  mocker.patch('functions.samplesheet_check.check_metadata_correspondence', return_value="")
  mocker.patch('functions.samplesheet_check.check_global_override_cycles', side_effect=OverrideCyclesError)
  mocker.patch('functions.samplesheet_check.check_internal_override_cycles', return_value="")

  assert run_check("SampleSheetClass","JWT-TOKEN") == "Override cycles check failed", "Expected error"
def test_run_check_internalOverrideCyclesError(mocker):
  mocker.patch('functions.samplesheet_check.get_years_from_samplesheet', return_value=set((2019,2020,2021)))
  mocker.patch('functions.samplesheet_check.check_samplesheet_header_metadata', return_value="")
  mocker.patch('functions.samplesheet_check.check_sample_sheet_for_index_clashes', return_value="")
  mocker.patch('functions.samplesheet_check.set_meta_data_by_library_id', return_value="")
  mocker.patch('functions.samplesheet_check.check_metadata_correspondence', return_value="")
  mocker.patch('functions.samplesheet_check.check_global_override_cycles', return_value="")
  mocker.patch('functions.samplesheet_check.check_internal_override_cycles', side_effect=OverrideCyclesError)

  assert run_check("SampleSheetClass","JWT-TOKEN") == "Override cycles check failed", "Expected error"