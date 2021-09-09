import email
import json
import tempfile
import os

from samplesheet_check import run_check, construct_logger, SampleSheet

from umccr_utils.globals import LOG_DIRECTORY


def construct_body(check_status, error_message, log_path):
    """Construct body from from information"""

    # Get Log Data
    with open(log_path, 'r') as log_file:
        log_text = log_file.read()

    # Remove the tmp values
    os.remove(log_path)
    body = {
        "checkStatus": check_status,
        "errorMessage": error_message,
        "log_file": log_text
    }
    return json.dumps(body)

def construct_response(status_code, body):
    """Construct response from parameter"""
    response = {}
    response["headers"] = {
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': [ 'https://sscheck.dev.umccr.org', 'https://sscheck.prod.umccr.org', 'https://sscheck.umccr.org' ],
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
    }

    response["body"] = body
    response["status_code"] = status_code

    return json.dumps(response)


def lambda_handler(event, context):

    auth_header = event["headers"]["Authorization"]

    body = event["body"].encode()

    # Parse contentType
    try:
        content_type = event["headers"]['Content-Type']
    except:
        content_type = event["headers"]['content-type']
    ct = "Content-Type: "+content_type+"\n"

    msg = email.message_from_bytes(ct.encode()+body)    

    multipart_content = {}
    # retrieving form-data
    for part in msg.get_payload():
        # checking if filename exist as a part of content-disposition header
        if part.get_filename():
            # fetching the filename
            file_name = part.get_filename()
        multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)

    file_data = multipart_content["file"]
    log_level = multipart_content["logLevel"].decode("utf-8")

    # Check if data input is correct
    if log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] == False:
        body = construct_body(check_status="FAIL", error_message="IncorrectLogLevel")
        response = construct_response(status_code=400, body=body)
        return response

    # Place data into temporary location
    temporaryData = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    temporaryData.write(file_data.decode("utf-8"))
    temporaryData.seek(0)   

    # Log Path 
    log_path = LOG_DIRECTORY["samplesheet_check"]

    # Setup Logging
    construct_logger(log_path=log_path, log_level=log_level)

    # Create SampleSheet 
    try:
        sample_sheet = SampleSheet(temporaryData.name)
    except:
        body = construct_body(check_status="FAIL", error_message="FileContentError", log_path=log_path)
        response = construct_response(status_code=400, body=body)
        return response

    
    # Execute sample checker function
    errorMessage = run_check(sample_sheet, auth_header=auth_header)


    # Check status 
    if errorMessage:
        check_status="FAIL"
    else:
        check_status="PASS"

    # Construct Response
    body = construct_body(check_status=check_status, error_message=errorMessage, log_path=log_path)
    response = construct_response(status_code=200, body=body)

    return response

