import email
import json
import tempfile
import os
from samplesheetCheck import main

# Response Template
response = {
    "statusCode":500,
    "body": "",
    'headers': {
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
    },
}

def lambda_handler(event, context):

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

    print(multipart_content)
    file_data = multipart_content["file"]
    log_level = multipart_content["logLevel"].decode("utf-8")

    # Check if data input is correct
    if log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] == False:
        response["statusCode"] = 400
        response["body"] = json.dumps({"message":"INVALID LOG LEVEL"})
        return response


    # Place data into temporary location
    temporaryData = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    temporaryData.write(file_data.decode("utf-8"))
    temporaryData.seek(0)   

    # Execute sample checker function
    errorMessage = main(samplesheet_file_path=temporaryData.name, deploy_env="dev", log_level=log_level)
    checkStatus = "FAIL"
    # Get Log Data
    with open('/tmp/samplesheetCheck.dev.log', 'r') as log_file:
        log_text = log_file.read()
        log_bytes_string = log_text

    # Remove the tmp values
    os.remove('/tmp/samplesheetCheck.dev.log')

    # Determine result status
    if errorMessage:
        checkStatus = "FAIL"
    else:
        checkStatus = "PASS"
    
    # Compile body response
    body = {
        "checkStatus": checkStatus,
        "errorMessage": errorMessage,
        "log_file": log_bytes_string
    }

    response["statusCode"] = 200
    response["body"] = json.dumps(body)

    
    return response
