#!/usr/bin/env python3
import sys
import os
import argparse
import collections
from pathlib import Path

# Globals
from umccr_utils.globals import LAB_SPREAD_SHEET_ID
# Logger
from umccr_utils.logger import set_logger, set_basic_logger, get_logger
# Get Classes
from umccr_utils.samplesheet import SampleSheet
# Get functions
from umccr_utils.samplesheet import get_years_from_samplesheet, get_grouped_samplesheets
# Checks
from umccr_utils.samplesheet import check_sample_sheet_for_index_clashes,\
                                    check_metadata_correspondence, check_samplesheet_header_metadata, \
                                    check_global_override_cycles, check_internal_override_cycles
# Sets
from umccr_utils.samplesheet import set_meta_data_by_library_id
# Errors
from umccr_utils.errors import SampleSheetHeaderError, SimilarIndexError, \
                               SampleNameFormatError, MetaDataError, OverrideCyclesError

# Relative paths
SCRIPT = Path(__file__)
SCRIPT_DIR = Path("/tmp")
SCRIPT_STEM = SCRIPT.stem
logger = set_basic_logger()


def get_args(samplesheet_file_path, deploy_env, log_level):
    """
    Get args for the workflow
    :return:
    """
    logger.debug("Get args")
    parser = argparse.ArgumentParser(description='Check samplesheet is configured correctly')
    parser.add_argument('samplesheet',
                        help="The samplesheet to process.")
    parser.add_argument('--check-only', action='store_true',
                        help="Only run the checks, do not split the samplesheet.")
    parser.add_argument('--deploy-env',
                        required=False,
                        default=None,
                        choices=["dev", "prod"],
                        help="Which deploy env are we using. Can also be set with DEPLOY_ENV")
    parser.add_argument("--outdir",
                        required=False,
                        help="Output directory for new samplesheets to be placed. Defaults to $PWD")
    parser.add_argument("--log-level",
                        required=False,
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        default="DEBUG")
    return parser.parse_args(['--check-only', samplesheet_file_path, '--deploy-env', deploy_env,
        '--log-level', log_level])


def check_args(args):
    """
    Check args are all-g
    :return:
    """

    global logger

    # Check deploy-env
    deploy_env_arg = getattr(args, "deploy_env", None)
    if deploy_env_arg is None:
        logger.debug("Could not find --deploy-env, taking DEPLOY_ENV from environment")
        deploy_env = os.environ["DEPLOY_ENV"]
        if deploy_env is None:
            logger.error("--deploy-env not specified and DEPLOY_ENV env var is also not specified")
            sys.exit(1)
        elif deploy_env not in list(LAB_SPREAD_SHEET_ID.keys()):
            logger.error("Found {} from 'DEPLOY_ENV' env var but {} is not in {}".format(
                deploy_env, deploy_env, ', '
            ))
        else:
            setattr(args, "deploy_env", deploy_env)

    set_logger(SCRIPT_DIR, SCRIPT_STEM, getattr(args, "deploy_env"), log_level=args.log_level)

    logger = get_logger()

    # Get path to samplesheet
    samplesheet_arg = getattr(args, "samplesheet")

    # Convert to path-like object
    samplesheet_path = Path(samplesheet_arg)

    # Check file exists
    if not samplesheet_path.is_file():
        logger.error("Samplesheet path at {} does not exist".format(samplesheet_path))
        sys.exit(1)

    # Set samplesheet_path to attribute
    setattr(args, "samplesheet", samplesheet_path)

    # Check output-dir
    outdir_arg = getattr(args, "outdir", None)
    if outdir_arg is not None:
        # Convert to path object
        outdir_path = Path(outdir_arg)
        # Ensure '--check-only' isn't also set
        if getattr(args, "check_only", False):
            logger.error("--outdir and --check-only are mutually exclusive arguments")
            sys.exit(1)
        # Create directory if it doesn't exist
        if not outdir_path.parent.is_dir():
            logger.error("Parent directory of --outdir parameter does not exist. Please create before continuing")
            sys.exit(1)
        if not outdir_path.is_dir():
            logger.debug("Creating directory {}".format(outdir_path))
            outdir_path.mkdir()
    else:
        # Assign to pwd
        outdir_path = Path(os.getcwd())
    # Assign value to args
    setattr(args, "outdir", outdir_path)

    # Check log level
    log_level_arg = getattr(args, "log_level", None)

    # Setting log level
    if log_level_arg is not None:
        logger.setLevel(log_level_arg)

    return args


def run_check(samplesheet_file_path, deploy_env, log_level, auth_header):

    # Grab args configuration
    args = get_args(samplesheet_file_path, deploy_env, log_level)

    logger.info("Checking args")
    args = check_args(args)

    logger.info("Read samplesheet as object")
    sample_sheet = SampleSheet(samplesheet_path=args.samplesheet)

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

    # Split and write individual SampleSheets, based on indexes and technology (10X)
    if args.check_only:
        logger.info("All done.")
        return

    # Sort samples based on override cycles
    # Also replace N indexes with ""
    sorted_samplesheets = get_grouped_samplesheets(sample_sheet)

    # Now that the samples have been sorted, we can write one or more custom sample sheets
    # (which may be the same as the original if no processing was necessary)
    logger.info(f"Writing {len(sorted_samplesheets)} sample sheets.")

    # Iterate through sample sheets
    for override_cycles, samplesheet in sorted_samplesheets.items():
        override_cycles_str = override_cycles.replace(";", "_")
        out_file = args.outdir / "SampleSheet.{}.csv".format(override_cycles_str)
        with open(out_file, "w") as samplesheet_h:
            samplesheet.write(samplesheet_h)
