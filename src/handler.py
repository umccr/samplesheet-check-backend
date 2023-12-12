import email
import json
import tempfile
import os
import logging
import asyncio

from samplesheet.samplesheet_check import run_sample_sheet_content_check, run_sample_sheet_check_with_metadata, construct_logger

from utils.samplesheet import SampleSheet
from utils.globals import LOG_DIRECTORY
from samplesheet.v2_samplesheet_builder import v1_to_v2_samplesheet

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Parameters
    ----------
    event : Object
        An object of payload pass through the lambda
    context : Object
        [NOT_USED] an aws resource information

    Return
    ----------
    error_message : str
        any error message that stops the check

    """
    logger.info('Processing samplesheet check based on the following event.')
    logger.info(json.dumps(event))

    try:
        origin = event["headers"]["origin"]
    except KeyError:
        origin = ""
    logger.info(f'Parsing origin header content: {origin}')

    auth_header = event["headers"]["Authorization"]
    body = event["body"].encode()

    # Parse contentType
    try:
        content_type = event["headers"]['Content-Type']
    except KeyError:
        content_type = event["headers"]['content-type']
    ct = "Content-Type: " + content_type + "\n"

    msg = email.message_from_bytes(ct.encode() + body)

    multipart_content = {}
    # retrieving form-data
    for part in msg.get_payload():
        # checking if filename exist as a part of content-disposition header
        multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)

    file_data = multipart_content["file"]
    log_level = multipart_content["logLevel"].decode("utf-8")

    # Log Path
    log_path = LOG_DIRECTORY["samplesheet_check"]

    # Check if data input is correct
    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        # Logging
        logger.info(f"Log Level selected is not recognized. '{log_level}' is not an option.")

        # Return response
        body = construct_body(check_status="FAIL", error_message="IncorrectLogLevel", log_path=log_path)
        response = construct_response(status_code=200, body=body, origin=origin)

        logger.info('Returning bad request response')
        return response

    # Place data into temporary location
    logger.info('Creating a logger temporary file')
    temporary_data = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    temporary_data.write(file_data.decode("utf-8"))
    temporary_data.seek(0)

    # Setup Logging
    logger.info(f"Constructing logger file at '{log_path}' with log Level of '{log_level}'")
    construct_logger(log_path=log_path, log_level=log_level)

    # Create SampleSheet
    try:
        sample_sheet = SampleSheet(temporary_data.name)
    except:
        body = construct_body(check_status="FAIL", error_message="FileContentError", log_path=log_path)
        response = construct_response(status_code=200, body=body, origin=origin)
        return response

    # Run some checks
    try:

        # Make async calls between get_metadata and samplesheet function
        loop = asyncio.new_event_loop()

        error = loop.run_until_complete(
            metadata_call_and_samplesheet_content_check(sample_sheet=sample_sheet, auth_header=auth_header))
        loop.close()

        # sample_sheet.set_metadata_df_from_api(auth_header)
        # Check just from samplesheet data
        # error = run_sample_sheet_content_check(sample_sheet)
        if error:
            raise ValueError(error)

        # Check sample_sheet with metadata
        error = run_sample_sheet_check_with_metadata(sample_sheet)
        if error:
            raise ValueError(error)

    except Exception as e:
        body = construct_body(check_status="FAIL", error_message=str(e), log_path=log_path)
        response = construct_response(status_code=200, body=body, origin=origin)
        return response

    # Check v2 samplesheet
    v2_samplesheet_str = v1_to_v2_samplesheet(sample_sheet)

    # Construct Response
    body = construct_body(check_status='PASS', log_path=log_path, v2_samplesheet_str=v2_samplesheet_str)
    response = construct_response(status_code=200, body=body, origin=origin)

    logger.info('Check completed, return a valid response')
    return response


async def metadata_call_and_samplesheet_content_check(sample_sheet, auth_header):
    loop = asyncio.get_running_loop()

    _, error = await asyncio.gather(
        sample_sheet.set_metadata_df_from_api(auth_header, loop),
        run_sample_sheet_content_check(sample_sheet)

    )
    return error


def construct_body(check_status='', error_message='', log_path='', v2_samplesheet_str=''):
    """
    Parameters
    ----------
    check_status : One of 'PASS' or 'FAIL'

    error_message : The error message to return

    log_path: The directory containing the logs

    v2_samplesheet_str : The string representation of the v2 samplesheet

    Return
    ----------
    error_message : str
        any error message that stops the check
    """

    # Get Log Data
    with open(log_path, 'r') as log_file:
        log_text = log_file.read()

    # Remove the tmp values
    os.remove(log_path)
    body = {
        "check_status": check_status,
        "error_message": error_message,
        "log_file": log_text,
        "v2_samplesheet_str": v2_samplesheet_str
    }
    return json.dumps(body)


def construct_response(status_code, body, origin):
    """Construct response from parameter"""

    # Configuration of allowed origin
    allowed_origin_list = ['https://sscheck.umccr.org', 'https://sscheck.dev.umccr.org',
                           'https://sscheck.prod.umccr.org']

    if origin in allowed_origin_list:
        return_origin = origin
    else:
        return_origin = allowed_origin_list[0]

    response = {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': return_origin,
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
        'body': body
    }

    return response
