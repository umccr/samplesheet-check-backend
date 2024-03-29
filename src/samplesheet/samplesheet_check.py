#!/usr/bin/env python3
from utils.logger import set_logger, set_basic_logger
from utils.samplesheet import get_years_from_samplesheet, check_sample_sheet_for_index_clashes, \
    check_metadata_correspondence, check_samplesheet_header_metadata, \
    check_global_override_cycles, check_internal_override_cycles,  set_metadata_by_library_id
from utils.errors import GetMetaDataError, SampleSheetHeaderError, SimilarIndexError, \
    SampleNameFormatError, MetaDataError, OverrideCyclesError
import pandas as pd

# Logger
logger = set_basic_logger()


def construct_logger(log_path, log_level):
    """
    Cosntructing logger for samplesheet.

    Parameters
    ----------
    log_path : str
        The path where the logger lives
    log_level : str
        The type of logging desired

    """
    global logger
    set_logger(log_path=log_path, log_level=log_level)


async def run_sample_sheet_content_check(sample_sheet):
    """
    Run check for the samplesheet.

    Parameters
    ----------
    sample_sheet : SampleSheet
        sample sheet data to be checked

    Return
    ----------
    error_message : str
        any error message that stops the check

    """
    logger.info("Check samplesheet content")

    # Run some consistency checks
    logger.info("Get all years of samples in samplesheets")
    years = get_years_from_samplesheet(sample_sheet)
    if len(list(years)) == 1:
        logger.info("Samplesheet contains IDs from year: {}".format(list(years)[0]))
    else:
        logger.info("Samplesheet contains IDs from {} years: {}".format(len(years), ', '.join(map(str, list(years)))))

    try:
        logger.info('----------check_samplesheet_header_metadata----------')
        check_samplesheet_header_metadata(sample_sheet)
        logger.info('----------check_sample_sheet_for_index_clashes----------')
        check_sample_sheet_for_index_clashes(sample_sheet)
    except SampleSheetHeaderError:
        logger.error("Samplesheet header did not have the appropriate attributes")
        return "Samplesheet header did not have the appropriate attributes"
    except SimilarIndexError:
        logger.error("Found at least two indexes that were too similar to each other")
        return "Found at least two indexes that were too similar to each other"
    except Exception as e:
        logger.error(f"Unknown samplesheet error. Error: {e}")
        return f"Unknown samplesheet error. Error: {e}"


def run_sample_sheet_check_with_metadata(sample_sheet):
    """
    Run check for the samplesheet.

    Parameters
    ----------
    sample_sheet : SampleSheet
        sample sheet data to be checked
    auth_header : str
        JWT token to fetch on data-portal API

    Return
    ----------
    error_message : str
        any error message that stops the check

    """

    logger.info("Check Samplesheet against metadata")

    # Run through checks with metadata integrate
    try:
        logger.info('----------set_metadata_by_library_id----------')
        set_metadata_by_library_id(sample_sheet)
        logger.info('----------check_metadata_correspondence----------')
        check_metadata_correspondence(sample_sheet)
        logger.info('----------check_global_override_cycles----------')
        _ = check_global_override_cycles(sample_sheet)
        logger.info('----------check_internal_override_cycles----------')
        check_internal_override_cycles(sample_sheet)
        logger.info("Info on the value_counts of the samplesheet (by assay, type and override cycles)")
        sample_sheet_df = pd.DataFrame([{"assay": sample.library_series['assay'],
                                         "type": sample.library_series['type'],
                                         "override_cycles": sample.library_series['override_cycles']}
                                         for sample in sample_sheet])
        logger.info(f"Value Counts:\n{sample_sheet_df.value_counts()}")

    except SampleNameFormatError:
        logger.error("Sample name was not appropriate.")
        return "Sample name was not appropriate."
    except MetaDataError:
        logger.error("Metadata could not be extracted")
        return "Metadata could not be extracted"
    except OverrideCyclesError:
        logger.error("Override cycles check failed")
        return "Override cycles check failed"
    except GetMetaDataError:
        logger.error("Unable to get metadata")
        return "Unable to get metadata"
    except Exception as e:
        logger.error(f"Unknown samplesheet error. Error: {e}")
        return f"Unknown samplesheet error. Error: {e}"
