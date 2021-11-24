#!/usr/bin/env python3

# Logger
from umccr_utils.logger import set_logger, set_basic_logger
# Get functions
from umccr_utils.samplesheet import get_years_from_samplesheet
# Checks
from umccr_utils.samplesheet import check_sample_sheet_for_index_clashes,\
                                    check_metadata_correspondence, check_samplesheet_header_metadata, \
                                    check_global_override_cycles, check_internal_override_cycles
# Sets
from umccr_utils.samplesheet import set_meta_data_by_library_id
# Errors
from umccr_utils.errors import GetMetaDataError, SampleSheetHeaderError, SimilarIndexError, \
                               SampleNameFormatError, MetaDataError, OverrideCyclesError

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

def run_check(sample_sheet, auth_header):
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

    logger.info("Read samplesheet as object")

    # Run some consistency checks
    logger.info("Get all years of samples in samplesheets")
    years = get_years_from_samplesheet(sample_sheet)
    if len(list(years)) == 1:
        logger.info("Samplesheet contains IDs from year: {}".format(list(years)[0]))
    else:
        logger.info("Samplesheet contains IDs from {} years: {}".format(len(years), ', '.join(map(str, list(years)))))

    # Run through checks
    try:
        check_samplesheet_header_metadata(sample_sheet)
        check_sample_sheet_for_index_clashes(sample_sheet)
        set_meta_data_by_library_id(sample_sheet, auth_header=auth_header)
        check_metadata_correspondence(sample_sheet,auth_header=auth_header)
        check_global_override_cycles(sample_sheet)
        check_internal_override_cycles(sample_sheet)
    except SampleSheetHeaderError:
        logger.error("Samplesheet header did not have the appropriate attributes")
        return ("Samplesheet header did not have the appropriate attributes")
    except SampleNameFormatError:
        logger.error("Sample name was not appropriate.")
        return ("Sample name was not appropriate.")
    except SimilarIndexError:
        logger.error("Found at least two indexes that were too similar to each other")
        return ("Found at least two indexes that were too similar to each other")
    except MetaDataError:
        logger.error("Metadata could not be extracted")
        return ("Metadata could not be extracted")
    except OverrideCyclesError:
        logger.error("Override cycles check failed")
        return ("Override cycles check failed")
    except GetMetaDataError:
        logger.error("Unable to get metadata")
        return ("Unable to get metadata")

    # # Split and write individual SampleSheets, based on indexes and technology (10X)
    # if args.check_only:
    #     logger.info("All done.")
    #     return

    # # Sort samples based on override cycles
    # # Also replace N indexes with ""
    # sorted_samplesheets = get_grouped_samplesheets(sample_sheet)

    # # Now that the samples have been sorted, we can write one or more custom sample sheets
    # # (which may be the same as the original if no processing was necessary)
    # logger.info(f"Writing {len(sorted_samplesheets)} sample sheets.")

    # # Iterate through sample sheets
    # for override_cycles, samplesheet in sorted_samplesheets.items():
    #     override_cycles_str = override_cycles.replace(";", "_")
    #     out_file = args.outdir / "SampleSheet.{}.csv".format(override_cycles_str)
    #     with open(out_file, "w") as samplesheet_h:
    #         samplesheet.write(samplesheet_h)

