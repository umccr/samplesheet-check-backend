#!/usr/bin/env python3

"""
Pull in library and metadata sheet from google
"""

import pandas as pd
from umccr_utils.globals import METADATA_VALIDATION_COLUMN_NAMES
from umccr_utils.logger import get_logger
from umccr_utils.errors import ColumnNotFoundError


logger = get_logger()

def check_validation_metadata_columns(validation_df):
    """
    Confirm that the validation metadata columns are present
    :param validation_df:
    :return:
    """

    for column_key, column_name in METADATA_VALIDATION_COLUMN_NAMES.items():
        if column_name not in validation_df.columns.tolist():
            logger.error(f"Could not find column {column_name}. "
                         f"The file is not structured as expected! Aborting.")
            raise ColumnNotFoundError
    logger.info(f"Loaded library tracking sheet validation data.")

def read_local_excel_file(local_path):
    """
    Read local excel file and parse through the sheet name as a pandas dataframe
    :param local_path:
    :param sheet_name:
    :return:
    """

    xl = pd.ExcelFile(local_path)

    return xl.parse()

def get_local_validation_metadata(lab_spreadsheet_path):
    """
    Get the local validation columns
    :param lab_spreadsheet_path:
    :return:
    """

    # Import from gsuite
    validation_df = read_local_excel_file(lab_spreadsheet_path)

    # Check validation columns
    check_validation_metadata_columns(validation_df)

    return validation_df
